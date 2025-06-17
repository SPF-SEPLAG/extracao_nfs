import os
import msal
import time
import requests
from pathlib import Path

# === CONFIGURAÇÕES DE AUTENTICAÇÃO ===
CACHE_FILE = "msal_cache.bin"

config = {
    "authority": "https://login.microsoftonline.com/e5d3ae7c-9b38-48de-a087-f6734a287574",
    "client_id": "d44a05d5-c6a5-4bbb-82d2-443123722380",
    "username": "x17187272677@ca.mg.gov.br"
}

def get_sharepoint_token(scope: str):
    """
    Obtém um token de acesso para o escopo especificado (SharePoint ou Flow).
    """
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())

    app = msal.PublicClientApplication(
        config["client_id"],
        authority=config["authority"],
        token_cache=cache
    )

    accounts = app.get_accounts(username=config["username"])
    result = app.acquire_token_silent([scope], account=accounts[0]) if accounts else None

    if not result:
        result = app.acquire_token_interactive(scopes=[scope])

    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())
        print("💾 Cache MSAL atualizado.")

    if "access_token" in result:
        return result["access_token"]
    else:
        print("❌ Erro ao obter token:")
        print(result.get("error"))
        print(result.get("error_description"))
        return None

def download_sharepoint_file(base_url, folder_path, file_name, local_filename):
    relative_url = f"{folder_path}/{file_name}".replace(" ", "%20")
    file_url = f"{base_url}/_api/web/GetFileByServerRelativeUrl('{relative_url}')/$value"

    access_token = get_sharepoint_token("https://cecad365.sharepoint.com/.default")
    if not access_token:
        return False

    response = requests.get(
        file_url,
        headers={'Authorization': f"Bearer {access_token}"},
        stream=True
    )

    if response.status_code == 200:
        Path(local_filename).parent.mkdir(parents=True, exist_ok=True)
        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"📥 Arquivo salvo em: {local_filename}")
        return True
    else:
        print(f"❌ Erro ao baixar arquivo: {response.status_code}")
        print(response.text)
        return False

def upload_sharepoint_file(base_url, folder_path, file_name, local_filename):
    upload_url = f"{base_url}/_api/web/GetFolderByServerRelativeUrl('{folder_path}')/Files/add(url='{file_name}',overwrite=true)"
    access_token = get_sharepoint_token("https://cecad365.sharepoint.com/.default")
    if not access_token:
        return False

    with open(local_filename, 'rb') as file:
        file_content = file.read()

    headers = {
        'Authorization': f"Bearer {access_token}",
        'Accept': 'application/json',
        'Content-Type': 'application/octet-stream'
    }

    response = requests.post(
        upload_url,
        headers=headers,
        data=file_content
    )

    if response.status_code in [200, 201]:
        print(f"📤 Arquivo enviado: {file_name}")
        return True
    else:
        print(f"❌ Erro ao enviar arquivo: {response.status_code}")
        print(response.text)
        return False

def count_files_in_sharepoint_folder(base_url, folder_path):
    access_token = get_sharepoint_token("https://cecad365.sharepoint.com/.default")
    if not access_token:
        return 0

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json;odata=verbose"
    }

    endpoint = f"{base_url}/_api/web/GetFolderByServerRelativeUrl('{folder_path}')/Files"
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        files = response.json()['d']['results']
        for file in files:
            print(f"📄 {file['Name']}")
        print(f"📁 Total de arquivos em '{folder_path}': {len(files)}")
        return len(files)
    else:
        print(f"❌ Erro {response.status_code} ao acessar a pasta")
        print(response.text)
        return 0

def verificar_status_fluxo_com_runid(run_id, flow_id, environment_id, access_token, intervalo_segundos=5):
    url = f"https://management.azure.com/providers/Microsoft.ProcessSimple/environments/{environment_id}/flows/{flow_id}/runs/{run_id}?api-version=2016-11-01"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    while True:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Erro ao consultar o status da execução ({response.status_code})")
            print(response.text)
            break

        data = response.json()
        status = data["properties"]["status"]
        start_time = data["properties"].get("startTime")

        print(f"⏳ Execução iniciada em {start_time} — Status atual: {status}")

        if status == "Succeeded":
            print("✅ Execução concluída com sucesso!")
            return True
        elif status == "Failed":
            raise Exception("❌ A execução do fluxo falhou!")
        elif status == "Cancelled":
            raise Exception("⚠️ Execução cancelada!")
        else:
            time.sleep(intervalo_segundos)
