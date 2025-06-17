from sharepoint_utils import download_sharepoint_file

base_url = "https://cecad365.sharepoint.com/sites/AutomatizacoesSPF"
folder_path = "/sites/AutomatizacoesSPF/Documentos Compartilhados/General/teste automação notas fiscais"
local_filename = "CONTROLE DCF 2025.xlsx"

download_sharepoint_file(base_url, folder_path, "CONTROLE DCF 2025.xlsx", local_filename)