import os
from sharepoint_utils import upload_sharepoint_file

# Pasta local com documentos
pasta_local = 'nfs/nfs_upload'

# Dados Sharepoint
base_url = "https://cecad365.sharepoint.com/sites/AutomatizacoesSPF"
sharepoint_folder = "/sites/AutomatizacoesSPF/Documentos Compartilhados/General/teste automação notas fiscais/notas fiscais"

# Loop para arquivos da pasta local
for file_name in os.listdir(pasta_local):
    local_path = os.path.join(pasta_local, file_name)

    if not os.path.isfile(local_path):
        continue
    

    print(f"🔁 Enviando: {file_name}")
    success = upload_sharepoint_file(
        base_url=base_url,
        folder_path=sharepoint_folder,
        file_name=file_name,
        local_filename=local_path
    )

    if not success:
        print(f"⚠️ Erro ao enviar {file_name}")
    else:
        print(f"✅ Enviado: {file_name}")

