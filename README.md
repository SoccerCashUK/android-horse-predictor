# Android Horse Predictor

Phone-first horse racing predictor built for GitHub Pages.

## What this version does

- Pulls Sporting Life's `today/download.csv`
- Parses upcoming races into JSON
- Shows a mobile-friendly race list
- Ranks runners by market-implied chance from odds
- Supports manual refresh through GitHub Actions

## Files

- `index.html` - mobile UI
- `styles.css` - styles
- `app.js` - prediction logic and UI rendering
- `scripts/update_races.py` - fetches and parses the CSV source
- `.github/workflows/update-races.yml` - scheduled updater
- `data/upcoming_races.json` - generated race data

## Setup after upload

1. Open repo settings
2. Open Pages
3. Set source to `Deploy from a branch`
4. Choose branch `main`
5. Choose folder `/ (root)`
6. Save

## Running updates

- Automatic: GitHub Actions runs on schedule
- Manual: open `Actions`, choose `Update race data`, then `Run workflow`

## Notes

Version 1 is market-based. It uses current odds as the prediction baseline.
Historical form can be added later.
