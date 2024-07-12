import requests
from bs4 import BeautifulSoup
import os
import yaml
import urllib.parse
import shutil
import argparse

# Fonction pour télécharger une image à partir d'une URL
def download_image(url, folder, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Assurez-vous que la requête s'est terminée avec succès
        with open(os.path.join(folder, filename), 'wb') as file:
            shutil.copyfileobj(response.raw, file)
        print(f"Image téléchargée: {url}")
    except requests.HTTPError as e:
        print(f"Erreur HTTP lors du téléchargement de l'image: {url} - {e}")
    except Exception as e:
        print(f"Erreur lors du téléchargement de l'image: {url} - {e}")

# Fonction pour récupérer les informations du talk et les images des speakers
def fetch_talk_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Assurez-vous que la requête s'est terminée avec succès
    except requests.HTTPError as e:
        raise Exception(f"Échec de la récupération de la page web : {url} - {e}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Récupération des talks
    talks_div = soup.select('div.talks')
    if not talks_div:
        raise Exception("Impossible de trouver la section des talks sur la page.")

    talks = talks_div[0].find_all('div', class_='talk')

    if not talks:
        raise Exception("Aucun talk trouvé dans la section des talks.")

    talk_data = []
    for i, talk in enumerate(talks, start=1):
        title = talk.select_one('h4').get_text(strip=True)
        speaker = talk.select_one('div > a').get_text(strip=True)

        # Préparer le dossier pour ce talk
        talk_folder = f'to-proceed/talk{i}'
        if not os.path.exists(talk_folder):
            os.makedirs(talk_folder)

        talk_info = {
            'title': title,
            'speaker_name': speaker,
        }
        talk_data.append(talk_info)

    # Récupération des images des speakers
    attendees_div = soup.select('div.attendees')
    if not attendees_div:
        raise Exception("Impossible de trouver la section des participants sur la page.")

    attendee_images = attendees_div[0].find_all('div', class_='attendee')

    for i, img_div in enumerate(attendee_images):
        img_url = img_div.select_one('img')['src']
        img_url = urllib.parse.urljoin(url, img_url)  # Assurez-vous que l'URL est absolue

        if i < len(talk_data):
            talk_folder = f'to-proceed/talk{i+1}'
            img_filename = "speaker.webp"
            download_image(img_url, talk_folder, img_filename)
        else:
            print(f"Aucune donnée de talk disponible pour l'image {i + 1}.")

    return talk_data

# Fonction pour créer des fichiers YAML avec les informations des talks
def create_yaml_files(talk_data):
    if not os.path.exists('to-proceed'):
        os.makedirs('to-proceed')

    for i, talk in enumerate(talk_data, start=1):
        talk_folder = f'to-proceed/talk{i}'

        # Créer le fichier YAML
        yaml_content = {
            'title': talk['title'],
            'speaker_name': talk['speaker_name'],
            'speaker': {
                'parts': [
                    {'start': '0:00', 'stop': '09:51'}
                ]
            },
            'sound': {'extra_offset': 0.0},
            'slides': {}
        }

        yaml_file_path = os.path.join(talk_folder, 'config.yml')
        with open(yaml_file_path, 'w') as file:
            yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False, allow_unicode=True)

# Fonction principale pour gérer les arguments et lancer le script
def main():
    parser = argparse.ArgumentParser(description="Récupère des informations sur un événement Humantalks et génère des fichiers YAML.")
    parser.add_argument(
        'url',
        type=str,
        help="L'URL complète de la page de l'événement"
    )

    args = parser.parse_args()

    print(f"Récupération des informations pour l'événement : {args.url}")

    # Exécution des fonctions
    talk_data = fetch_talk_info(args.url)
    create_yaml_files(talk_data)
    print(f"Les informations des talks et les images ont été récupérées et sauvegardées dans 'to-proceed'.")

if __name__ == "__main__":
    main()
