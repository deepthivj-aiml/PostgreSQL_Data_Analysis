\set ON_ERROR_STOP on
\pset pager off
\pset border 2
\pset null '[NULL]'
SET search_path TO week5_mtsamples, public;

\echo 'SCREENSHOT 1 - Tables created in PostgreSQL'
\dt week5_mtsamples.*
\prompt 'Capture the table list, then press Enter to continue: ' evidence_continue

\echo 'SCREENSHOT 2 - ClinicalNote keys, columns, and constraints'
\d+ week5_mtsamples.clinical_note
\prompt 'Capture the ClinicalNote definition, then press Enter to continue: ' evidence_continue

\echo 'SCREENSHOT 3 - NoteKeyword bridge primary and foreign keys'
\d+ week5_mtsamples.note_keyword
\prompt 'Capture the bridge table definition, then press Enter to continue: ' evidence_continue

\echo 'SCREENSHOT 4 - Row counts and validation checks'
\i validate.sql
\prompt 'Capture the validation output, then press Enter to continue: ' evidence_continue

\echo 'SCREENSHOT 5 - Query 1: notes by specialty label'
SELECT s.specialty_name, s.specialty_category, count(n.note_id) AS note_count
FROM medical_specialty AS s
LEFT JOIN clinical_note AS n ON n.specialty_id = s.specialty_id
GROUP BY s.specialty_id, s.specialty_name, s.specialty_category
ORDER BY s.specialty_category, note_count DESC, s.specialty_name;
\prompt 'Capture Query 1, then press Enter to continue: ' evidence_continue

\echo 'SCREENSHOT 6 - Query 2: average transcription length by clinical specialty'
SELECT s.specialty_name,
       count(n.note_id) AS note_count,
       round(avg(t.recount_words), 1) AS average_words
FROM medical_specialty AS s
JOIN clinical_note AS n ON n.specialty_id = s.specialty_id
JOIN note_text AS t ON t.note_id = n.note_id
WHERE s.specialty_category = 'Clinical specialty'
GROUP BY s.specialty_id, s.specialty_name
ORDER BY average_words DESC;
\prompt 'Capture Query 2, then press Enter to continue: ' evidence_continue

\echo 'SCREENSHOT 7 - Query 3: top 20 normalized keywords'
SELECT k.keyword_term, count(DISTINCT nk.note_id) AS note_frequency
FROM keyword AS k
JOIN note_keyword AS nk ON nk.keyword_id = k.keyword_id
GROUP BY k.keyword_id, k.keyword_term
ORDER BY note_frequency DESC, k.keyword_term
LIMIT 20;
\prompt 'Capture Query 3, then press Enter to continue: ' evidence_continue

\echo 'SCREENSHOT 8 - Query 4: notes over 500 recounted words'
SELECT n.note_id, s.specialty_name, n.sample_name, t.recount_words
FROM clinical_note AS n
JOIN medical_specialty AS s ON s.specialty_id = n.specialty_id
JOIN note_text AS t ON t.note_id = n.note_id
WHERE t.recount_words > 500
ORDER BY t.recount_words DESC, n.note_id;
\prompt 'Capture Query 4, then press Enter to continue: ' evidence_continue

\echo 'SCREENSHOT 9 - Query 5: note type counts by specialty label'
SELECT s.specialty_name, nt.note_type_name, count(n.note_id) AS note_count
FROM medical_specialty AS s
JOIN clinical_note AS n ON n.specialty_id = s.specialty_id
JOIN note_type AS nt ON nt.note_type_id = n.note_type_id
GROUP BY s.specialty_id, s.specialty_name, nt.note_type_id, nt.note_type_name
ORDER BY s.specialty_name, note_count DESC, nt.note_type_name;
\prompt 'Capture Query 5, then press Enter to continue: ' evidence_continue

\echo 'SCREENSHOT 10 - Final analytics-ready view'
SELECT specialty_name, specialty_category, note_count,
       average_transcription_words, average_transcription_characters,
       shortest_transcription_words, longest_transcription_words
FROM v_specialty_analytics
ORDER BY specialty_category, specialty_name;
\prompt 'Capture the analytics-ready output, then press Enter to finish: ' evidence_continue

\echo 'Evidence output sequence complete.'
