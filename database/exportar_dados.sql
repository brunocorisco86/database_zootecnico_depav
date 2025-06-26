-- Criação da view vw_condena_resultados
DROP VIEW IF EXISTS vw_condena_resultados;

-- View para trazer os dados de condena e resultados
CREATE VIEW vw_condena_resultados AS
SELECT 
    c."Data Produção" AS Data_Abate,
    c."Data Alojamento" AS Data_Alojamento,
    c."Aviário-Lote" AS Lote_Composto,
    c."Aviário" AS Aviario,
    n."Número do Núcleo" AS Nucleo,
    c."Fornecedor" AS Fornecedor,
    c."Placa Caminhão" AS Placa,
    c."Aves Efetivas" AS Aves,
    ROUND(c."Peso Médio", 3) AS Peso_Medio,
    ROUND(c."Artrite_Total_pct", 2) AS Artrite_pct,
    r."Proprietario" AS Proprietário,
    r."Nome_Linhagem" AS Linhagem,
    r."Idade_Matriz" AS Idade_Matriz,
    r."Lista_matriz" AS Matriz,
    r."Fornecedor_Pinto" AS Fornecedor_Pintainho,
    r."CLASSIFICAÇÃO" AS Classificacao,
    r."Conversão_Alimentar" AS Conversao,
    r."Ano" AS ANO
FROM 
    condena c
JOIN 
    resultados r ON c."Aviário-Lote" = r."Número_Composto"
LEFT JOIN
    nucleos n ON c."Aviário" = n."Aviário";
    nucleos n ON c."Aviário" = n."Aviário";

-- Exportar os dados da view para CSV
.headers on
.mode csv
.output vw_condena_resultados.csv
SELECT * FROM vw_condena_resultados;
.output stdout
