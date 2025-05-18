
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from typing import Any, Optional, Dict

def get_drive_service(credentials_path="credentials.json", token_path="token.pickle"):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                print("Attempting re-authentication...")
                creds = None # Force re-authentication
        if not creds: # If refresh failed or no token at all
            if not os.path.exists(credentials_path):
                print(f"Error: Credentials file '{credentials_path}' not found.")
                print("Please download it from Google Cloud Console and place it here.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0) # Runs a local server for auth

        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f'An API error occurred: {error}')
        return None
    except Exception as e:
        print(f"An unexpected error occurred building the service: {e}")
        return None


def check_if_file_exists_in_drive_folder(service: Any, filename: str, drive_folder_id: str) -> bool:
    """
    Checks if a file with the given name already exists in the specified Google Drive folder.
    """
    try:
        # Escape single quotes in filename for the query, as Drive query language uses them for string literals
        query_filename = filename.replace("'", "\\'")
        query = f"name = '{query_filename}' and '{drive_folder_id}' in parents and trashed = false"

        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            # supportsAllDrives=True, # Add if you might use Shared Drives
            # includeItemsFromAllDrives=True, # Add if you might use Shared Drives
            corpora='user' # 'user' for My Drive, 'drive' for a specific Shared Drive (with driveId)
                           # 'allDrives' for all shared drives the user is a member of.
        ).execute()

        existing_files = response.get('files', [])
        if existing_files:
            print(f"Found existing file(s) with name '{filename}' in folder ID '{drive_folder_id}':")
            for f in existing_files:
                print(f"  - ID: {f.get('id')}, Name: {f.get('name')}")
            return True
        return False
    except HttpError as error:
        print(f"API error while checking for existing file '{filename}': {error}")
        # Depending on the error, you might want to re-raise or handle differently
        # For now, assume failure to check means we shouldn't risk overwriting/duplicating
        return True # Err on the side of caution: if check fails, assume it might exist.
                    # Or, return False and proceed with upload, logging the check failure.
                    # Let's change this to return False and log, so upload can proceed if check fails.
        # print(f"API error while checking for existing file '{filename}': {error}. Proceeding with upload attempt.")
        # return False # If you prefer to attempt upload even if check fails.
    except Exception as e:
        print(f"Unexpected error while checking for existing file '{filename}': {e}")
        return True # Err on the side of caution.
        # print(f"Unexpected error while checking for existing file '{filename}': {e}. Proceeding with upload attempt.")
        # return False

def upload_pdf_to_drive_folder(local_pdf_path: str, drive_folder_id: str,
                               new_filename: Optional[str] = None,
                               overwrite_existing: bool = False) -> Optional[Dict[str, Any]]:
    """
    Uploads a local PDF file to a specific Google Drive folder.
    Optionally checks if a file with the same name exists and skips or overwrites.

    Args:
        local_pdf_path (str): The local path to the PDF file.
        drive_folder_id (str): The ID of the Google Drive folder to upload to.
        new_filename (str, optional): The name for the file in Google Drive.
                                      If None, uses the local filename.
        overwrite_existing (bool): If True, will upload even if a file with the
                                   same name exists (Google Drive will version it or
                                   create a duplicate with (1), (2) etc. depending
                                   on exact API usage - create always makes new).
                                   If False (default), skips upload if name exists.

    Returns:
        Dict[str, Any] | None: A dictionary containing the 'id', 'name', and 'webViewLink'
                               of the uploaded file if successful, otherwise None.
                               If skipped, returns None.
    """
    if not os.path.exists(local_pdf_path):
        print(f"Error: Local PDF file not found at '{local_pdf_path}'")
        return None

    service = get_drive_service()
    if not service:
        print("Could not get Google Drive service. Aborting upload.")
        return None

    if new_filename is None:
        new_filename = os.path.basename(local_pdf_path)

    # --- Check if file already exists ---
    if not overwrite_existing:
        print(f"Checking if '{new_filename}' already exists in Drive folder ID '{drive_folder_id}'...")
        # In the check_if_file_exists_in_drive_folder, if an error occurs during the check,
        # it currently defaults to returning True (meaning "exists / don't upload").
        # You might want to adjust its error handling if you prefer to try uploading
        # even if the existence check fails.
        if check_if_file_exists_in_drive_folder(service, new_filename, drive_folder_id):
            print(f"File '{new_filename}' already exists and overwrite_existing is False. Skipping upload.")
            return None # Indicate skipped
    else:
        print(f"overwrite_existing is True. Will attempt to upload '{new_filename}' even if it exists.")


    file_metadata = {
        'name': new_filename,
        'parents': [drive_folder_id],
        'mimeType': 'application/pdf'
    }

    media = MediaFileUpload(local_pdf_path,
                            mimetype='application/pdf',
                            resumable=True)

    try:
        print(f"Uploading '{local_pdf_path}' as '{new_filename}' to Drive folder ID '{drive_folder_id}'...")
        file_resource = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink',
            supportsAllDrives=True # Good to include if folder might be in a Shared Drive
        ).execute()
        print(f"File uploaded successfully!")
        print(f"  ID: {file_resource.get('id')}")
        print(f"  Name: {file_resource.get('name')}")
        print(f"  Link: {file_resource.get('webViewLink')}")
        return file_resource
    except HttpError as error:
        print(f'An API error occurred during upload: {error}')
        if error.resp.status == 404:
            print("Error 404: The specified folder ID might be incorrect or you may not have access.")
        elif error.resp.status == 403:
            print("Error 403: Permission denied. Check API scope and folder write access.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during upload: {e}")
        return None

