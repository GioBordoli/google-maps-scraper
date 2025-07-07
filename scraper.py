import os
import argparse
import gspread
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# --- CONFIGURATION ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]

def authenticate_google_sheets():
    """Authenticates with Google Sheets and returns a gspread client."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Make sure to have credentials.json from Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return gspread.authorize(creds), creds

def get_place_details(service, place_name):
    """Fetches detailed information for a specific place using its resource name."""
    try:
        # Request details using the place's resource name
        place_details = service.places().get(
            name=place_name, # e.g., "places/ChIJN1t_tDeuEmsRUsoyG83frY4"
            fields="name,rating,userRatingCount,formattedAddress,internationalPhoneNumber,websiteUri"
        ).execute()
        return place_details
    except Exception as e:
        print(f"Error fetching details for {place_name}: {e}")
        return {}

def main():
    """Main function to run the scraper."""
    parser = argparse.ArgumentParser(description="Scrape Google Maps and save data to Google Sheets.")
    parser.add_argument("--api-key", required=True, help="Your Google Cloud Places API key.")
    parser.add_argument("--query", required=True, help="The search query (e.g., 'avvocati a Roma').")
    parser.add_argument("--sheet-name", required=True, help="The name of the Google Sheet to save data to.")
    parser.add_argument("--zip-codes", help="Comma-separated list of zip codes to search within.")
    args = parser.parse_args()

    # 1. Authenticate and initialize services
    print("Authenticating with Google... This may open a browser window.")
    # Note: The first run will require browser authentication for Google Sheets.
    gspread_client, creds = authenticate_google_sheets()
    places_service = build('places', 'v1', developerKey=args.api_key)

    # 2. Find or create the Google Sheet
    try:
        spreadsheet = gspread_client.open(args.sheet_name)
    except gspread.SpreadsheetNotFound:
        print(f"Creating new spreadsheet named '{args.sheet_name}'...")
        spreadsheet = gspread_client.create(args.sheet_name)
        # Share with your email to ensure you have access in Google Drive
        # Share with your email to ensure you have access in Google Drive
        # Note: This assumes the email is available in the ID token of the credentials.
        user_email = creds.id_token.get('email') if creds.id_token else None
        if user_email:
            spreadsheet.share(user_email, perm_type='user', role='writer')
        else:
            print("Warning: Could not determine user email for sharing. Please share the spreadsheet manually.")

    worksheet = spreadsheet.sheet1
    worksheet.clear()
    worksheet.append_row(["Name", "Rating", "Reviews", "Address", "Phone", "Website"])

    try:
        # Milan Zip Codes (approximate range, some may be invalid or not used for Places API)
        # A more robust solution would involve a curated list or a geo-fencing service.
        if args.zip_codes:
            MILAN_ZIP_CODES = [zc.strip() for zc in args.zip_codes.split(',') if zc.strip()]
        else:
            MILAN_ZIP_CODES = [f"22{i:03d}" for i in range(10, 101)] # Default to Como zip codes if not provided

        # 3. Search for places with pagination and geographic subdivision
        print(f"Searching for '{args.query}' across Milan zip codes with pagination...")
        all_unique_places = {} # Using a dictionary to store unique places by resource_name

        for zip_code in MILAN_ZIP_CODES:
            current_query = f"{args.query} {zip_code}"
            print(f"  Searching in {zip_code} for '{current_query}'...")
            next_page_token = None
            
            try:
                while True:
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
                            all_unique_places[resource_name] = place # Store by resource_name to ensure uniqueness

                    print(f"    Found {len(places)} results on this page. Total unique so far: {len(all_unique_places)}")

                    next_page_token = response.get("nextPageToken")
                    if not next_page_token:
                        break # No more pages for this zip code

            except Exception as e:
                print(f"  An error occurred during search for '{current_query}': {e}")
                # Continue to the next zip code even if one fails

        print(f"Total unique places found across all zip codes: {len(all_unique_places)}")

        # 4. Fetch details for each unique place and write to sheet
        all_place_data = []
        for resource_name, place_info in all_unique_places.items():
            details = get_place_details(places_service, resource_name)
            if details:
                all_place_data.append([
                    details.get("name"),
                    details.get("rating"),
                    details.get("userRatingCount"),
                    details.get("formattedAddress"),
                    details.get("internationalPhoneNumber"),
                    details.get("websiteUri")
                ])
        
        if all_place_data:
            worksheet.append_rows(all_place_data)
            print(f"Successfully wrote {len(all_place_data)} records to '{args.sheet_name}'.")
        else:
            print("No detailed place data could be fetched.")

        print(f"Sheet URL: {spreadsheet.url}")

    except Exception as e:
        print(f"An error occurred during Google Places search: {e}")

if __name__ == "__main__":
    main()