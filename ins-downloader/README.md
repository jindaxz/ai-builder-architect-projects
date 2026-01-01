# Instagram Image Downloader

This is a simple Flask + Instaloader website that downloads the latest Instagram post images for the username entered by a user and bundles them into a zip archive. The project fulfills “📸 Project 2: download images from an Instagram account.”

## Feature Overview

- Enter an Instagram username and the number of posts to fetch (1-50) to trigger a download.
- The server uses Instaloader to grab the newest images from public accounts and returns a zip file once the request finishes.
- Set `INSTAGRAM_USERNAME` / `INSTAGRAM_PASSWORD` environment variables to log in so you can download private-but-accessible content and avoid unauthenticated rate limits.

## How to Run

1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Optional: configure environment variables**
   ```bash
   export INSTAGRAM_USERNAME="your_username"
   export INSTAGRAM_PASSWORD="your_password"
   export FLASK_DEBUG=1  # enable during development if needed
   ```
3. **Start the server**
   ```bash
   python app.py
   ```
4. Open `http://localhost:5000` in your browser, enter an Instagram username, and start the download.

## Important Notes

- Only public accounts (or accounts visible to the provided credentials) can be scraped. Trying to fetch a private account without logging in returns an error.
- Instaloader relies on Instagram’s public web interface. Excessive requests can trigger rate limits; provide credentials or slow down requests if that happens.
- Downloaded files are cleaned up after each request and are not kept on disk.
- This project is for learning and demos only. If you deploy it publicly, follow Instagram’s Terms of Use and protect sensitive data.

## Structure

```
.
├── app.py                # Flask app and download logic
├── requirements.txt      # Python dependencies
├── templates/index.html  # Frontend page
└── static/               # Styles and scripts
```

Feel free to add features such as authentication, progress indicators, or task queues if your delivery requires them.
