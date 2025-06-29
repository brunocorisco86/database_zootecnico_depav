-- Criar uma tabela temporária com valores únicos, mantendo a primeira ocorrência
CREATE TABLE temp_promob AS
SELECT *
FROM promob
WHERE ROWID IN (
    SELECT MIN(ROWID)
    FROM promob
    GROUP BY "Aviário-Lote"
);

-- Excluir a tabela original
DROP TABLE promob;

-- Renomear a tabela temporária para o nome original
ALTER TABLE temp_promob RENAME TO promob;

-- Criar a view avg_nota_nucleo excluindo Núcleo = '0x2a'
CREATE VIEW avg_nota_nucleo AS
SELECT 
    p."Núcleo" AS Granja,
        n."Nome Proprietário" AS Proprietario,
        p.Ano,
        ROUND(AVG(p.Nota), 1) AS Media_Nota
FROM promob p
LEFT JOIN nucleos n ON p."Aviário" = n."Aviário"
WHERE CAST(p."Núcleo" AS TEXT) != '0x2a'
GROUP BY p."Núcleo", p.Ano
ORDER BY p."Núcleo", p.Ano;

-- View trazer os dados de condena e resultados

DROP VIEW IF EXISTS vw_condena_resultados;

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
    r."Mortalidade" AS Mortalidade,
    r."Ano" AS ANO
FROM 
    condena c
JOIN 
    resultados r ON c."Aviário-Lote" = r."Número_Composto"
LEFT JOIN
    nucleos n ON c."Aviário" = n."Aviário";
