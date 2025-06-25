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
    p.Ano,
    AVG(p.Nota) AS Media_Nota
FROM promob p
LEFT JOIN nucleos n ON p."Aviário" = n."Aviário"
WHERE CAST(p."Núcleo" AS TEXT) != '0x2a'
GROUP BY p."Núcleo", p.Ano
ORDER BY p."Núcleo", p.Ano;
