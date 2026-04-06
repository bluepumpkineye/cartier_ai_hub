# Cartier APAC Intelligence Hub — Deployment Guide

This guide describes how to deploy the cleaned-up project to **Streamlit Community Cloud**.

## 1. Prepare your Repository
- Ensure all changes (especially `requirements.txt` and `.streamlit/config.toml`) are committed and pushed to your GitHub repository: `bluepumpkineye/cartier_ai_hub`.

## 2. Connect to Streamlit Cloud
1.  Log in to [share.streamlit.io](https://share.streamlit.io).
2.  Click **"New app"**.
3.  Select your repository (`bluepumpkineye/cartier_ai_hub`).
4.  Set the Main file path to: `app.py`.
5.  **Stop! Don't click Deploy yet.**

## 3. Add Environment Secrets
1.  In the deployment screen, click **"Advanced settings..."**.
2.  Paste your **OpenRouter API Key** into the **Secrets** text area using this format:

```toml
OPENROUTER_API_KEY = "your-sk-or-v1-key-here"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
APP_ENV = "production"
APP_NAME = "Cartier APAC Intelligence Hub"
```

3.  Click **"Save"** and then **"Deploy!"**.

## 4. Troubleshooting
- **Build Fails**: If the build logs indicate a memory error while installing `torch`, we can switch to a lighter embedding model or use an API-based embedding (like OpenAI).
- **Data Missing**: The app expects CSV files in `data/`. Ensure these are committed to your repo.
