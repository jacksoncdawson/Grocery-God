import csv
import os
import re
import logging
import time
from datetime import datetime
from typing import Tuple, List, Optional

from playwright.sync_api import (
    Page,
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

DATE_RX = re.compile(r"([a-zA-Z]+ \d+[a-zA-Z]+) - ([a-zA-Z]+ \d+[a-zA-Z]+)")


def _parse_dates(date_text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Accepts strings like 'Jan 3rd - Jan 9th' and returns ('YYYY-MM-DD','YYYY-MM-DD').
    """

    def _strip_ordinals(s: str) -> str:
        return re.sub(r"(\d{1,2})(st|nd|rd|th)", r"\1", s)

    m = DATE_RX.search(date_text.strip())

    if not m:
        return None, None

    current_year = datetime.now().year
    start_str = f"{_strip_ordinals(m.group(1))} {current_year}"
    end_str = f"{_strip_ordinals(m.group(2))} {current_year}"

    valid_from = datetime.strptime(start_str, "%b %d %Y").strftime("%Y-%m-%d")
    valid_until = datetime.strptime(end_str, "%b %d %Y").strftime("%Y-%m-%d")
    return valid_from, valid_until


def _extract_dates_from_nav_iframe(
    page: Page, timeout_ms: int = 30_000
) -> Tuple[Optional[str], Optional[str]]:

    iframe_locator = page.locator('iframe[title="Navigation Bar"]')
    iframe_locator.wait_for(state="attached", timeout=timeout_ms)

    handle = iframe_locator.element_handle()
    frame = handle.content_frame()
    if frame is None:
        raise PlaywrightTimeoutError("Navigation Bar iframe has no content frame yet.")

    locator = frame.get_by_text(DATE_RX).first
    locator.wait_for(state="attached", timeout=timeout_ms)

    date_text = locator.text_content() or ""
    valid_from, valid_until = _parse_dates(date_text)
    return valid_from, valid_until


def _extract_products_from_main_iframe(
    page: Page, timeout_ms: int = 30_000
) -> List[str]:

    iframe = page.locator('iframe[title="Main Panel"]')
    iframe.wait_for(state="attached", timeout=timeout_ms)
    frame = iframe.element_handle().content_frame()
    if frame is None:
        raise PlaywrightTimeoutError("Main Panel iframe not ready")

    items = frame.locator("sfml-flyer-image-a[aria-label]")
    items.first.wait_for(state="attached", timeout=timeout_ms)

    labels = items.evaluate_all(
        "nodes => nodes.map(n => n.getAttribute('aria-label')).filter(Boolean)"
    )
    return labels


def _scrape() -> Tuple[List[str], Optional[str], Optional[str]]:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1920,1080",
            ],
        )
        context = browser.new_context(viewport={"width": 1920, "height": 1080})

        try:
            page = context.new_page()
            page.set_default_timeout(30_000)
            page.goto(
                "https://www.safeway.com/weeklyad/", wait_until="domcontentloaded"
            )

            valid_from, valid_until = _extract_dates_from_nav_iframe(page)
            products = _extract_products_from_main_iframe(page)
        finally:
            context.close()
            browser.close()

    return products, valid_from, valid_until


def scrape_safeway(
    retries: int = 3, backoff: int = 5
) -> Tuple[List[str], Optional[str], Optional[str]]:
    for attempt in range(1, retries + 1):
        try:
            return _scrape()
        except (PlaywrightTimeoutError, ValueError) as e:
            logging.error("Attempt %s/%s failed: %s", attempt, retries, e)
            if attempt < retries:
                time.sleep(backoff)
            else:
                logging.error("All retries exhausted.")
                break

    return [], None, None


def scrape_to_csv(all_products: List[str], valid_from: str, valid_until: str) -> str:
    """Write CSV locally and return the path."""

    os.makedirs("./data", exist_ok=True)
    filename = f"./data/weeklyad_{valid_from}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([f"{valid_from} - {valid_until}"])
        for product in all_products:
            w.writerow([product])

    return filename
