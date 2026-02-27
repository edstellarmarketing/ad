# AdRoll Creative Studio — Edstellar

A Streamlit app to generate, customize, and download AdRoll retargeting ad creatives for corporate training campaigns.

## Features

- **9 Ad Formats**: 300×250 (3 variants), 728×90 (2), 160×600, 300×600, 320×50 (2)
- **Dual Logo Upload**: Separate logos for dark and light backgrounds
- **AI Prompt**: Describe your ad style and auto-generate content
- **Quick Presets**: Urgency, Social Proof, Benefits, Re-engage, Minimal
- **Live Preview**: All creatives update in real-time
- **PNG Download**: Individual or batch ZIP download
- **Full Customization**: Headlines, CTAs, stats, colors, clients, benefits

## Local Setup

```bash
pip install -r requirements.txt
playwright install chromium
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set:
   - **Main file**: `app.py`
   - **Python version**: 3.11+
5. The `packages.txt` file handles system deps automatically
6. Add this to **Advanced Settings > Secrets** or create a `setup.sh`:
   ```
   playwright install chromium
   ```

## File Structure

```
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── packages.txt        # System packages (for Streamlit Cloud)
├── setup.sh            # Browser install script
└── README.md           # This file
```

## How It Works

1. Each ad is generated as standalone HTML with inline styles
2. Playwright (headless Chromium) renders the HTML to high-res PNG
3. Streamlit serves the preview via `st.components.v1.html()`
4. Downloads use `st.download_button()` with rendered PNG bytes
