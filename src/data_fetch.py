import os
from math import ceil
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.data_format import normalize_marks


def fetch_toplist(event_url: str, amount: int = 100, delay: float = 0.1, output_folder: str | None = None) -> pd.DataFrame | None:
    """
    Fetches an athletics toplist table from a World Athletics event page and saves it to CSV.

    Returns
    -------
    pandas.DataFrame or None
        The parsed results table if successful, or None if parsing fails.
    """
    max_pages = 10
    amount_per_page = 100
    pageNum = ceil(amount / amount_per_page)
    all_rows=[]
    for page_num in range(1, pageNum + 1):

        print(f"📡 Fetching data from: {event_url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AthleticsDataBot/1.0; +https://worldathletics.org)"
        }

        paged_url = f"{event_url}?page={page_num}"
        try:
            response = requests.get(paged_url, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {paged_url}: {e}")
            continue

        time.sleep(delay)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the main results table body
        tbody = soup.find("tbody")
        if not tbody:
            print("No table body found for {paged_url}")
            return None

        rows_data = []
        rows = tbody.find_all("tr")
        for row in rows:   # Look in the children of this PageElement and find all PageElement objects that match the given criteria
            cells = row.find_all("td")
            if not cells:
                continue

            row_dict = {}
            for cell in cells:
                # each <td> has a data-th attribute
                header = cell.get("data-th", "").strip()
                value = cell.get_text(strip=True)

                # capture link if available
                link = cell.find("a")
                if link and link.get("href"):
                    row_dict[f"{header}_link"] = "https://worldathletics.org" + link["href"]

                row_dict[header] = value
            rows_data.append(row_dict)

        all_rows.extend(rows_data)
        if len(all_rows) >= amount:
            print("Reached requested amount.")
            break

    if not all_rows:
        print("⚠No rows found in table.")
        return None

    # convert to pandas DataFrame
    df = pd.DataFrame(all_rows)
    df = normalize_marks(df)

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

        parts = [p for p in event_url.split("/") if p]
        filename = f"{parts[-4]}_{parts[-3]}_{parts[-2]}_{parts[-1]}.csv".replace("?", "_")
        filepath = os.path.join(output_folder, filename)

        df.to_csv(filepath, index=False)
        print(f"Saved {len(df)} rows to {filepath}")

    return df

def build_event_url(event_category: str, event_name: str, gender: str, year: int) -> str:
    base_url = "https://worldathletics.org/records/toplists"
    return f"{base_url}/{event_category}/{event_name}/all/{gender}/senior/{year}?bestResultsOnly=false"

if __name__ == "__main__":
    # test run
    test_url = "https://worldathletics.org/records/toplists/sprints/100-metres/all/women/senior/2024"
    df = fetch_toplist(test_url, "C:\\Users\\44784\\Documents\\Coding\\Python\\AthleticsDataProject\\TestOutput")
    if df is not None:
        print("🔍 Preview of scraped data:")
        print(df.head())