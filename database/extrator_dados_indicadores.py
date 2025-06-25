import glob
import os
import pandas as pd
import sqlite3
import re
from pyxlsb import open_workbook

# Importar dados de arquivos Indicadores_Fomento_*  para um banco de dados SQLite
def import_xlsb_to_sqlite(input_files, output_db, sheet_name='BD_Resultado Lotes', columns=None):
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect(output_db)
    
    # Mapeamento para conversão da coluna CLASSIFICAÇÃO
    class_map = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}
    
    for file_path in input_files:
        try:
            with open_workbook(file_path) as wb:
                if sheet_name in wb.sheets:
                    # Ler as colunas desejadas
                    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='pyxlsb', usecols=columns)
                    
                    # Limpar nomes de colunas
                    df.columns = [col.strip().replace(' ', '_') for col in df.columns]
                    
                    # Converter valores da coluna CLASSIFICAÇÃO
                    if 'CLASSIFICAÇÃO' in df.columns:
                        df['CLASSIFICAÇÃO'] = df['CLASSIFICAÇÃO'].map(class_map)
                        # Verificar valores não mapeados
                        if df['CLASSIFICAÇÃO'].isna().any():
                            print(f"Aviso: Valores inválidos em CLASSIFICAÇÃO encontrados em {file_path}")
                    
                    # Extrair ano do nome do arquivo
                    file_name = os.path.basename(file_path)
                    year_match = re.search(r'Indicadores_Fomento_(\d{4})\.xlsb', file_name)
                    if year_match:
                        year = int(year_match.group(1))
                        df['Ano'] = year
                    else:
                        print(f"Aviso: Não foi possível extrair o ano do arquivo {file_name}")
                        df['Ano'] = None
                    
                    # Remover linhas que contêm NaN ou null
                    df = df.dropna()

                    # Salvar na tabela 'resultados'
                    df.to_sql('resultados', conn, if_exists='append', index=False)
                    print(f"Dados de {file_name} importados com sucesso para a tabela 'resultados' com ano {year}")
                else:
                    print(f"Aba '{sheet_name}' não encontrada em {file_path}")
        except Exception as e:
            print(f"Erro ao processar {file_path}: {str(e)}")
    
    # Fechar conexão
    conn.close()
    print(f"\nBanco de dados salvo em {output_db}")

# Configurações para Indicadores_Fomento_*
folder_path = r'P:\Git\database_zootecnico_depav\database\\'
input_files = glob.glob(os.path.join(folder_path, 'Indicadores_Fomento_*.xlsb'))
output_db = os.path.join(folder_path, 'resultado_lotes.db')
sheet_name = 'BD_Resultado Lotes'
columns = ['Fazenda', 'Proprietario', 'Conversão Alimentar', 'CLASSIFICAÇÃO']

# Processar e importar dados para a tabela 'nucleos'
excel_file = pd.ExcelFile(os.path.join(folder_path, "PLANILHA_MESTRA.xlsx"))
df_nucleos = excel_file.parse("DADOS CADASTRAIS", header=0, usecols=['Aviário', 'Número do Núcleo', 'Nome Proprietário'])
df_nucleos = df_nucleos.dropna(subset=['Número do Núcleo'])
df_nucleos['Número do Núcleo'] = df_nucleos['Número do Núcleo'].astype(float).astype(int).astype(str)
print(df_nucleos.head())

conn = sqlite3.connect(output_db)
df_nucleos.to_sql('nucleos', conn, if_exists='replace', index=False)
conn.close()
print("Tabela 'nucleos' criada e salva com sucesso.")

# Configurações para Promob_*
input_promob = glob.glob(os.path.join(folder_path, 'ProMOB_*.xlsb'))
sheet_promob = 'Dados'

def import_promob_to_sqlite(input_promob, output_db, sheet_name=sheet_promob, columns=None):
    if columns is None:
        columns = ['Aviário','Aviário-Lote', 'Núcleo', 'Mês', 'Técnico','Nota']
    
    conn = sqlite3.connect(output_db)
    
    for file_path in input_promob:
        try:
            file_name = os.path.basename(file_path)
            print(f"Processando arquivo: {file_name}")
            
            with open_workbook(file_path) as wb:
                if sheet_name in wb.sheets:
                    df = pd.read_excel(file_path, sheet_name=sheet_promob, engine='pyxlsb', usecols=columns)
                    
                    # Limpar nomes de colunas
                    df.columns = [col.strip().replace(' ', '_') for col in df.columns]
                    
                    # Extrair os 4 primeiros caracteres da coluna 'Mês' e criar a coluna 'Ano'
                    if 'Mês' in df.columns:
                        df['Ano'] = df['Mês'].astype(str).str[:4]
                        df.drop(columns=['Mês'], inplace=True)
                    
                    # Remover linhas com dados faltantes
                    df = df.dropna(subset=['Aviário-Lote'])
                    
                    #Multiplicar valores da coluna 'Nota' por 100 e arredondar para 1 casa decimal
                    if 'Nota' in df.columns:
                        df['Nota'] = (df['Nota'] * 100).round(1)
                        
                # Extrair somente o primeiro nome da coluna 'Técnico'
                if 'Técnico' in df.columns:
                    # Substituir valores nulos por string vazia
                    df['Técnico'] = df['Técnico'].fillna('')
                    # Extrair o primeiro nome (tudo antes do primeiro espaço)
                    df['Técnico'] = df['Técnico'].str.split().str[0]
                    
                    df.to_sql('promob', conn, if_exists='append', index=False)
                    print(f"Dados de {file_name} importados para a tabela 'promob'")
                else:
                    print(f"Aba '{sheet_name}' não encontrada em {file_name}")
        except Exception as e:
            print(f"Erro ao processar {file_path}: {str(e)}")

    conn.close()
    print("Tabela 'promob' criada e duplicatas removidas com sucesso.")

if __name__ == "__main__":
    import_xlsb_to_sqlite(input_files, output_db, sheet_name, columns)

    # Importar planilhas ProMOB_*
    promob_files = glob.glob(os.path.join(folder_path, 'ProMOB_*.xlsb'))
    import_promob_to_sqlite(promob_files, output_db, sheet_name='Dados')