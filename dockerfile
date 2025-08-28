FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# 4) Useful env defaults
#   - PYTHONUNBUFFERED: immediate log flush (shows up live in Cloud Run logs)
#   - PLAYWRIGHT_BROWSERS_PATH: browsers already baked into this base image
#   - PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: don’t waste time re-downloading
ENV PYTHONUNBUFFERED=1 
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Set entrypoint to run the Safeway pipeline
CMD ["python", "-m", "grocery_god"]