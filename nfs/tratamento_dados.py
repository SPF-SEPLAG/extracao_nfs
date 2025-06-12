import pandas as pd
import openpyxl
import re

# Carregar o CSV
df = pd.read_csv('/home/x17187272677/code/nfs/NOTAS FISCAIS MESTRE.csv', encoding='utf-8')

def corrigir_e_limpar_credor(texto):
    try:
        # Corrigir mojibake
        texto_corrigido = texto.encode('latin1').decode('utf-8')
    except:
        texto_corrigido = texto

    # Remover tudo até e incluindo 'emitente' (sem considerar maiúsculas/minúsculas)
    match = re.search(r'(?i)emitente\s*(.*)', texto_corrigido)
    if match:
        return match.group(1).strip()
    return texto_corrigido.strip()


def treatment_script():

    df.drop(df.columns[4:16], axis=1, inplace=True)
    df.columns = ['CNPJ', 'Valor Total', 'Nome Credor', 'Numero Nota Fiscal']

    # Apagar linhas indesejadas
    df = df[~df.iloc[:, 0].astype(str).str.startswith('\\')]

    # Limpar coluna CNPJ
    df['CNPJ'] = df['CNPJ'].astype(str).str.replace(r'^CNPJ:?\s*', '', regex=True)

    # Limpar coluna Nota Fiscal
    df['Numero Nota Fiscal'] = df['Numero Nota Fiscal'].astype(str).str.replace(r'^[^\d]*', '', regex=True)

    # Trocar ponto por vírgula como sepador decimal
    df['Valor Total'] = df['Valor Total'].astype(str).str.replace(r'.', ',', regex=False)

    # Correção textual
    df['Nome Credor'] = df['Nome Credor'].apply(corrigir_e_limpar_credor)

    return df 
    #df.to_excel('df.xlsx', index=False, engine='openpyxl')


treated_df = treatment_script()
