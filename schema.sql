CREATE SCHEMA week5_mtsamples;
SET search_path TO week5_mtsamples, public;

CREATE TABLE medical_specialty (
    specialty_id smallint PRIMARY KEY,
    specialty_name varchar(120) NOT NULL UNIQUE,
    specialty_category varchar(32) NOT NULL
        CHECK (specialty_category IN ('Clinical specialty', 'Document-type grouping'))
);

CREATE TABLE note_type (
    note_type_id smallint PRIMARY KEY,
    note_type_name varchar(80) NOT NULL UNIQUE,
    is_inferred boolean NOT NULL
);

CREATE TABLE data_source (
    source_id smallint PRIMARY KEY,
    source_name text NOT NULL,
    source_url text NOT NULL
);

CREATE TABLE clinical_note (
    note_id varchar(10) PRIMARY KEY,
    source_row_id integer NOT NULL UNIQUE,
    specialty_id smallint NOT NULL REFERENCES medical_specialty(specialty_id),
    note_type_id smallint NOT NULL REFERENCES note_type(note_type_id),
    source_id smallint NOT NULL REFERENCES data_source(source_id),
    sample_name text NOT NULL,
    description_or_chief_concern text NOT NULL,
    source_word_count integer NOT NULL CHECK (source_word_count >= 0)
);

CREATE TABLE note_text (
    note_id varchar(10) PRIMARY KEY REFERENCES clinical_note(note_id) ON DELETE CASCADE,
    transcription_text text NOT NULL,
    character_length integer NOT NULL CHECK (character_length >= 0),
    recount_words integer NOT NULL CHECK (recount_words >= 0),
    deid_status varchar(40) NOT NULL
);

CREATE TABLE keyword (
    keyword_id integer PRIMARY KEY,
    keyword_term text NOT NULL UNIQUE CHECK (btrim(keyword_term) <> '')
);

CREATE TABLE note_keyword (
    note_id varchar(10) NOT NULL REFERENCES clinical_note(note_id) ON DELETE CASCADE,
    keyword_id integer NOT NULL REFERENCES keyword(keyword_id),
    keyword_position smallint NOT NULL CHECK (keyword_position > 0),
    PRIMARY KEY (note_id, keyword_id)
);

CREATE TABLE note_section (
    section_id integer PRIMARY KEY,
    note_id varchar(10) NOT NULL REFERENCES clinical_note(note_id) ON DELETE CASCADE,
    section_order smallint NOT NULL CHECK (section_order > 0),
    section_header text NOT NULL,
    section_text text,
    UNIQUE (note_id, section_order)
);

CREATE INDEX clinical_note_specialty_idx ON clinical_note(specialty_id);
CREATE INDEX clinical_note_type_idx ON clinical_note(note_type_id);
CREATE INDEX note_keyword_keyword_idx ON note_keyword(keyword_id);
CREATE INDEX note_section_note_idx ON note_section(note_id);
CREATE INDEX note_text_transcription_fts_idx
    ON note_text USING gin (to_tsvector('english', transcription_text));

CREATE VIEW v_specialty_analytics AS
SELECT
    s.specialty_id,
    s.specialty_name,
    s.specialty_category,
    count(n.note_id)::integer AS note_count,
    round(avg(t.recount_words), 1) AS average_transcription_words,
    round(avg(t.character_length), 1) AS average_transcription_characters,
    min(t.recount_words)::integer AS shortest_transcription_words,
    max(t.recount_words)::integer AS longest_transcription_words
FROM medical_specialty AS s
LEFT JOIN clinical_note AS n ON n.specialty_id = s.specialty_id
LEFT JOIN note_text AS t ON t.note_id = n.note_id
GROUP BY s.specialty_id, s.specialty_name, s.specialty_category;

CREATE VIEW v_specialty_keyword_frequency AS
SELECT
    s.specialty_name,
    k.keyword_term,
    count(DISTINCT n.note_id)::integer AS note_frequency
FROM medical_specialty AS s
JOIN clinical_note AS n ON n.specialty_id = s.specialty_id
JOIN note_keyword AS nk ON nk.note_id = n.note_id
JOIN keyword AS k ON k.keyword_id = nk.keyword_id
GROUP BY s.specialty_name, k.keyword_id, k.keyword_term;
