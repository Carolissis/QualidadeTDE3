import sqlite3

conn = sqlite3.connect('nc_database.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS nc_database (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    responsavel TEXT NOT NULL,
    impacto TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Aberta',
    aplicavel TEXT NOT NULL CHECK (aplicavel IN ('Sim', 'Não'))
)
''')

conn.commit()
conn.close()