import os
import requests
from pathlib import Path
import time

from sharepoint_utils import (
    get_token,
    download_sharepoint_file,
    upload_sharepoint_file
)

# CONFIGURAÇÕES
base_url = "https://cecad365.sharepoint.com/sites/AutomatizacoesSPF"
folder_origem = "/sites/AutomatizacoesSPF/Documentos Compartilhados/General/teste automação notas fiscais/notas fiscais telma"
folder_destino = "/sites/AutomatizacoesSPF/Documentos Compartilhados/General/teste automação notas fiscais/notas fiscais"

local_folder = Path("pdfs")
local_folder.mkdir(parents=True, exist_ok=True)

lock_file = Path(".fluxo_em_execucao")

# AUTENTICAÇÃO
access_token_sp = get_token("https://cecad365.sharepoint.com/.default")
if not access_token_sp:
    print("❌ Falha ao obter token do SharePoint.")
    exit()

headers = {
    "Authorization": f"Bearer {access_token_sp}",
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

        # BLOQUEIO: aguarda até que nenhum fluxo esteja em execução
        while lock_file.exists():
            print("🔒 Fluxo em execução detectado. Aguardando liberação...")
            time.sleep(10)

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

            # CRIA ARQUIVO DE BLOQUEIO
            lock_file.touch()
            print("🔐 Bloqueio ativado. Aguardando execução do fluxo...")

            # Aguarda tempo fixo (ou poderia ser monitoramento de pasta de saida)
            time.sleep(60)  # ajuste conforme o tempo médio do seu fluxo

            # REMOVE BLOQUEIO
            if lock_file.exists():
                lock_file.unlink()
                print("🔓 Bloqueio removido. Pronto para próxima iteração.")

        else:
            print(f"⚠️ Falha ao enviar para destino: {file_name}")

else:
    print(f"❌ Erro ao listar arquivos na pasta de origem: {response.status_code}")
    print(response.text)
