from count_list_sharepoint_utils import count_files_in_sharepoint_folder

base_url = "https://cecad365.sharepoint.com/sites/AutomatizacoesSPF"
folder_path = "/sites/AutomatizacoesSPF/Documentos Compartilhados/General/teste automação notas fiscais/notas fiscais"

count_files_in_sharepoint_folder(base_url, folder_path)

print(count_files_in_sharepoint_folder)