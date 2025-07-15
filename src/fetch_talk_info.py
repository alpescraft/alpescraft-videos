import typer
import requests
from bs4 import BeautifulSoup
import os
import yaml
import urllib.parse
import shutil

app = typer.Typer()

def download_image(url, folder, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(os.path.join(folder, filename), 'wb') as file:
            shutil.copyfileobj(response.raw, file)
        print(f"✅ Image téléchargée: {url}")
    except Exception as e:
        print(f"❌ Erreur image: {url} - {e}")

def fetch_talk_info(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    talks_div = soup.select('div.talks')
    if not talks_div:
        raise Exception("❌ Aucun bloc talks trouvé.")

    talks = talks_div[0].find_all('div', class_='talk')
    if not talks:
        raise Exception("❌ Aucun talk trouvé.")

    attendees_div = soup.select_one('div.attendees')
    if not attendees_div:
        raise Exception("❌ Aucun bloc attendees trouvé.")

    # Liste des speakers (attendees)
    attendee_divs = attendees_div.find_all('div', class_='attendee')
    speakers_info = []
    for attendee in attendee_divs:
        name_tag = attendee.select_one('strong.name')
        name = name_tag.get_text(strip=True) if name_tag else "Unknown"
        img_tag = attendee.select_one('img')
        img_url = urllib.parse.urljoin(url, img_tag['src']) if img_tag else ""
        speakers_info.append({'name': name, 'img_url': img_url})

    talk_data = []

    for i, talk in enumerate(talks, start=1):
        # Titre
        title = talk.select_one('h4').get_text(strip=True)

        # Texte brut dans <a>
        speaker_tag = talk.select_one('div > a')
        if speaker_tag:
            full_text = speaker_tag.get_text(strip=True)
            # Enlever " le ..." s'il existe
            if " le " in full_text:
                speaker_name_in_talk = full_text.split(" le ")[0].strip()
            else:
                speaker_name_in_talk = full_text.strip()
        else:
            speaker_name_in_talk = f"Speaker {i}"

        # Chercher le speaker correspondant
        matched_speaker = next((s for s in speakers_info if s['name'] == speaker_name_in_talk), None)

        if matched_speaker:
            speaker_name = matched_speaker['name']
            img_url = matched_speaker['img_url']
        else:
            speaker_name = speaker_name_in_talk
            img_url = ""

        # Créer dossier
        talk_folder = f'to-proceed/talk{i}'
        os.makedirs(talk_folder, exist_ok=True)

        if img_url:
            download_image(img_url, talk_folder, 'img.png')

        talk_info = {
            'title': title,
            'speaker_name': speaker_name,
        }
        talk_data.append(talk_info)

    return talk_data

def create_yaml_files(talk_data):
    os.makedirs('to-proceed', exist_ok=True)

    for i, talk in enumerate(talk_data, start=1):
        talk_folder = f'to-proceed/talk{i}'
        yaml_content = {
            'title': talk['title'],
            'speaker_name': talk['speaker_name'],
            'speaker': {'parts': [{'start': '0:00', 'stop': '09:51'}]},
            'sound': {'extra_offset': 0.0},
            'slides': {}
        }

        yaml_file_path = os.path.join(talk_folder, 'config.yml')
        with open(yaml_file_path, 'w') as file:
            yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"✅ YAML: {yaml_file_path}")

@app.command()
def main(url: str = typer.Argument(..., help="URL complète de l'événement")):
    print(f"🚀 Traitement de: {url}")

    talk_data = fetch_talk_info(url)
    create_yaml_files(talk_data)

    print("✅ Tout terminé.")

if __name__ == "__main__":
    app()
