import subprocess
import os

def run_scraper_interactive():
    print("--- Google Maps Scraper Interactive CLI ---")
    print("Please provide the following information:")

    api_key = input("Google Cloud Places API Key: ").strip()
    query = input("Search Query (e.g., 'avvocati'): ").strip()
    city = input("City to scrape (e.g., 'Milan', 'Como'): ").strip()
    sheet_name = input("Name for the Google Sheet (e.g., 'My Leads'): ").strip()
    zip_codes_input = input("Comma-separated list of zip codes (e.g., '20121,20122,20123'): ").strip()

    # Convert comma-separated zip codes to a Python list
    zip_codes = [zc.strip() for zc in zip_codes_input.split(',') if zc.strip()]

    print("\n--- Running Scraper ---")
    print(f"API Key: {api_key}")
    print(f"Query: {query}")
    print(f"City: {city}")
    print(f"Sheet Name: {sheet_name}")
    print(f"Zip Codes: {zip_codes}")

    command = [
        os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python'),
        os.path.join(os.path.dirname(__file__), 'scraper.py'),
        '--api-key', api_key,
        '--query', query,
        '--sheet-name', sheet_name
    ]

    if zip_codes:
        command.extend(['--zip-codes', ','.join(zip_codes)])

    try:
        subprocess.run(command, check=True)
        print("\nScraper finished successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\nError running scraper: {e}")
        print(f"Stdout: {e.stdout.decode()}")
        print(f"Stderr: {e.stderr.decode()}")
    except FileNotFoundError:
        print("\nError: Python or scraper.py not found. Ensure venv is activated or paths are correct.")

if __name__ == "__main__":
    run_scraper_interactive()