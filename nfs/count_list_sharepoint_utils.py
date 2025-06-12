import requests
from sharepoint_utils import get_sharepoint_token

def count_files_in_sharepoint_folder(base_url, folder_path):
    """
    Conta os arquivos em uma pasta do SharePoint via API REST.

    Args:
        base_url (str): Ex: 'https://cecad365.sharepoint.com/sites/SeuSite'
        folder_path (str): Ex: '/Documentos Compartilhados/SuaPasta'

    Returns:
        int: número de arquivos na pasta
    """
    token_data = get_sharepoint_token()
    if not token_data or "access_token" not in token_data:
        print("❌ Falha ao obter token")
        return 0

    headers = {
        "Authorization": f"Bearer {token_data['access_token']}",
        "Accept": "application/json;odata=verbose"
    }

    endpoint = f"{base_url}/_api/web/GetFolderByServerRelativeUrl('{folder_path}')/Files"
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        files = response.json()['d']['results']
        for file in files:
            print(f"{file['Name']}")
        print(f"📁 Total de arquivos em '{folder_path}': {len(files)}")
        return len(files)
    else:
        print(f"❌ Erro {response.status_code} ao acessar a pasta")
        print(response.text)
        return 0
