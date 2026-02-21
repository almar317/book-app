import sqlite3
import json

JSONFILENAME = 'books.json'
DBFILENAME = 'books.sqlite'

# Fonction utilitaire pour exécuter des requêtes SQL
def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.rowcount

# Fonction pour exécuter une requête SQL de sélection
def select_books(limit=5):
    query = 'SELECT * FROM books LIMIT ?'
    with sqlite3.connect(DBFILENAME) as conn:
        cur = conn.cursor()
        cur.execute(query, (limit,))
        rows = cur.fetchall()
        for row in rows:
            print(row)




# Fonction pour charger les données à partir du fichier JSON dans la base de données SQLite
def load(fname=JSONFILENAME, db_name=DBFILENAME):
    # Supprimer les tables existantes
    db_run('DROP TABLE IF EXISTS books')
    db_run('DROP TABLE IF EXISTS users')
    db_run('DROP TABLE IF EXISTS favorites')
    db_run('DROP TABLE IF EXISTS reservations')
    db_run('DROP TABLE IF EXISTS cart')

    # Créer les tables
    db_run('''CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        img TEXT,
        title TEXT,
        author TEXT,
        summary TEXT,
        publisher TEXT,
        price REAL,
        genre TEXT,
        library TEXT,
        address TEXT,
        code_postal TEXT,
        arrondissement TEXT
    )''')

    db_run('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        password_hash TEXT
    )''')
    db_run('''
    CREATE TABLE favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        img TEXT,  -- Ajout de la colonne img pour stocker l'URL de l'image
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )''')


    db_run('''CREATE TABLE reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        img TEXT,  -- Ajout de la colonne img pour stocker l'URL de l'image
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )''')

    db_run('''CREATE TABLE cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        img TEXT,  -- Ajout de la colonne img pour stocker l'URL de l'image
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )''')

    # Insérer les données à partir du fichier JSON dans la table "books"
    insert_book = '''INSERT INTO books (
        img, title, author, summary, publisher, price, genre, library, address, code_postal, arrondissement
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

    with open(fname, 'r', encoding='utf-8') as fh:
        books = json.load(fh)
        for book in books:
            db_run(insert_book, (
                book['img'], book['title'], book['author'], book['summary'], 
                book['publisher'], book['price'], book['genre'], book['library'], 
                book['address'], book['code_postal'], book['arrondissement']
            ))

# Appeler la fonction load() pour charger les données dans la base de données SQLite
load()
