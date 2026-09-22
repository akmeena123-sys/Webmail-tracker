# WEBMAIL TRACKER Dashboard

This project creates a local dashboard from the public Google Sheet:
https://docs.google.com/spreadsheets/d/1AOD6mSBcrS63NnWctlQhvtAAgqQ23sYjSYkNVKOBlrs/edit?gid=0#gid=0

## What it does
- Pulls the Google Sheet CSV every day at 11:00 AM and 5:00 PM
- Saves the latest data in `data/latest.json`
- Shows a dashboard with:
  - pending count
  - red flag count for cases older than 7 days
  - filter by official
  - bar charts
  - table of pending mails

## Files in this project
- `dashboard.html` - the main dashboard page
- `scraper.py` - fetches data from the Google Sheet and prepares JSON
- `scheduler.py` - runs the scraper at the scheduled times automatically
- `server.py` - serves the dashboard locally in the browser

## Easiest way to start the dashboard
1. In this folder, double-click:
   `start_dashboard.bat`
2. Your browser will open automatically.
3. Visit:
   `http://localhost:8000`

## How to stop it
1. Double-click:
   `stop_dashboard.bat`

## Automatic daily refresh
The scheduler runs automatically at 11:00 AM and 5:00 PM.
To start it, double-click:
`start_scheduler.bat`

## Notes
- This is a local dashboard for your computer.
- The dashboard reads the latest saved JSON file, not the Google Sheet directly in the browser.
- If the Google Sheet is changed, the next scheduled run updates the local dashboard automatically.
