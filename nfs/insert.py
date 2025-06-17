import pandas as pd
from openpyxl import load_workbook

# Load original workbook
xlsx_path = "CONTROLE DCF 2025.xlsx"
wb = load_workbook(xlsx_path)
df_xlsx = pd.read_excel(xlsx_path, sheet_name="Notas Fiscais", engine="openpyxl")
df_csv = pd.read_csv("df.csv")

# Find first empty row based on column F (index 5)
first_empty_idx = df_xlsx[df_xlsx.iloc[:, 5].isna()].index.min()
if pd.isna(first_empty_idx):
    first_empty_idx = len(df_xlsx)

# Extend DataFrame if needed
rows_to_add = len(df_csv)
total_needed = first_empty_idx + rows_to_add
if len(df_xlsx) < total_needed:
    missing = total_needed - len(df_xlsx)
    new_rows = pd.DataFrame(columns=df_xlsx.columns, index=range(missing))
    df_xlsx = pd.concat([df_xlsx, new_rows], ignore_index=True)

# Insert values
df_xlsx.iloc[first_empty_idx:first_empty_idx + rows_to_add, 21] = df_csv["CNPJ"].values
df_xlsx.iloc[first_empty_idx:first_empty_idx + rows_to_add, 18] = df_csv["Valor Total"].values
df_xlsx.iloc[first_empty_idx:first_empty_idx + rows_to_add, 20] = df_csv["Nome Credor"].values
df_xlsx.iloc[first_empty_idx:first_empty_idx + rows_to_add, 5] = df_csv["Numero Nota Fiscal"].values

# ✅ Save only the updated sheet, preserving the others
with pd.ExcelWriter(xlsx_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    df_xlsx.to_excel(writer, sheet_name="Notas Fiscais", index=False)
