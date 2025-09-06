FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

RUN pip install --no-cache-dir awslambdaric

WORKDIR /var/task

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

CMD ["python", "-m", "awslambdaric", "grocery_god.pipelines.safeway_lambda.handler"]