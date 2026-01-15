# Webcheck Feature Documentation

## Overview
The Webcheck feature is an automated maintenance tool for the Admin interface. It iterates through the database of Tools to verify their website availability, enhance their assets (snapshots, favicons), and improve data quality.

## Features

### 1. URL Validation
- Checks if the `website_url` is accessible (HTTP 200).
- Detects redirects to known domain parking or sales pages.
- Marks tools with invalid URLs as "Incomplete".

### 2. Asset Generation
- **Snapshot**: Captures a screenshot of the website (top 600px) 1 second after loading. This is saved as the Tool's image/media.
- **Icon**: Detects and downloads the website's favicon. Converts `.ico` to `.png` if necessary and saves it as the Tool's logo.

### 3. Relevance Improvement
- **Meta Scraping**: Fetches `meta title` and `meta description` to suggest improvements for the tool's description.
- **Keyword Analysis**: (Future) Analyze content for better tagging.

## User Interface
- **Admin Dashboard**: A new "Webcheck" button initiates the process.
- **Tools List**: An "Incomplete" filter allows admins to quickly identify tools that failed the Webcheck or have missing data.
- **Results View**: A summary page displaying the outcome of the batch check (Successes, Failures, Updates).

## Technical Implementation
- **Back-end**: Python/Django.
- **Browser Automation**: Playwright (or Selenium) for snapshots.
- **Image Processing**: Pillow (PIL).

## Usage
1. Go to Admin Dashboard.
2. Click "Webcheck".
3. Wait for the process to complete.
4. Review the "Summarisation" page.
5. Use the "Incomplete" filter in the Tools list to fix issues.
