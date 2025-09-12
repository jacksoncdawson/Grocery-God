# Grocery God

## Overview
Grocery God is a tool designed to streamline grocery shopping by collecting, processing, and analyzing data from various stores. The project consists of multiple components working together to provide valuable insights for grocery shopping decisions.

## Key Components

### Price Logger
- **Web Interface**: Built with Streamlit for logging grocery purchases
- **Features**:
  - Store selection (Trader Joe's, Safeway, Costco)
  - Trip date tracking
  - Product details logging (name, brand, price, sale status, quantity)
  - Trip summary view with detailed purchase information
- **Data Storage**: All logged purchases are stored in a Supabase relational database for analysis

### Data Collection Pipeline
- **Safeway Scraper**: 
  - Utilizes Playwright to automatically extract weekly ad data from Safeway
  - Captures product details and valid date ranges
  - Exports raw data to CSV format
  - Implemented with retry logic and error handling for reliability

### Data Processing
- **Parsing & Cleaning**:
  - Processes raw scraper data using Pandas
  - Extracts structured product information, deals, and pricing
  - Handles various price formats and deal types
  - Calculates unit prices for better comparison
- **Database Integration**:
  - Uploads cleaned data to Supabase tables
  - Maintains separate tables for flyers and products

### Containerization & AWS Deployment
- **Docker Implementation**:
  - Uses `mcr.microsoft.com/playwright/python:v1.54.0-jammy` as base image
  - Configures Playwright for headless browser operation
  - Includes AWS Lambda runtime interface client
- **AWS Lambda Deployment**:
  - Packaged as a serverless function for scheduled execution
  - Outputs saved to S3 buckets for storage
  - Deployment managed via ECR (Elastic Container Registry)
- **Local Development**:
  - Supports local testing via docker-compose
  - Includes separate profiles for local and remote builds

### Infrastructure
- **CI/CD Tools**:
  - `docker_setup.sh` script for building and pushing to ECR
  - Platform-specific builds for Lambda compatibility (linux/amd64)
- **Environment Management**:
  - Supports multiple environment configurations (.env, .env.local)
  - AWS credentials and region configuration

## Technologies Used
- **Frontend**: Streamlit
- **Backend**: Python, Playwright, Pandas
- **Database**: PostgreSQL (via Supabase)
- **Cloud**: AWS (Lambda, ECR, S3, EventBridge)
- **Containerization**: Docker, Docker Compose

## Future Plans
- **Data Insights**: Provide shopping recommendations based on price analysis
- **Additional Scrapers**: Expand to other grocery store chains
- **Dashboard**: Create visual analytics using Tableau or similar tools