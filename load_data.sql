\set ON_ERROR_STOP on
SET search_path TO week5_mtsamples, public;
\cd data

\copy medical_specialty (specialty_id, specialty_name, specialty_category) FROM 'MedicalSpecialty.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy note_type (note_type_id, note_type_name, is_inferred) FROM 'NoteType.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy data_source (source_id, source_name, source_url) FROM 'DataSource.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy clinical_note (note_id, source_row_id, specialty_id, note_type_id, source_id, sample_name, description_or_chief_concern, source_word_count) FROM 'ClinicalNote.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy note_text (note_id, transcription_text, character_length, recount_words, deid_status) FROM 'NoteText.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy keyword (keyword_id, keyword_term) FROM 'Keyword.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy note_keyword (note_id, keyword_id, keyword_position) FROM 'NoteKeyword.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy note_section (section_id, note_id, section_order, section_header, section_text) FROM 'NoteSection.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

\cd ..
