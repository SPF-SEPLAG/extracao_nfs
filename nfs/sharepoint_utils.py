import os, msal, pickle
from pathlib import Path

import requests

config = {
  "authority": "https://login.microsoftonline.com/e5d3ae7c-9b38-48de-a087-f6734a287574",
  "client_id": "d44a05d5-c6a5-4bbb-82d2-443123722380",
  "scope": ["https://cecad365.sharepoint.com/.default"], #["Group.ReadWrite.All"],
  "username": "x17187272677@ca.mg.gov.br",
  "endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
}

CACHE_FILE = "msal_cache.bin"

def get_sharepoint_token():
    # ✅ Load or create token cache
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())

    app = msal.PublicClientApplication(
        config["client_id"], authority=config["authority"], token_cache=cache
        )

    # initialize result variable to hole the token response
    result = None 

    # We now check the cache to see
    # whether we already have some accounts that the end user already used to sign in before.
    accounts = app.get_accounts(username=config.get("username"))
    print(accounts)

    if accounts:
        result = app.acquire_token_silent(config["scope"], account=accounts[0])

    if not result:
        # So no suitable token exists in cache. Let's get a new one from Azure AD.
        result = app.acquire_token_interactive(scopes=config["scope"])

    # ✅ Save updated cache
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())
        print("💾 Token cache saved.")
    
    if "access_token" in result:
        #print(result)  # Yay!
        return result
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))  # You may need this when reporting a bug


def download_sharepoint_file(base_url, folder_path, file_name, local_filename):
    """
    Downloads a file from SharePoint using dynamic components for the URL.

    Args:
        base_url (str): The base SharePoint site URL (e.g., 'https://cecad365.sharepoint.com/sites/Splor').
        folder_path (str): The relative path to the folder containing the file (e.g., '/Documentos Compartilhados/General').
        file_name (str): The name of the file to download (e.g., 'datamart.xlsx').
        local_filename (str): The local path where the file will be saved.

    Returns:
        bool: True if the file was downloaded successfully, False otherwise.
    """
    # Construct the file URL
    relative_url = f"{folder_path}/{file_name}".replace(" ", "%20")
    file_url = f"{base_url}/_api/web/GetFileByServerRelativeUrl('{relative_url}')/$value"

    # Acquire token using the utility function
    result = get_sharepoint_token()

    if result and "access_token" in result:
        print("Access token acquired.")
        # Download the file
        response = requests.get(
            file_url,
            headers={'Authorization': 'Bearer ' + result['access_token']},
            stream=True  # Enable streaming
        )
        if response.status_code == 200:
            # Save the file locally in chunks

            Path(local_filename).parent.mkdir(parents=True, exist_ok=True)
            with open(local_filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File downloaded successfully as {local_filename}")
            return True
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")
            print(response.text)
            return False
    else:
        print("Failed to acquire an access token.")
        return False


def upload_sharepoint_file(base_url, folder_path, file_name, local_filename):
    """
    Uploads a file to SharePoint using dynamic components for the URL.
    If the file already exists, it will be overwritten.

    Args:
        base_url (str): The base SharePoint site URL (e.g., 'https://cecad365.sharepoint.com/sites/Splor').
        folder_path (str): The relative path to the folder where the file will be uploaded (e.g., '/Documentos Compartilhados/General').
        file_name (str): The name of the file to upload (e.g., 'datamart.txt').
        local_filename (str): The local path of the file to upload.

    Returns:
        bool: True if the file was uploaded successfully, False otherwise.
    """
    # Construct the upload URL
    upload_url = f"{base_url}/_api/web/GetFolderByServerRelativeUrl('{folder_path}')/Files/add(url='{file_name}',overwrite=true)"

    # Acquire token using the utility function
    result = get_sharepoint_token()

    if result and "access_token" in result:
        print("Access token acquired.")
        # Read the local file content to upload
        with open(local_filename, 'rb') as file:
            file_content = file.read()

        # Upload the file with raw binary data
        headers = {
            'Authorization': 'Bearer ' + result['access_token'],
            'Accept': 'application/json',
            'Content-Type': 'application/octet-stream'  # Content type for raw binary data
        }

        response = requests.post(
            upload_url,
            headers=headers,
            data=file_content  # Send the raw binary data as the body
        )

        if response.status_code in [200, 201]:
            print(f"File uploaded successfully to {folder_path}/{file_name}")
            return True
        else:
            print(f"Failed to upload the file. Status code: {response.status_code}")
            print(response.text)
            return False
    else:
        print("Failed to acquire an access token.")
        return False