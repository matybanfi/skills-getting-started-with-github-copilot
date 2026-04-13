-- Oracle DDL script: Create DIPENDENTI (employees) table
-- Columns: nome, cognome, data_di_nascita, data_inizio_lavoro

CREATE TABLE DIPENDENTI (
    id                NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome              VARCHAR2(100)  NOT NULL,
    cognome           VARCHAR2(100)  NOT NULL,
    data_di_nascita   DATE           NOT NULL,
    data_inizio_lavoro DATE          NOT NULL
);

-- Index on cognome for fast lookups
CREATE INDEX idx_dipendenti_cognome ON DIPENDENTI (cognome);

COMMENT ON TABLE  DIPENDENTI                       IS 'Anagrafica dipendenti con date utili al calcolo pensionistico';
COMMENT ON COLUMN DIPENDENTI.nome                  IS 'Nome del dipendente';
COMMENT ON COLUMN DIPENDENTI.cognome               IS 'Cognome del dipendente';
COMMENT ON COLUMN DIPENDENTI.data_di_nascita       IS 'Data di nascita del dipendente';
COMMENT ON COLUMN DIPENDENTI.data_inizio_lavoro    IS 'Data di inizio del rapporto lavorativo';
