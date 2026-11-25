\set ON_ERROR_STOP on
SET search_path TO week5_mtsamples, public;

DO $$
BEGIN
    IF (SELECT count(*) FROM clinical_note) < 30 THEN
        RAISE EXCEPTION 'Minimum 30 clinical notes was not met';
    END IF;
    IF (SELECT count(*) FROM medical_specialty WHERE specialty_category = 'Clinical specialty') < 5 THEN
        RAISE EXCEPTION 'Minimum five clinical specialties was not met';
    END IF;
    IF (SELECT count(*) FROM keyword) < 20 THEN
        RAISE EXCEPTION 'Minimum 20 keywords was not met';
    END IF;
    IF EXISTS (
        SELECT 1
        FROM clinical_note AS n
        LEFT JOIN note_text AS t ON t.note_id = n.note_id
        WHERE t.note_id IS NULL
    ) THEN
        RAISE EXCEPTION 'A clinical note has no NoteText record';
    END IF;
    IF EXISTS (
        SELECT 1
        FROM note_keyword AS nk
        JOIN keyword AS k ON k.keyword_id = nk.keyword_id
        JOIN medical_specialty AS s
          ON lower(btrim(k.keyword_term)) = lower(btrim(s.specialty_name))
    ) THEN
        RAISE EXCEPTION 'A specialty label remains in the keyword bridge';
    END IF;
END
$$;

SELECT 'medical_specialty' AS table_name, count(*) AS row_count FROM medical_specialty
UNION ALL SELECT 'note_type', count(*) FROM note_type
UNION ALL SELECT 'data_source', count(*) FROM data_source
UNION ALL SELECT 'clinical_note', count(*) FROM clinical_note
UNION ALL SELECT 'note_text', count(*) FROM note_text
UNION ALL SELECT 'keyword', count(*) FROM keyword
UNION ALL SELECT 'note_keyword', count(*) FROM note_keyword
UNION ALL SELECT 'note_section', count(*) FROM note_section
ORDER BY table_name;

SELECT
    count(*) FILTER (WHERE section_text IS NULL) AS empty_section_bodies,
    count(*) AS total_sections
FROM note_section;
