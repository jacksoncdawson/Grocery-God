# 1) Base Python
FROM python:3.11-slim

# 2) OS deps + Google Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates unzip fonts-liberation libnss3 libu2f-udev \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libatk1.0-0 \
    libasound2 libpangocairo-1.0-0 libgtk-3-0 \
 && rm -rf /var/lib/apt/lists/*

# chrome repo + install
RUN mkdir -p /usr/share/keyrings \
 && wget -qO- https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor -o /usr/share/keyrings/google-linux.gpg \
 && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux.gpg] \
    http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
 && apt-get update && apt-get install -y --no-install-recommends google-chrome-stable \
 && rm -rf /var/lib/apt/lists/*

# 3) chromedriver that matches Chrome major version
RUN CHROME_MAJOR=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) \
 && LATEST=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR}") \
 && wget -q "https://chromedriver.storage.googleapis.com/${LATEST}/chromedriver_linux64.zip" -O /tmp/chromedriver.zip \
 && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
 && rm /tmp/chromedriver.zip \
 && chmod +x /usr/local/bin/chromedriver

# 4) Workdir + copy
WORKDIR /app
COPY . /app

# 5) Python deps
RUN pip install --no-cache-dir -r requirements.txt

# 6) Environment defaults for headless Chrome (selenium)
ENV PYTHONUNBUFFERED=1 \
    CHROME_BIN=/usr/bin/google-chrome \
    CHROMEDRIVER=/usr/local/bin/chromedriver

# 7) Run your package entrypoint
CMD ["python", "-m", "grocery_god"]