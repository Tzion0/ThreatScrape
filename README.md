# ThreatScrape
**An Automated Google Dorking Tool for APT & Threat Reports**

## Overview
ThreatScrape is a Python-based **Google Custom Search & Threat Intelligence Scraper** that leverages:
- **Google Custom Search API** to fetch relevant **APT/Malware/Threat reports**
- **Gemini AI** to enhance search queries with related **APT aliases & threat actor names**
- **Google Dorking techniques** for more accurate search results

The tool automatically excludes **common news sites** and refines results based on customizable **Google Dorking parameters**.

---

## Installation
### 1. Install Dependencies
Ensure you have Python 3 installed, then install required libraries:

```bash
# Option 1
pip install requests argparse logging json
# Option 2
pip install -r requirements.txt --br
```

### 2. Get API Keys
You need the following API keys:

- **Google Custom Search API Key** 👉 [Get it here](https://developers.google.com/custom-search/v1/introduction#identify_your_application_to_google_with_api_key)
- **Google Custom Search Engine ID (CX)** 👉 [Get it here](https://cse.google.com/all)
- **Google Gemini AI API Key** 👉 [Get it here](https://aistudio.google.com/apikey)

---

## Configuration

Edit the **`config.json`** file in the same directory and add your API keys & settings:

```json
{
    "GOOGLE_API_KEY": "YOUR_GOOGLE_CUSTOM_SEARCH_API_KEY",
    "CX": "YOUR_CUSTOM_SEARCH_ENGINE_ID",
    "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY",
    "TOTAL_RESULTS": 50,
    "INTEXT_KEYWORDS": [
        "TTP",
        "APT",
        "Malware",
        "Cyber"
    ],
    "EXCLUDED_SITES": [
        "bleepingcomputer.com",
        "thehackernews.com",
        "krebsonsecurity.com",
        "securityweek.com",
        "zdnet.com",
        "wired.com",
        "huggingface.co"
    ]
}
```

**Key Configurations:**
- `TOTAL_RESULTS`: Default is **50**, can be modified.
- `EXCLUDED_SITES`: Domains to exclude from results (can be customized).
- `INTEXT_KEYWORDS`: Additional Google Dorking keywords.

---

## Usage

Run the script via the command line:

```bash
python threatscrape.py "APT32"
```

or specify a different **config file**:

```bash
python threatscrape.py "Ocean Lotus" --config custom_config.json
```

### Example Queries:
```bash
python threatscrape.py "APT28"
python threatscrape.py "Lazarus Group"
python threatscrape.py "FIN7"
```

## License
This project is released under **MIT License**.

