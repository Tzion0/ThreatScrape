import requests
import json
import logging
import time
import argparse
import sys
import csv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_config(config_path):
    """Load API credentials and settings from a specified config file."""
    try:
        with open(config_path, "r") as config_file:
            return json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading config file: {e}")
        sys.exit(1)

def get_related_keywords(search_term, gemini_api_key):
    """Query Gemini API for related keywords based on the search term."""
    if not gemini_api_key:
        logging.error("Gemini API key is missing.")
        return [search_term]

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    prompt = f"Provide related APT or threat actor names for: {search_term}. Include alternative names and aliases, separated by commas."

    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(gemini_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "candidates" in data and "parts" in data["candidates"][0]["content"]:
            related_text = data["candidates"][0]["content"]["parts"][0]["text"]
            related_keywords = [term.strip() for term in related_text.split(",") if term]
            logging.info(f"Related keywords found: {related_keywords}")
            return related_keywords
    except requests.exceptions.RequestException as e:
        logging.error(f"Gemini API request failed: {e} Try rerunning the script.")

    return [search_term]

def build_google_dorking_query(base_keyword, config):
    """Construct a Google Dorking query using related keywords and site exclusions."""
    related_keywords = get_related_keywords(base_keyword, config.get("GEMINI_API_KEY"))
    query_terms = " OR ".join(f'"{kw}"' for kw in related_keywords)

    excluded_sites = config.get("EXCLUDED_SITES", [])
    exclusion_query = " ".join(f"-site:{site}" for site in excluded_sites)

    intext_keywords = config.get("INTEXT_KEYWORDS", [])
    intext_query = " ".join(f"intext:{kw}" for kw in intext_keywords)

    full_query = f"({query_terms}) {exclusion_query} {intext_query}"
    logging.info(f"Generated Google Dorking Query: {full_query}")

    return full_query

def google_search(query, config, results_per_page=10):
    """Perform Google Custom Search API request."""
    google_api_key = config.get("GOOGLE_API_KEY")
    cx = config.get("CX")
    total_results = config.get("TOTAL_RESULTS", 50)

    if not google_api_key or not cx:
        logging.error("Google API key or CX ID missing in config file.")
        return []

    base_url = "https://www.googleapis.com/customsearch/v1"
    results = []

    for start in range(1, total_results + 1, results_per_page):
        params = {
            "key": google_api_key,
            "cx": cx,
            "q": query,
            "num": results_per_page,
            "start": start,
        }

        logging.info(f"Fetching results {start} to {start + results_per_page - 1}...")

        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "items" in data:
                results.extend(data["items"])
            else:
                logging.warning("No results found in this batch.")

            time.sleep(1)  # Respect API rate limits
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            break

    return results

def save_results_to_json(results, filename):
    """Save search results to a JSON file."""
    with open(filename, "w") as json_file:
        json.dump(results, json_file, indent=4)
    logging.info(f"Results saved to {filename}")

def save_results_to_csv(results, filename):
    """Save search results to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Title", "Link"])  # Header row

        for item in results:
            csv_writer.writerow([item.get("title", "N/A"), item.get("link", "N/A")])

    logging.info(f"Results saved to {filename}")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Google Dorking Search for APT & Malware & Threat Reports")
    parser.add_argument("search_keyword", help="The APT/Malware/Threat name to search for")
    parser.add_argument("--config", default="config.json", help="Path to the configuration file (default: config.json)")
    return parser.parse_args()

def main():
    """Main execution function."""
    args = parse_arguments()
    search_keyword = args.search_keyword.strip()
    config_path = args.config.strip()

    if not search_keyword:
        logging.error("Error: Search keyword cannot be empty.")
        sys.exit(1)

    logging.info(f"Using configuration from: {config_path}")
    config = load_config(config_path)

    logging.info(f"Starting search for: {search_keyword}")
    refined_query = build_google_dorking_query(search_keyword, config)
    search_results = google_search(refined_query, config)

    if search_results:
        logging.info(f"Total results retrieved: {len(search_results)}")
        json_filename = f"{search_keyword.replace(' ', '_')}_search_results.json"
        csv_filename = f"{search_keyword.replace(' ', '_')}_search_results.csv"

        save_results_to_json(search_results, json_filename)
        save_results_to_csv(search_results, csv_filename)

        for index, item in enumerate(search_results, start=1):
            print(f"{index}. {item.get('title')}\n{item.get('link')}\n")
    else:
        logging.info("No results found.")

if __name__ == "__main__":
    main()
