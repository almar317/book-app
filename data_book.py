import requests  # type: ignore
from bs4 import BeautifulSoup # type: ignore
import json

# Initialiser un compteur global pour les IDs uniques
id_counter = 1



# Fonction pour récupérer les informations d'une page
def scrape_page(url):
    global id_counter  # Utilisation de la variable globale id_counter
    # Envoyer une requête GET à l'URL
    response = requests.get(url)
    # Parser le contenu HTML de la page
    soup = BeautifulSoup(response.text, 'html.parser')
    # Initialiser une liste pour stocker les informations des livres sur cette page
    books_on_page = []

    # Trouver tous les éléments contenant les informations des livres
    book_items = soup.find_all('div', class_='details')
    # Itérer sur chaque élément de livre et extraire les informations
    for item in book_items:
        book = {}
        # Extraire l'URL de l'image spécifique à chaque livre
        img_div = item.find_previous_sibling('div', class_='image')
        if img_div:
            img_elem = img_div.find('img')
            if img_elem:
                # Vérifier si l'URL est un chemin relatif (commence par "//")
                image_url = img_elem['src']
                if image_url.startswith("//"):
                    # Ajouter le préfixe "https:"
                    image_url = "https:" + image_url
                book['image_url'] = image_url
            else:
                book['image_url'] = "No Image"
        else:
            book['image_url'] = "No Image"

        # Extraire le titre du livre
        title_elem = item.find('a', class_='name')
        if title_elem:
            book['title'] = title_elem.text.strip()
        else:
            book['title'] = "Unknown Title"
        # Extraire l'auteur du livre
        author_elem = item.find_all('div')[0]
        if author_elem:
            book['author'] = author_elem.text.strip()
        else:
            book['author'] = "Unknown Author"
        # Récupérer l'URL du livre pour extraire le résumé
        book_url = "https://www.librairievauban.fr" + title_elem['href']
        # Extraire le résumé du livre en utilisant la fonction extract_summary
        book['summary'] = extract_summary(book_url)    
        # Extraire l'éditeur du livre
        publisher_elem = item.find_all('div')[1]
        if publisher_elem:
            book['publisher'] = publisher_elem.text.strip()
        else:
            book['publisher'] = "Unknown Publisher"
        # Extraire le prix du livre
        price_elem = item.find('span', class_='price')
        if price_elem:
            book['price'] = price_elem.text.strip()
        else:
            book['price'] = "Unknown Price"

        # Définir la librairie du livre
        book['bookstore'] = "Librairie Vauban"
        # Définir l'arrondissement du livre
        book['arrondissement'] = "6ème arrondissement"
        # Générer un ID unique pour le livre
        book['code postal'] = "13006"
        book['genre'] = "Science-Fiction"
        # Ajouter le livre à la liste
        books_on_page.append(book)
    return books_on_page

# Fonction pour extraire le résumé d'un livre à partir de son URL
def extract_summary(book_url):
    # Envoyer une requête GET à l'URL de la page du livre
    response = requests.get(book_url)
    # Parser le contenu HTML de la page
    soup = BeautifulSoup(response.text, 'html.parser')
    # Trouver la div contenant le résumé avec l'ID "infos-description"
    summary_div = soup.find('div', id='infos-description')
    # Extraire le texte du résumé
    if summary_div:
        summary = summary_div.text.strip()
    else:
        summary = "No summary available"
    return summary



# URL de la première page
base_url = "https://www.librairievauban.fr/rayon/sentimental-chick-lit/?f_shipping_delay=1&f_product_type=Book&page={}"


# Initialiser une liste pour stocker tous les livres
all_books = []

# Nombre total de pages à parcourir 
total_pages = 1

# Parcourir chaque page et récupérer les livres
for page_num in range(1, total_pages + 1):
    page_url = base_url.format(page_num)
    books_on_page = scrape_page(page_url)
    all_books.extend(books_on_page)

# Écrire les informations des livres dans un fichier JSON
with open('romance_vauban.json', 'w') as json_file:
    json.dump(all_books, json_file, indent=4)

print("Les données ont été stockées avec succès dans 'books.json'")

