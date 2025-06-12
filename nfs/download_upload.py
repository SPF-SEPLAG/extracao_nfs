import os
import requests
from pathlib import Path

from sharepoint_utils import (
    get_sharepoint_token,
    download_sharepoint_file,
    upload_sharepoint_file
)

# CONFIGURAÇÕES
base_url = "https://cecad365.sharepoint.com/sites/AutomatizacoesSPF"
folder_origem = "/sites/AutomatizacoesSPF/Documentos Compartilhados/General/teste automação notas fiscais/notas fiscais telma"
folder_destino = "/sites/AutomatizacoesSPF/Documentos Compartilhados/General/teste automação notas fiscais/notas fiscais"

local_folder = Path("pdfs")
local_folder.mkdir(parents=True, exist_ok=True)

# AUTENTICAÇÃO
token_data = get_sharepoint_token()
if "access_token" not in token_data:
    print("❌ Falha ao obter token do SharePoint.")
    exit()

headers = {
    "Authorization": f"Bearer {token_data['access_token']}",
    "Accept": "application/json;odata=verbose"
}

# LISTA DE ARQUIVOS NA PASTA DE ORIGEM
endpoint = f"{base_url}/_api/web/GetFolderByServerRelativeUrl('{folder_origem}')/Files"
response = requests.get(endpoint, headers=headers)

if response.status_code == 200:
    files = response.json()['d']['results']
    print(f"📁 {len(files)} arquivos encontrados em '{folder_origem}'")


    for file in files:
        file_name = file['Name']
        print(f"\n⬇️ Baixando de X: {file_name}")
        
        local_path = local_folder / file_name
        download_success = download_sharepoint_file(
            base_url=base_url,
            folder_path=folder_origem,
            file_name=file_name,
            local_filename=str(local_path)
        )

        if not download_success:
            print(f"⚠️ Falha ao baixar {file_name}")
            continue
        
        print(f"⬆️ Enviando para Y: {file_name}")
        upload_success = upload_sharepoint_file(
            base_url=base_url,
            folder_path=folder_destino,
            file_name=file_name,
            local_filename=str(local_path)
        )

        if upload_success:
            print(f"✅ Enviado para destino: {file_name}")
        else:
            print(f"⚠️ Falha ao enviar para destino: {file_name}")

else:
    print(f"❌ Erro ao listar arquivos na pasta de origem: {response.status_code}")
    print(response.text)







for file in files:
    upload("pdf")
    upload("lock")

    while True:
        if sharepoint_file_exists(base_url, folder_destino, 'processing.lock'):
            next
        else:
            sleep(10)
            break
