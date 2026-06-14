import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from config import SOURCES

# Fetch HTML content from a given URL
def fetch_url(url):
    try:
        # Send HTTP GET request with timeout
        response = requests.get(url, timeout=30)

        print(f"[INFO] URL: {url}")
        print(f"[INFO] Status Code: {response.status_code}")

        # Return raw HTML content
        return response.text

    except Exception as e:
        # Handle any request or network errors
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None


def main():
    # Iterate through all configured sources
    for url in SOURCES:
        html = fetch_url(url)

        if html:
            # Print a small preview of HTML for debugging
            print("\n--- HTML Preview ---\n")
            print(html[:1000])


if __name__ == "__main__":
    main()