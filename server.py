from flask import Flask, session, Response, request, redirect, url_for, render_template, flash, abort
import data_model as model
from functools import wraps
from data_model import (
    read_favorite, get_favorite_books, remove_from_favorites, add_to_favorites,
    get_book_details, books_by_genre, books_by_library, read, search, new_user,
    login, user_exists, add_to_cart, remove_from_cart, get_cart_items,
    add_reservation, get_user_reservations, remove_reservation, get_book
)

app = Flask(__name__)

# Generate your own secret key, e.g. by running :
#    python -c 'import secrets; print(secrets.token_hex())'
# in a terminal
# This is used to sign encrypted cookies
app.secret_key = b'f8123ef1cd67d4e47a9dfc079354dcd760ee40e602845785d941e360617db7cd'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not('user_id' in session):
            return Response("Veuillez vous connecter pour accéder à cette ressource",
                            status=401)
        else:
            return f(*args, **kwargs)
    return decorated_function

@app.post('/login')
def login_post():
    username = request.form['user']
    password = request.form['password']
    if user_exists(username):
        user_id = model.login(username, password)
        if user_id != -1:
            session['user_id'] = user_id
            session['user_name'] = username
            return redirect(url_for('home'))
    # Si l'utilisateur n'existe pas ou les informations d'identification sont incorrectes,
    # redirigez-le vers la page d'inscription
    return redirect(url_for('sign_up_form'))



@app.post('/new_user')
def new_user_post():
    user_id = new_user(request.form['user'], request.form['password'])
    if user_id != -1:
        session['user_id'] = user_id
        session['user_name'] = request.form['user']
        return redirect(url_for('successful_registration'))  # Redirection vers successful_registration.html
    else:
        return redirect(url_for('existing_user'))  # Redirection vers existing_user.html en cas d'utilisateur existant


@app.route('/existing_user')
def existing_user():
    return render_template('existing_user.html')


@app.route('/successful_registration')
def successful_registration():
    return render_template('successful_registration.html')




@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = model.login(request.form['user'], request.form['password'])
        if user_id != -1:
            session['user_id'] = user_id
            session['user_name'] = request.form['user']
            return redirect(url_for('home'))
        else:
            # Rediriger vers la page de création de compte si l'utilisateur n'existe pas
            return redirect(url_for('sign_up_form'))
    else:
        # Afficher le formulaire de connexion
        return render_template('login.html')

@app.get('/login')
def login_form():
    if not user_exists(request.args.get('user')):
        return redirect(url_for('sign_up_form'))
    else:
        return render_template('login.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Traitement des données du formulaire si nécessaire
        return redirect(url_for('new_user_form'))
    else:
        # Afficher le formulaire d'inscription
        return render_template('sign_up.html')

@app.get('/sign_up')
def sign_up_form():
    return render_template('sign_up.html')



@app.get('/new_user')
def new_user_form():
    return render_template('new_user.html')


########################################
# Routes des pages principales du site #
########################################

# Retourne une page principale avec le nombre de recettes
@app.get('/')
def home():
    return render_template('header.html')


# Retourne les résultats de la recherche à partir de la requête "query"
@app.get('/search')
def search():
    if 'page' in request.args:
        page = int(request.args["page"])
    else:
        page = 1
    if 'query' in request.args:
        query = request.args["query"]
    else:
        query = ""
    found = model.search(query, page)
    return render_template('search_book.html', found=found)


@app.route('/genre/<genre>')
def genre_books(genre):
    page = int(request.args.get('page', 1))
    books = model.books_by_genre(genre, page)
    return render_template('genre_books.html', books=books)


@app.route('/library/<library>')
def library_books(library):
    page = int(request.args.get('page', 1))
    books = model.books_by_library(library, page)
    return render_template('library_books.html', books=books)


@app.get('/read/<id>')
def read(id):
    book = model.read(int(id))
    return render_template('book_details.html', book=book)


@app.route('/book_details/<book_id>')
def book_details(book_id):
    # Récupérer les détails du livre à partir de l'ID du livre
    book = model.get_book_details(book_id)
    if book:
        return render_template('book_details.html', book=book)
    else:
        return render_template('error.html')


@app.route('/read/<id>', methods=['GET', 'POST'])
def read_book(id):
    if request.method == 'POST':
        user_id = session.get('user_id')
        if user_id is None:
            return "Vous devez être connecté pour ajouter un livre aux favoris."

        # Ajouter le livre aux favoris en utilisant la fonction importée
        add_to_favorites(user_id, id)  # Utilisation de l'ID du livre passé dans la route
        return "Livre ajouté aux favoris avec succès"
    else:
        # Lire le livre à partir de la fonction read_favorite
        book = read_favorite(int(id))  # Utilisation de la fonction read_favorite
        return render_template('book_details.html', book=book)



@app.route('/add_to_favorites', methods=['POST'])
def add_to_favorites_route():
    user_id = request.form['user_id']
    book_id = request.form['book_id']
    
    # Récupérer les détails du livre à partir de la base de données
    book = model.get_book_details(book_id)
    
    # Ajouter le livre aux favoris
    model.add_to_favorites(user_id, book_id)
    
    # Passer les détails du livre à la template pour affichage
    return render_template('add_to_favorite.html', book=book)





@app.route('/remove_from_favorites', methods=['POST'])
def remove_from_favorites_route():
    user_id = request.form['user_id']
    book_id = request.form['book_id']
    removed = model.remove_from_favorites(user_id, book_id)
    if removed:
        # Si le livre a été retiré des favoris avec succès, renvoyer le template remove_from_favorite.html
        return render_template('remove_from_favorite.html', book_id=book_id)
    else:
        
        return "Livre a été retirer des favoris"





@app.route('/favorite_book/<user_id>')
def favorite_books_route(user_id):
    favorite_books = model.get_favorite_books(user_id)
    return render_template('favorite_book.html', favorite_books=favorite_books)


@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    added = model.add_to_cart(session['user_id'], book_id)
    if added:
        return redirect(url_for('book_added_to_cart'))  # Redirige vers la page de confirmation d'ajout au panier
    else:
        return "Ce livre est déjà dans votre panier."

@app.route('/book_added_to_cart')
def book_added_to_cart():
    return render_template('book_added_to_cart.html')


# Supprimer du panier
@app.route('/remove_from_cart/<book_id>', methods=['POST'])
@login_required
def remove_from_cart(book_id):
    model.remove_from_cart(session['user_id'], book_id)
    return redirect(url_for('home'))



@app.route('/cart', methods=['GET', 'POST'])
@login_required
def view_cart():
    if request.method == 'GET':
        cart_items = model.get_cart_items(session['user_id'])
        return render_template('cart.html', cart_items=cart_items)
    elif request.method == 'POST':
        book_id = request.form.get('book_id')
        if book_id:
            model.remove_from_cart(session['user_id'], book_id)
            return redirect(url_for('view_cart'))
        else:
            # Gérer les erreurs ici, si nécessaire
            pass


@app.route('/reservation_confirmation/<int:book_id>', methods=['POST'])
@login_required
def reservation_confirmation(book_id):
    if request.method == 'POST':
        added = model.add_reservation(session['user_id'], book_id)
        if added:
            return render_template('reservation_confirmation.html')  # Rendre la page de confirmation
        else:
            return "Erreur lors de la réservation."




@app.route('/my_reservations')
@login_required
def my_reservations():
    user_reservations = model.get_user_reservations(session['user_id'])
    return render_template('reservations_user.html', user_reservations=user_reservations)


@app.route('/remove_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def remove_reservation_route(reservation_id):
    user_id = session['user_id']

    remove_reservation(reservation_id, user_id)


    return redirect(url_for('my_reservations'))


@app.route('/confirm_remove_reservation/<int:reservation_id>')
@login_required
def confirm_remove_reservation(reservation_id):
    return render_template('reservation_confirmation_remove.html', reservation_id=reservation_id)

'''
if __name__ == "__main__":
    app.run(debug=True)'''
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
