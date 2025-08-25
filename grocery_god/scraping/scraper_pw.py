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


def _strip_ordinals(s: str) -> str:
    return re.sub(r"(\d{1,2})(st|nd|rd|th)", r"\1", s)


def _parse_dates(date_text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Accepts strings like 'Jan 3rd - Jan 9th' and returns ('YYYY-MM-DD','YYYY-MM-DD').
    """

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
    page: Page, timeout_ms: int = 40_000
) -> Tuple[Optional[str], Optional[str]]:

    # 1) Wait for the iframe element to exist (not necessarily “visible”)
    iframe_locator = page.locator('iframe[title="Navigation Bar"]')
    iframe_locator.wait_for(state="attached", timeout=timeout_ms)

    # 2) Get its content frame explicitly (avoids weirdness with frame_locator and visibility)
    handle = iframe_locator.element_handle()
    frame = handle.content_frame()
    if frame is None:
        raise PlaywrightTimeoutError("Navigation Bar iframe has no content frame yet.")

    locator = frame.get_by_text(DATE_RX).first
    locator.wait_for(state="attached", timeout=timeout_ms)

    date_text = locator.text_content() or ""
    valid_from, valid_until = _parse_dates(date_text)
    return valid_from, valid_until


def scrape_safeway(retries: int = 3) -> Tuple[List[str], Optional[str], Optional[str]]:
    """
    Scrape the Safeway Weekly Ad using Playwright.
    Returns: (all_products, valid_from_iso, valid_until_iso)
    """
    attempt = 0
    backoff = 5

    while attempt < retries:
        try:
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
                page = context.new_page()
                page.set_default_timeout(30_000)

                page.goto(
                    "https://www.safeway.com/weeklyad/", wait_until="domcontentloaded"
                )

                # ---- Dates (Navigation Bar iframe) ----
                try:
                    valid_from, valid_until = _extract_dates_from_nav_iframe(page)
                    if not valid_from or not valid_until:
                        raise PlaywrightTimeoutError(
                            "Could not parse dates from nav iframe"
                        )
                except PlaywrightTimeoutError as e:
                    logging.error(
                        "Timeout extracting date info (attempt %s): %s", attempt + 1, e
                    )
                    attempt += 1
                    time.sleep(backoff)
                    continue

                # ---- Products (Main Panel iframe) ----
                all_products: List[str] = []
                try:
                    main_frame = page.frame_locator('iframe[title="Main Panel"]')
                    # Wait for at least one flyer node to appear
                    flyers = main_frame.locator("sfml-flyer-image")
                    flyers.first.wait_for(state="visible", timeout=30_000)

                    flyer_count = flyers.count()
                    for i in range(flyer_count):
                        flyer = flyers.nth(i)
                        items = flyer.locator("sfml-flyer-image-a")
                        item_count = items.count()
                        for j in range(item_count):
                            label = items.nth(j).get_attribute("aria-label")
                            if label:
                                all_products.append(label)

                except PlaywrightTimeoutError as e:
                    logging.error(
                        "Timeout getting product info (attempt %s): %s", attempt + 1, e
                    )
                    attempt += 1
                    time.sleep(backoff)
                    continue
                finally:
                    context.close()
                    browser.close()

                return all_products, valid_from, valid_until

        except Exception as e:
            logging.exception("Scraper attempt %s failed: %s", attempt + 1, e)
            attempt += 1
            time.sleep(backoff)

    # All retries failed
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
