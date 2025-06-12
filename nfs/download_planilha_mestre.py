from sharepoint_utils import download_sharepoint_file, get_sharepoint_token

base_url = "https://cecad365.sharepoint.com/sites/AutomatizacoesSPF"
folder_path = "/sites/AutomatizacoesSPF/Documentos Compartilhados/General/teste automação vitor"
local_filename = "NOTAS FISCAIS MESTRE.csv"

download_sharepoint_file(base_url, folder_path, "NOTAS FISCAIS MESTRE.csv", local_filename)