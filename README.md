# Repositório de Análise de Dados de Produção Avícola

Este repositório contém scripts e notebooks Jupyter para análise de dados relacionados à produção avícola. O objetivo principal é realizar a Análise Exploratória de Dados (EDA) e consolidar informações de diversas fontes de dados em formato de planilha Excel.

## Estrutura do Repositório

- **`database/`**: Contém os notebooks Jupyter, scripts Python e SQL para processamento e análise dos dados.
    - **`EDA_Planilha_mestra.ipynb`**: Notebook para análise exploratória do arquivo `PLANILHA_MESTRA.xlsx`. Foca na extração e visualização de dados cadastrais de aviários, proprietários e informações relacionadas.
    - **`EDA_Promob.ipynb`**: Notebook para análise exploratória do arquivo `ProMOB_2022.xlsb`. Analisa dados de lotes, avaliações, notas de conformidade e informações de técnicos. Tenta também processar dados do arquivo `Indicadores Fomento_2025.xlsb` e armazená-los em um banco de dados SQLite (`fomento_data.db`).
    - **`EDA_indicadores fomento.ipynb`**: Notebook dedicado à análise do arquivo `Indicadores_Fomento_2025.xlsb`, com foco nos resultados de lotes, conversão alimentar e classificações.
    - **`extrator_dados_indicadores.py`**: Script Python responsável por automatizar a extração, transformação e carregamento (ETL) de dados de várias planilhas Excel (`Indicadores_Fomento_*.xlsb`, `PLANILHA_MESTRA.xlsx`, `ProMOB_*.xlsb`) para um banco de dados SQLite centralizado chamado `resultado_lotes.db`. O script limpa os dados, extrai informações relevantes como o ano a partir do nome dos arquivos, converte tipos de dados e estrutura as informações em tabelas (`resultados`, `nucleos`, `promob`).
    - **`tratamento_dados.sql`**: Script SQL que realiza o pós-processamento dos dados no banco de dados `resultado_lotes.db` (criado pelo `extrator_dados_indicadores.py`). Suas principais funções são:
        - Remover registros duplicados da tabela `promob` com base na coluna `"Aviário-Lote"`.
        - Criar uma view chamada `avg_nota_nucleo` que calcula a média das notas (`Nota`) da tabela `promob`, agrupada por núcleo (granja) e ano, juntando informações do proprietário da tabela `nucleos` e excluindo entradas específicas.

## Arquivos de Dados (Não incluídos no repositório)

Os seguintes arquivos Excel são utilizados pelos notebooks e scripts:

- `PLANILHA_MESTRA.xlsx`
- `ProMOB_2022.xlsb` (e outros arquivos `ProMOB_*.xlsb`)
- `Indicadores_Fomento_2025.xlsb` (e outros arquivos `Indicadores_Fomento_*.xlsb`)

## Banco de Dados Gerado

- **`resultado_lotes.db`**: Banco de dados SQLite gerado pelo `extrator_dados_indicadores.py` e modificado pelo `tratamento_dados.sql`. Contém as tabelas:
    - `resultados`: Dados consolidados dos arquivos `Indicadores_Fomento_*.xlsb`.
    - `nucleos`: Dados cadastrais da `PLANILHA_MESTRA.xlsx`.
    - `promob`: Dados consolidados dos arquivos `ProMOB_*.xlsb`.
    - `avg_nota_nucleo` (view): Visão com a média de notas por granja e ano.

## Como Usar

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DO_REPOSITORIO>
    ```
2.  **Ambiente:**
    - Recomenda-se o uso de um ambiente virtual Python.
    - Instale as bibliotecas Python necessárias. Principalmente `pandas`, `jupyter`, `openpyxl` e `pyxlsb`:
      ```bash
      pip install pandas jupyter openpyxl pyxlsb
      ```
3.  **Coloque os Arquivos de Dados:**
    - Certifique-se de que os arquivos Excel mencionados (`PLANILHA_MESTRA.xlsx`, `ProMOB_*.xlsb`, `Indicadores_Fomento_*.xlsb`) estejam presentes na pasta `database/` ou ajuste os caminhos no script `extrator_dados_indicadores.py` (variável `folder_path`).
4.  **Execute o Script de Extração:**
    - Navegue até a pasta `database`.
    - Execute o script Python para popular o banco de dados:
      ```bash
      python extrator_dados_indicadores.py
      ```
5.  **Execute o Script SQL (Opcional/Verificação):**
    - Você pode executar o script `tratamento_dados.sql` usando uma ferramenta de gerenciamento de SQLite (como DB Browser for SQLite) conectada ao banco `resultado_lotes.db` para aplicar as transformações ou verificar sua lógica. O script Python já executa a lógica de criação das tabelas `resultados`, `nucleos` e `promob`. O SQL foca na limpeza de `promob` e criação da view.
6.  **Execute os Notebooks Jupyter:**
    - Na pasta `database`, inicie o Jupyter Notebook:
      ```bash
      jupyter notebook
      ```
    - Abra os arquivos `.ipynb` desejados e execute as células para análise exploratória. Os notebooks podem precisar de ajustes para ler diretamente do banco de dados `resultado_lotes.db` ou dos arquivos Excel, dependendo de sua configuração atual.

**Observação:** Os notebooks Jupyter (`EDA_*.ipynb`) podem ter sido criados para ler diretamente dos arquivos Excel. Para utilizá-los com o banco de dados consolidado `resultado_lotes.db`, pode ser necessário adaptar o código de leitura de dados dentro dos notebooks para consultarem o banco SQLite.
