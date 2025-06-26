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
                    df_resultado = pd.read_excel(file_path, sheet_name=sheet_name, engine='pyxlsb', usecols=columns)
                    
                    # Limpar nomes de colunas
                    df_resultado.columns = [col.strip().replace(' ', '_') for col in df_resultado.columns]
                    
                    
                    # Converter valores da coluna CLASSIFICAÇÃO
                    if 'CLASSIFICAÇÃO' in df_resultado.columns:
                        df_resultado['CLASSIFICAÇÃO'] = df_resultado['CLASSIFICAÇÃO'].map(class_map)
                        # Verificar valores não mapeados
                        if df_resultado['CLASSIFICAÇÃO'].isna().any():
                            print(f"Aviso: Valores inválidos em CLASSIFICAÇÃO encontrados em {file_path}")
                    
                    # Converter CLASSIFICAÇÃO para inteiro apenas se for um valor numérico entre 0 e 5
                    if 'CLASSIFICAÇÃO' in df_resultado.columns:
                        # Converter para NaN valores que não estão entre 0 e 5
                        df_resultado['CLASSIFICAÇÃO'] = df_resultado['CLASSIFICAÇÃO'].apply(
                            lambda x: x if pd.notnull(x) and 0 <= x <= 5 else pd.NA
                        )
                        # Converter para inteiro os valores válidos
                        df_resultado['CLASSIFICAÇÃO'] = df_resultado['CLASSIFICAÇÃO'].astype('Int64')

                    # Converter a coluna 'Número Composto' para string
                    if 'Número_Composto' in df_resultado.columns:
                        df_resultado['Número_Composto'] = df_resultado['Número_Composto'].astype(str)

                    # Procurar valores '-' na coluna 'Número Composto' e substituir por string vazia
                    if 'Número_Composto' in df_resultado.columns:
                        df_resultado['Número_Composto'] = df_resultado['Número_Composto'].replace('-0', '', regex=True)
                        # Verificar se a coluna contém valores vazios após a substituição
                        if df_resultado['Número_Composto'].str.strip().eq('').any():
                            print(f"Aviso: Valores vazios encontrados na coluna 'Número Composto' em {file_path}")
                            
                    # Extrair ano do nome do arquivo
                    file_name = os.path.basename(file_path)
                    year_match = re.search(r'Indicadores_Fomento_(\d{4})\.xlsb', file_name)
                    if year_match:
                        year = int(year_match.group(1))
                        df_resultado['Ano'] = year
                    else:
                        print(f"Aviso: Não foi possível extrair o ano do arquivo {file_name}")
                        df_resultado['Ano'] = None
                    
                    # Remover linhas que contêm NaN ou null
                    df_resultado = df_resultado.dropna()
                    
                    #Converter coluna 'Nome Linhagem' para string
                    if 'Nome_Linhagem' in df_resultado.columns:
                        df_resultado['Nome_Linhagem'] = df_resultado['Nome_Linhagem'].astype(str)
                        # Remover espaços extras
                        df_resultado['Nome_Linhagem'] = df_resultado['Nome_Linhagem'].str.strip()
                        
                    # Converter "COBB SLOW 500" para "COBB MALE" na coluna Nome_Linhagem
                    if 'Nome_Linhagem' in df_resultado.columns:
                        df_resultado['Nome_Linhagem'] = df_resultado['Nome_Linhagem'].replace('COBB SLOW 500', 'COBB MALE')

                    # Caso a coluna 'Lista matriz' tenha uma virgula "," como separador trazer somente o valor antes da vírgula
                    if 'Lista_matriz' in df_resultado.columns:
                        df_resultado['Lista_matriz'] = df_resultado['Lista_matriz'].str.split(',').str[0]

                    # Trazer o valor após o último hífen "-" da coluna 'Lista matriz'
                    if 'Lista_matriz' in df_resultado.columns:
                        df_resultado['Lista_matriz'] = df_resultado['Lista_matriz'].str.split('-').str[-1].str.strip()
                    
                    # Converter coluna 'Idade Matriz' para número inteiro, arrendondando para cima
                    if 'Idade_Matriz' in df_resultado.columns:
                        df_resultado['Idade_Matriz'] = df_resultado['Idade_Matriz'].apply(lambda x: -(-x // 1) if pd.notna(x) else x)
                    
                    # Salvar na tabela 'resultados'
                    df_resultado.to_sql('resultados', conn, if_exists='append', index=False)
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
columns = ['Fazenda', 'Número Composto', 'Proprietario', 'Conversão Alimentar', 'CLASSIFICAÇÃO','Nome Linhagem','Fornecedor Pinto','Lista matriz','Idade Matriz','Mortalidade']

# Processar e importar dados para a tabela 'nucleos'
excel_file = pd.ExcelFile(os.path.join(folder_path, "PLANILHA_MESTRA.xlsx"))
df_nucleos = excel_file.parse("DADOS CADASTRAIS", header=0, usecols=['Aviário', 'Número do Núcleo', 'Nome Proprietário','Cidade'])
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

#Função para importar dados de planilhas ProMOB_*
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

# Configurações para Painel_Condenações_*
input_condena = glob.glob(os.path.join(folder_path, 'Painel_Condenações_*.xlsb'))
sheet_condena = 'BD_Condenações'

#Função para importar dados de planilhas Painel_Condenações_*
def import_condena_to_sqlite(input_condena, output_db, sheet_name=sheet_condena, columns=None):
    """
    Imports data from Painel_Condenações_*.xlsb files into a SQLite database table 'condena'.

    Parameters:
        input_condena (list): List of file paths to .xlsb files to import.
        output_db (str): Path to the SQLite database file.
        sheet_name (str): Name of the worksheet to read from each file.
        columns (list, optional): List of column names to import. If None, uses default columns.
    """
    if columns is None:
        columns = ['Data Produção', 'Data Alojamento','Fornecedor','Aviário','Lote','Placa Caminhão','Cabeça','Mortos','Peso','Total - Artrite (1 articulação)','Total - Artrite (2 articulações)','Parcial - Artrite (1 articulação)','Parcial - Artrite (2 articulações)']
    
    conn = sqlite3.connect(output_db)
    
    for file_path in input_condena:
        try:
            file_name = os.path.basename(file_path)
            print(f"Processando arquivo: {file_name}")
            
            with open_workbook(file_path) as wb:
                if sheet_name in wb.sheets:
                    # Primeiro, ler o cabeçalho para obter os nomes das colunas
                    header_df = pd.read_excel(file_path, sheet_name=sheet_condena, engine='pyxlsb')
                    
                    # Limpar nomes de colunas
                    header_df.columns = header_df.columns.str.strip()
                    
                    # Selecionar colunas desejadas
                    df = header_df[['Data Produção', 'Data Alojamento','Fornecedor','Aviário','Lote','Placa Caminhão','Cabeça','Mortos','Peso','Total - Artrite (1 articulação)','Total - Artrite (2 articulações)','Parcial - Artrite (1 articulação)','Parcial - Artrite (2 articulações)']]
                    
                    # Criar uma cópia completa do dataframe para evitar warnings
                    df = header_df[['Data Produção', 'Data Alojamento','Fornecedor','Aviário','Lote','Placa Caminhão','Cabeça','Mortos',
                                   'Peso','Total - Artrite (1 articulação)','Total - Artrite (2 articulações)',
                                   'Parcial - Artrite (1 articulação)','Parcial - Artrite (2 articulações)']].copy()
                    
                    # Converter datas do formato Excel para datetime
                    df['Data Produção'] = pd.to_datetime(df['Data Produção'], unit='D', origin='1899-12-30', errors='coerce')
                    df['Data Alojamento'] = pd.to_datetime(df['Data Alojamento'], unit='D', origin='1899-12-30', errors='coerce')
                    
                    # Normalizar para meia-noite (remover a parte do tempo)
                    df['Data Produção'] = df['Data Produção'].dt.normalize()
                    df['Data Alojamento'] = df['Data Alojamento'].dt.normalize()
                    
                    # Remover linhas onde as datas não puderam ser convertidas
                    df = df[df['Data Produção'].notna() & df['Data Alojamento'].notna()]
                    
                    # Converter para formato de string ISO para armazenamento correto em SQLite
                    df['Data Produção'] = df['Data Produção'].dt.strftime('%Y-%m-%d')
                    df['Data Alojamento'] = df['Data Alojamento'].dt.strftime('%Y-%m-%d')
                                      
                    # Converter colunas para string
                    df['Fornecedor'] = df['Fornecedor'].astype(str)
                    # Converter para inteiro e depois para string
                    df['Aviário'] = pd.to_numeric(df['Aviário'], errors='coerce').fillna(0).astype(int).astype(str)
                    df['Lote'] = pd.to_numeric(df['Lote'], errors='coerce').fillna(0).astype(int).astype(str)


                    # Concatenar Aviário e Lote para criar o campo Aviário-Lote, mantendo as colunas originais
                    df['Aviário-Lote'] = df['Aviário'] + '-' + df['Lote']
                    
                    # Calcular "Aves Efetivas" como a diferença entre "Cabeça" e "Mortos"
                    df['Aves Efetivas'] = df['Cabeça'] - df['Mortos']

                    # Garantir que não existam valores negativos (caso haja inconsistências nos dados)
                    df['Aves Efetivas'] = df['Aves Efetivas'].clip(lower=0)

                    # Converter para tipo inteiro para evitar decimais
                    df['Aves Efetivas'] = df['Aves Efetivas'].fillna(0).astype(int)
                    
                    # Substituir valores NaN e null por 0 nas colunas de artrite
                    artrite_cols = [
                        'Total - Artrite (1 articulação)',
                        'Total - Artrite (2 articulações)',
                        'Parcial - Artrite (1 articulação)',
                        'Parcial - Artrite (2 articulações)'
                    ]

                    # Substituir NaN e null por 0
                    for col in artrite_cols:
                        if col in df.columns:
                            df[col] = df[col].fillna(0)

                    # Converter para tipo numérico (inteiro)
                    df[artrite_cols] = df[artrite_cols].astype(int)
                    
                    # Calcular percentuais de artrite dividindo pela quantidade de 'Aves Efetivas'
                    for col in artrite_cols:
                        if col in df.columns:
                            # Evitar divisão por zero
                            df[f'{col} (%)'] = df.apply(
                                lambda x: (x[col] / x['Aves Efetivas'] * 100) if x['Aves Efetivas'] > 0 else 0, 
                                axis=1
                            ).round(2)

                    # Remover as colunas originais de contagem e manter apenas os percentuais
                    df = df.drop(columns=artrite_cols)

                    # Renomear as colunas de percentual para nomes mais simples
                    df = df.rename(columns={
                        'Total - Artrite (1 articulação) (%)': 'Total_Artrite_1_pct',
                        'Total - Artrite (2 articulações) (%)': 'Total_Artrite_2_pct',
                        'Parcial - Artrite (1 articulação) (%)': 'Parcial_Artrite_1_pct',
                        'Parcial - Artrite (2 articulações) (%)': 'Parcial_Artrite_2_pct'
                    })
                    
                    # Calcular o somatório dos percentuais de artrite
                    df['Artrite_Total_pct'] = df['Total_Artrite_1_pct'] + df['Total_Artrite_2_pct'] + \
                                              df['Parcial_Artrite_1_pct'] + df['Parcial_Artrite_2_pct']

                    # Arredondar o valor total para 2 casas decimais
                    df['Artrite_Total_pct'] = df['Artrite_Total_pct'].round(2)

                    # Remover linhas com dados inconsistentes ou nulos
                    df = df.dropna(subset=['Aviário-Lote', 'Data Produção', 'Data Alojamento'])
                    
                    # Criar uma coluna chamada 'Peso Médio' que é o peso dividido pelo número de aves efetivas, arredondamento de 3 casas decimais
                    if 'Peso' in df.columns and 'Cabeça' in df.columns:
                        # Deixar como NaN onde qualquer uma das colunas tem valores nulos
                        df['Peso Médio'] = df.apply(
                            lambda x: round(x['Peso'] / x['Cabeça'], 3) 
                            if pd.notnull(x['Peso']) and pd.notnull(x['Cabeça']) and x['Cabeça'] > 0 
                            else pd.NA, 
                            axis=1
                        )
                        # Remover linhas onde o peso médio é infinito (mas manter NaN)
                        df = df[~df['Peso Médio'].isin([float('inf'), float('-inf')])]
                    else:
                        print(f"Aviso: Colunas 'Peso' ou 'Cabeça' não encontradas em {file_name}. Peso Médio não será calculado.")
                        df['Peso Médio'] = None
                        
                    #conectar na base de dados e salvar os dados
                    df.to_sql('condena', conn, if_exists='append', index=False)
                    print(f"Dados de {file_name} importados para a tabela 'condena'")
                else:
                    print(f"Aba '{sheet_name}' não encontrada em {file_name}")
        except Exception as e:
            print(f"Erro ao processar {file_path}: {str(e)}")

    conn.close()
    print("Tabela 'condena' criada com sucesso.")

if __name__ == "__main__":
    # Importar planilhas Indicadores_Fomento_*
    import_xlsb_to_sqlite(input_files, output_db, sheet_name, columns)

    # Importar planilhas ProMOB_*
    promob_files = glob.glob(os.path.join(folder_path, 'ProMOB_*.xlsb'))
    import_promob_to_sqlite(promob_files, output_db, sheet_name='Dados')

    # Importar planilhas Painel_Condenações_*
    condena_files = glob.glob(os.path.join(folder_path, 'Painel_Condenações_*.xlsb'))
    import_condena_to_sqlite(condena_files, output_db, sheet_name='BD_Condenações')