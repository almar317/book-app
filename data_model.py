import sqlite3
import math
from werkzeug.security import generate_password_hash, check_password_hash

DBFILENAME = 'books.sqlite'

# Fonctions utilitaires pour les requêtes SQL

def db_fetch(query, args=(), all=False, db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row  # pour accéder aux colonnes par nom
        cur = conn.execute(query, args)
        if all:
            res = cur.fetchall()
            if res:
                res = [dict(row) for row in res]
            else:
                res = []
        else:
            res = cur.fetchone()
            if res:
                res = dict(res)
    return res

def db_insert(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.lastrowid

def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()

# Gestion des livres

def read(id):
    return db_fetch('SELECT * FROM books WHERE id = ?', (id,))

def delete(id):
    db_run('DELETE FROM books WHERE id = ?', (id,))

def search(query="", page=1):
    num_per_page = 32
    query_str = '%' + query + '%'
    res = db_fetch('SELECT count(*) FROM books WHERE title LIKE ? OR author LIKE ? OR library LIKE ? OR genre LIKE ?',
                   (query_str, query_str, query_str, query_str))
    num_found = res['count(*)']
    results = db_fetch('SELECT id as entry, title, img FROM books WHERE title LIKE ? OR author LIKE ? OR library LIKE ? OR genre LIKE ? ORDER BY id LIMIT ? OFFSET ?',
                       (query_str, query_str, query_str, query_str, num_per_page, (page - 1) * num_per_page), all=True)
    return {
        'results': results,
        'num_found': num_found, 
        'query': query,
        'next_page': page + 1,
        'page': page,
        'num_pages': math.ceil(float(num_found) / float(num_per_page))
    }

def books_by_genre(genre, page=1):
    num_per_page = 32
    results = db_fetch('SELECT id as entry, title, img FROM books WHERE genre = ? ORDER BY id LIMIT ? OFFSET ?',
                       (genre, num_per_page, (page - 1) * num_per_page), all=True)
    num_found = len(results)
    return {
        'results': results,
        'num_found': num_found,
        'query': genre,
        'next_page': page + 1,
        'page': page,
        'num_pages': math.ceil(float(num_found) / float(num_per_page))
    }

def books_by_library(library, page=1):
    num_per_page = 20
    results = db_fetch('SELECT id as entry, title, img FROM books WHERE library = ? ORDER BY id LIMIT ? OFFSET ?',
                       (library, num_per_page, (page - 1) * num_per_page), all=True)
    num_found = len(results)
    return {
        'results': results,
        'num_found': num_found,
        'query': library,
        'next_page': page + 1,
        'page': page,
        'num_pages': math.ceil(float(num_found) / float(num_per_page))
    }

def get_book_details(book_id):
    return db_fetch("SELECT * FROM books WHERE id = ?", (book_id,))

# Gestion des favoris

def add_to_favorites(user_id, book_id):
    db_run('INSERT INTO favorites (user_id, book_id) VALUES (?, ?)', (user_id, book_id))

def remove_from_favorites(user_id, book_id):
    db_run('DELETE FROM favorites WHERE user_id = ? AND book_id = ?', (user_id, book_id))

def get_favorite_books(user_id):
    query = """
    SELECT books.id, books.title, books.author, books.price, books.img
    FROM favorites
    INNER JOIN books ON favorites.book_id = books.id
    WHERE favorites.user_id = ?
    """
    return db_fetch(query, (user_id,), all=True)

def read_favorite(user_id, book_id):
    try:
        query = "SELECT * FROM favorites WHERE user_id = ? AND book_id = ?"
        favorite = db_fetch(query, (user_id, book_id))
        if favorite:
            book_details = get_book_details(book_id)
            favorite['book_details'] = book_details
        return favorite
    except Exception as e:
        print("Error reading favorite:", e)
        return None

# Gestion des utilisateurs

def login(username, password):
    result = db_fetch('SELECT id, password_hash FROM users WHERE name = ?', (username,))
    if result is None:
        return -1
    elif not check_password_hash(result['password_hash'], password):
        return -1
    else:
        return result['id']

def new_user(username, password):
    if user_exists(username):
        return -1
    else:
        password_hash = generate_password_hash(password)
        return db_insert('INSERT INTO users (name, password_hash) VALUES (?, ?)', (username, password_hash))

def user_exists(username):
    result = db_fetch('SELECT COUNT(*) FROM users WHERE name = ?', (username,))
    if result:
        return result['COUNT(*)'] > 0  # Vérifie si le compte existe
    else:
        return False  # Retourne False si aucune donnée n'a été renvoyée

def add_to_cart(user_id, book_id):
    try:
        db_run('INSERT INTO cart (user_id, book_id) VALUES (?, ?)', (user_id, book_id))
        return True  # Indique que le livre a été ajouté avec succès au panier
    except Exception as e:
        print("Error adding book to cart:", e)
        return False  # Indique qu'une erreur s'est produite lors de l'ajout au panier

def remove_from_cart(user_id, book_id):
    try:
        db_run('DELETE FROM cart WHERE user_id = ? AND book_id = ?', (user_id, book_id))
    except Exception as e:
        print("Error removing book from cart:", e)

def get_cart_items(user_id):
    query = """
    SELECT books.id, books.title, books.author, books.price, books.img
    FROM cart
    INNER JOIN books ON cart.book_id = books.id
    WHERE cart.user_id = ?
    """
    return db_fetch(query, (user_id,), all=True)

def add_reservation(user_id, book_id):
    try:
        db_run('INSERT INTO reservations (user_id, book_id) VALUES (?, ?)', (user_id, book_id))
        return True
    except Exception as e:
        print("Error adding reservation:", e)
        return False

def get_user_reservations(user_id):
    query = """
    SELECT reservations.id as reservation_id, books.id as book_id, books.title, books.author, books.img
    FROM reservations
    INNER JOIN books ON reservations.book_id = books.id
    WHERE reservations.user_id = ?
    """
    return db_fetch(query, (user_id,), all=True)


def remove_reservation(reservation_id, user_id):
    try:
        with sqlite3.connect(DBFILENAME) as conn:
            cursor = conn.execute(
                'DELETE FROM reservations WHERE id = ? AND user_id = ?',
                (reservation_id, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print("Erreur suppression :", e)
        return False



def get_book(book_id):
    try:
        query = "SELECT * FROM books WHERE id = ?"
        result = db_fetch(query, (book_id,), one=True)
        if result:
            # Si le livre est trouvé dans la base de données, retournez ses informations
            book = {
                'id': result[0],
                'title': result[1],
                'author': result[2],
                'img': result[3]  # Assurez-vous que la colonne contenant l'URL de l'image est correcte
            }
            return book
        else:
            # Si le livre n'est pas trouvé, retournez None
            return None
    except Exception as e:
        print("Error fetching book:", e)
        return None

