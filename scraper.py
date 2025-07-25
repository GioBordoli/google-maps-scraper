import os
import gspread
import subprocess
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# --- CONFIGURATION ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
API_KEY = 

def authenticate_google_sheets():
    """Authenticates with Google Sheets and returns a gspread client."""
    creds = None
    # Build absolute paths to the credentials and token files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, "token.json")
    credentials_path = os.path.join(base_dir, "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"Error: credentials.json not found at {credentials_path}")
                print("Please ensure it is in the same directory as the script.")
                exit()
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return gspread.authorize(creds), creds

def get_place_details(service, place_name):
    """Fetches detailed information for a specific place using its resource name."""
    try:
        # Request displayName instead of the resource name for the output
        place_details = service.places().get(
            name=place_name, # e.g., "places/ChIJN1t_tDeuEmsRUsoyG83frY4"
            fields="displayName,rating,userRatingCount,formattedAddress,internationalPhoneNumber,websiteUri"
        ).execute()
        return place_details
    except Exception as e:
        print(f"Error fetching details for {place_name}: {e}")
        return {}

def scrape_emails_from_website(url):
    """Scrapes emails from a website using the URL2email scraper."""
    if not url:
        return ""
    try:
        # Correctly locate the python executable in the venv
        python_executable = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
        scraper_script = os.path.join(os.path.dirname(__file__), 'URL2email', 'scraper.py')
        command = [python_executable, scraper_script, url]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        emails = result.stdout.strip().split('\n')
        if emails and "Found the following email addresses:" in emails[0]:
            emails = emails[1:]
        return ", ".join(set(emails))
    except subprocess.CalledProcessError as e:
        print(f"Error scraping emails from {url}: {e.stderr}")
        return ""
    except FileNotFoundError:
        print("Error: The email scraper script or python executable was not found.")
        return ""

def main():
    """Main function to run the scraper interactively."""
    print("--- Google Maps & Email Scraper ---")
    category = input("Enter the business category (e.g., 'accountant', 'lawyer'): ").strip()
    city = input("Enter the city to search in (e.g., 'Rome', 'Milan'): ").strip()
    sheet_name = input("Enter the name of the Google Sheet: ").strip()
    worksheet_name = input("Enter the name of the worksheet: ").strip()
    zip_codes_input = input("Enter comma-separated zip codes (or press Enter for default): ").strip()

    print("\nAuthenticating with Google... This may open a browser window.")
    gspread_client, creds = authenticate_google_sheets()
    places_service = build('places', 'v1', developerKey=API_KEY)

    try:
        spreadsheet = gspread_client.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        print(f"Creating new spreadsheet named '{sheet_name}'...")
        spreadsheet = gspread_client.create(sheet_name)
        user_email = creds.id_token.get('email') if creds.id_token else None
        if user_email:
            spreadsheet.share(user_email, perm_type='user', role='writer')
        else:
            print("Warning: Could not determine user email for sharing. Please share the spreadsheet manually.")

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        print(f"Creating new worksheet named '{worksheet_name}'...")
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="30")

    worksheet.clear()
    worksheet.append_row(["Name", "Rating", "Reviews", "Address", "Phone", "Website", "Emails"])

    try:
        if zip_codes_input:
            zip_codes = [zc.strip() for zc in zip_codes_input.split(',') if zc.strip()]
        else:
            # Default to a wide range of zip codes if none are provided
            zip_codes = [f"2{i:04d}" for i in range(100, 1000)] # Example: 20100 to 29999

        print(f"\nSearching for '{category}' in '{city}' across the specified zip codes...")
        all_unique_places = {}

        for zip_code in zip_codes:
            # More specific query combining category, city, and zip code
            current_query = f"{category} in {city} {zip_code}"
            print(f"  Searching for '{current_query}'...")
            next_page_token = None
            
            try:
                while True:
                    # Removed the restrictive 'includedType' which caused errors
                    body = {"textQuery": current_query, "maxResultCount": 20}
                    if next_page_token:
                        body["pageToken"] = next_page_token

                    response = places_service.places().searchText(
                        body=body,
                        fields="places.name,places.displayName"
                    ).execute()

                    places = response.get("places", [])
                    for place in places:
                        resource_name = place.get("name")
                        if resource_name:
                            all_unique_places[resource_name] = place

                    print(f"    Found {len(places)} results. Total unique places so far: {len(all_unique_places)}")

                    next_page_token = response.get("nextPageToken")
                    if not next_page_token:
                        break

            except Exception as e:
                print(f"  An error occurred during search for '{current_query}': {e}")

        print(f"\nTotal unique places found: {len(all_unique_places)}")
        print("Fetching details and scraping emails...")

        all_place_data = []
        for i, (resource_name, place_info) in enumerate(all_unique_places.items()):
            print(f"  Processing {i+1}/{len(all_unique_places)}: {place_info.get('displayName', {}).get('text')}")
            details = get_place_details(places_service, resource_name)
            if details:
                website_uri = details.get("websiteUri")
                emails = scrape_emails_from_website(website_uri)
                # Get the human-readable name from the 'displayName' field
                display_name = details.get("displayName", {}).get("text")
                all_place_data.append([
                    display_name,
                    details.get("rating"),
                    details.get("userRatingCount"),
                    details.get("formattedAddress"),
                    details.get("internationalPhoneNumber"),
                    website_uri,
                    emails
                ])
        
        if all_place_data:
            worksheet.append_rows(all_place_data)
            print(f"\nSuccessfully wrote {len(all_place_data)} records to '{sheet_name}' ('{worksheet_name}').")
        else:
            print("\nNo detailed place data could be fetched.")

        print(f"Sheet URL: {spreadsheet.url}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
