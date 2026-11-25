\set ON_ERROR_STOP on
SET search_path TO week5_mtsamples, public;

-- Query 1: How many sampled notes are recorded under each label/category?
SELECT s.specialty_name, s.specialty_category, count(n.note_id) AS note_count
FROM medical_specialty AS s
LEFT JOIN clinical_note AS n ON n.specialty_id = s.specialty_id
GROUP BY s.specialty_id, s.specialty_name, s.specialty_category
ORDER BY s.specialty_category, note_count DESC, s.specialty_name;

-- Query 2: What is the average transcription length for each true clinical specialty?
SELECT s.specialty_name,
       count(n.note_id) AS note_count,
       round(avg(t.recount_words), 1) AS average_words
FROM medical_specialty AS s
JOIN clinical_note AS n ON n.specialty_id = s.specialty_id
JOIN note_text AS t ON t.note_id = n.note_id
WHERE s.specialty_category = 'Clinical specialty'
GROUP BY s.specialty_id, s.specialty_name
ORDER BY average_words DESC;

-- Query 3: Which normalized keywords occur in the greatest number of distinct notes?
SELECT k.keyword_term, count(DISTINCT nk.note_id) AS note_frequency
FROM keyword AS k
JOIN note_keyword AS nk ON nk.keyword_id = k.keyword_id
GROUP BY k.keyword_id, k.keyword_term
ORDER BY note_frequency DESC, k.keyword_term
LIMIT 20;

-- Query 4: Which sampled notes have a transcription longer than 500 recounted words?
SELECT n.note_id, s.specialty_name, n.sample_name, t.recount_words
FROM clinical_note AS n
JOIN medical_specialty AS s ON s.specialty_id = n.specialty_id
JOIN note_text AS t ON t.note_id = n.note_id
WHERE t.recount_words > 500
ORDER BY t.recount_words DESC, n.note_id;

-- Query 5: How are inferred note types distributed across specialty labels?
SELECT s.specialty_name, nt.note_type_name, count(n.note_id) AS note_count
FROM medical_specialty AS s
JOIN clinical_note AS n ON n.specialty_id = s.specialty_id
JOIN note_type AS nt ON nt.note_type_id = n.note_type_id
GROUP BY s.specialty_id, s.specialty_name, nt.note_type_id, nt.note_type_name
ORDER BY s.specialty_name, note_count DESC, nt.note_type_name;

-- Analytics-ready output: a row per specialty label for direct charting/export.
SELECT specialty_name, specialty_category, note_count,
       average_transcription_words, average_transcription_characters,
       shortest_transcription_words, longest_transcription_words
FROM v_specialty_analytics
ORDER BY specialty_category, specialty_name;

-- Export the dashboard-ready dataset when running with psql from this folder:
\copy (SELECT s.specialty_name, s.specialty_category, count(n.note_id) AS note_count FROM medical_specialty AS s LEFT JOIN clinical_note AS n ON n.specialty_id = s.specialty_id GROUP BY s.specialty_id, s.specialty_name, s.specialty_category ORDER BY s.specialty_category, note_count DESC, s.specialty_name) TO 'results/query1_specialty_note_counts.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy (SELECT s.specialty_name, count(n.note_id) AS note_count, round(avg(t.recount_words), 1) AS average_words FROM medical_specialty AS s JOIN clinical_note AS n ON n.specialty_id = s.specialty_id JOIN note_text AS t ON t.note_id = n.note_id WHERE s.specialty_category = 'Clinical specialty' GROUP BY s.specialty_id, s.specialty_name ORDER BY average_words DESC) TO 'results/query2_average_words_by_specialty.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy (SELECT k.keyword_term, count(DISTINCT nk.note_id) AS note_frequency FROM keyword AS k JOIN note_keyword AS nk ON nk.keyword_id = k.keyword_id GROUP BY k.keyword_id, k.keyword_term ORDER BY note_frequency DESC, k.keyword_term LIMIT 20) TO 'results/query3_top_keywords.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy (SELECT n.note_id, s.specialty_name, n.sample_name, t.recount_words FROM clinical_note AS n JOIN medical_specialty AS s ON s.specialty_id = n.specialty_id JOIN note_text AS t ON t.note_id = n.note_id WHERE t.recount_words > 500 ORDER BY t.recount_words DESC, n.note_id) TO 'results/query4_long_transcriptions.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy (SELECT s.specialty_name, nt.note_type_name, count(n.note_id) AS note_count FROM medical_specialty AS s JOIN clinical_note AS n ON n.specialty_id = s.specialty_id JOIN note_type AS nt ON nt.note_type_id = n.note_type_id GROUP BY s.specialty_id, s.specialty_name, nt.note_type_id, nt.note_type_name ORDER BY s.specialty_name, note_count DESC, nt.note_type_name) TO 'results/query5_note_types_by_specialty.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy (SELECT specialty_name, specialty_category, note_count, average_transcription_words, average_transcription_characters, shortest_transcription_words, longest_transcription_words FROM v_specialty_analytics ORDER BY specialty_category, specialty_name) TO 'results/analytics_ready_specialty.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy (SELECT s.specialty_name, s.specialty_category, nt.note_type_name, count(n.note_id) AS note_count FROM medical_specialty AS s JOIN clinical_note AS n ON n.specialty_id = s.specialty_id JOIN note_type AS nt ON nt.note_type_id = n.note_type_id GROUP BY s.specialty_id, s.specialty_name, s.specialty_category, nt.note_type_id, nt.note_type_name ORDER BY s.specialty_name, nt.note_type_name) TO 'results/specialty_note_type_counts.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
