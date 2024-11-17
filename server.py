import datetime
import json
import os
import sqlite3
import threading
from enum import Enum
from hashlib import md5

import frontmatter
import markdown
import requests
import unidecode
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware

from scripts.utils.validate import validate_doc

lock = threading.Lock()
version = "1.3.0"
app = FastAPI(title='Remède', description='Un dictionnaire libre.', version=version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


class BinariesVariant(str, Enum):
    aarch_dmg = "aarch64.dmg"
    aarch_app = "aarch64.app.tar.gz"
    x64_dmg = "x64.dmg"
    x64_app = "x64.app.tar.gz"
    apk = "apk"
    deb = "deb"
    exe = "exe"
    msi = "msi"


def get_stats(db_path: str):
    db = sqlite3.connect(db_path, check_same_thread=False)
    db_cursor = db.cursor()
    total = db_cursor.execute("SELECT COUNT(*) FROM dictionary").fetchone()[0]
    db_cursor.close()
    return total


def check_validity(db_path: str, use_new_schema: bool = False, schema: str = None):
    db = sqlite3.connect(db_path, check_same_thread=False)
    db_cursor = db.cursor()
    all_documents = db_cursor.execute("SELECT * FROM dictionary").fetchall()
    db_cursor.close()
    index = 1 if not use_new_schema else 9
    for row in all_documents:
        doc = json.loads(row[index])
        if not doc:
            continue
        success, error = validate_doc(doc, schema)
        if not success:
            print(f"\033[A\033[KStarting API | Checking JSON schemas validity... Failed for \"{db_path}\", {error} [3/3]")
            return False
    return True


def in_json(response: str | list):
    return json.loads(json.dumps(response))


def fetch_random_word():
    lock.acquire(True)
    return cursor.execute("SELECT word FROM dictionary ORDER BY RANDOM() LIMIT 1").fetchone()[0]


def fetch_remede_word_of_day():
    global WORD_OF_DAY
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    if today != WORD_OF_DAY['date']:
        WORD_OF_DAY['date'] = today
        WORD_OF_DAY['word'] = fetch_random_word()
        lock.release()
    return WORD_OF_DAY['word']


def fetch_remede_doc(word: str):
    lock.acquire(True)
    response = cursor.execute(f"SELECT document FROM dictionary WHERE word = '{word}'").fetchone()
    return response[0] if response else json.dumps({'message': 'Mot non trouvé'})


def fetch_autocomplete(query: str, limit: bool = False, page: int = 0):
    lock.acquire(True)
    if limit:
        response = cursor.execute(f"SELECT word FROM wordlist WHERE indexed LIKE '{query}%' ORDER BY word ASC LIMIT 5").fetchall()
    else:
        response = cursor.execute(f"SELECT word FROM wordlist WHERE indexed LIKE '{query}%' ORDER BY word ASC LIMIT 50 OFFSET ${page * 50}").fetchall()
    return list(map(lambda row: row[0], response))


def get_sheets():
    files = os.listdir('data/fiches')
    sheets = []
    for filename in files:
        with open(f'data/fiches/{filename}') as file:
            metadata = frontmatter.load(file)
            metadata['credits']['text'] = markdown.markdown(metadata['credits']['text'])
            sheets.append({
                'nom': metadata['nom'],
                'description': metadata['description'],
                'tags': metadata['tags'],
                'credits': metadata['credits'],
                'slug': metadata['slug'],
                'contenu': markdown.markdown(metadata.content),
                'path': f'data/fiches/{filename}'
            })
    return sheets


def get_github_config():
    with open('.github.json') as file:
        return json.loads(file.read())


def register_new_word_idea(word: str):
    try:
        config = get_github_config()
        repo = config['repo']
        token = config['token']
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        data = {
            "title": f"📘 [Anonymous:Word] Add word \"{word}\"",
            "body": f"Word \"{word}\" was searched on Remède but no definition was found so an anonymous user reported it !",
            "labels": config['labels'],
            "assignees": config['assignees']
        }
        response = requests.post(f"https://api.github.com/repos/{repo}/issues", headers=headers, json=data)
        return response.status_code == 201
    except:
        return False


def sanitize_query(q: str):
    return unidecode.unidecode(q.lower().replace('-', ' ').replace("'", " "))


@app.get('/')
def root():
    """
    ### Returns useful information about API and datasets
    - Its version
    - The available dictionaries
        - Their name (`name`)
        - Their unique identifier (hash) (`hash`)
        - Their slug; used to download or search in specific database (`slug`)
        - The number of words in the database (`total`)
        - Does the database respect the Remède JSON Schema (`valid`)
        - Which schema does it follow (`schema`)
        - Database readable size (`size`)
    """
    return {
        "version": version,
        "message": "Check /docs for documentation",
        "dictionaries": DICTIONARIES
    }


@app.get('/word/{word}')
def get_word_document(word: str):
    """
    Renvoie le document Remède du mot `word`
    """
    document = fetch_remede_doc(word.replace("'", "''"))
    lock.release()
    return json.loads(document)


@app.get('/random')
def get_random_word_document():
    """
    Renvoie un mot au hasard
    """
    word = fetch_random_word()
    lock.release()
    return in_json(word)


@app.get('/word-of-day')
def get_word_of_day():
    """
    Renvoie le mot du jour
    """
    return in_json(fetch_remede_word_of_day())


@app.get('/autocomplete/{query}')
def get_autocomplete(query: str):
    """
    Renvoie les 6 premiers mots commençant par `query`, n'est pas sensible à la casse et aux accents !
    """
    safe_query = sanitize_query(query)
    results = fetch_autocomplete(safe_query, True)
    lock.release()
    return in_json(results)


@app.get('/search/{query}')
def get_search_results(query: str, page: int = 0):
    """
    Renvoie les mots commençant par `query`, n'est pas sensible à la casse et aux accents !
    """
    safe_query = sanitize_query(query)
    results = fetch_autocomplete(safe_query, False, page)
    lock.release()
    return in_json(results)


@app.get('/ask-new-word/{query}')
def send_new_word(query: str):
    """
    Enregistre le word `query` comme mot à rajouter au dictionnaire !
    """
    success = register_new_word_idea(query)
    if success:
        return {
            "message": "Successfully added word to words to add."
        }
    return {
        "message": "Failed to add word to list..."
    }


@app.get('/sheets')
def get_cheatsheets():
    """
    Renvoie la totalité des fiches de grammaire, d'orthographe et de règles référencées
    """
    return SHEETS


@app.get('/sheets/{slug}')
def get_cheatsheet_by_slug(slug: str):
    """
    Renvoie la fiche de grammaire / d'orthographe avec le slug `slug`
    """
    return SHEETS_BY_SLUG.get(slug, {
        "contenu": "",
        "description": "La fiche n'a pas été trouvée !",
        "nom": "Pas de fiche",
        "tags": [],
        "slug": "",
        "credits": ""
    })


@app.get('/sheets/download/{slug}')
def download_cheatsheet_by_slug(slug: str):
    """
    Renvoie le fichier markdown correspondant à la fiche avec le slug `slug`
    """
    fiche = SHEETS_BY_SLUG.get(slug, {
        "contenu": "",
        "description": "La fiche n'a pas été trouvée !",
        "nom": "Pas de fiche",
        "tags": [],
        "slug": "",
        "credits": "",
        "path": None
    })
    if fiche['path']:
        return FileResponse(fiche['path'], filename=f"{slug}.md")
    return HTTPException(status_code=404, detail='Fiche non trouvée !')


@app.get('/download')
def download_database(variant: str = 'remede'):
    """
    Télécharge la base Sqlite sous form de fichier.
    """
    return FileResponse(f'data/{variant}.db')


@app.get('/release/{variant}')
def download_binary(variant: BinariesVariant):
    """
    Télécharge les derniers exécutables
    """
    return FileResponse(f'builds/remede.{variant}', filename=f"remede.{variant}", media_type="multipart/form-data")


if __name__ == '__main__':
    print("Starting API | Opening databases... [1/3]")
    remede_database = sqlite3.connect('data/remede.db', check_same_thread=False)
    remede_cursor = remede_database.cursor()

    DATABASES = {
        "remede": remede_cursor,
        "remede.legacy": remede_cursor  # TODO change
    }

    WORD_OF_DAY = {
        "date": "",
        "word": ""
    }
    print("\033[A\033[KStarting API | Calculating databases size... [2/3]")
    DICTIONARIES = {
        "remede": {
            "name": "Remède (FR)",
            "slug": "remede",
            "total": get_stats('data/remede.db'),
            "hash": md5(open('data/remede.db', 'rb').read()).hexdigest()[0:7],
            "valid": False,
            "schema": "schema.json",
            "size": f"{int(os.path.getsize('data/remede.db') * 10e-7)}Mb"
        },
        "remede.legacy": {
            "name": "Remède 1.2.3 (FR)",
            "slug": "remede.legacy",
            "total": get_stats('data/remede.legacy.db'),
            "hash": md5(open('data/remede.legacy.db', 'rb').read()).hexdigest()[0:7],  # TODO replace with legacy new database
            "valid": False,
            "schema": "1.2.3.schema.json",
            "size": f"{int(os.path.getsize('data/remede.legacy.db') * 10e-7)}Mb"
        },
        # "remede.en": {
        #     "nom": "Remède (EN) ~200Mb",
        #     "slug": "remede.en",
        #     "hash": md5(open('data/remede.en.db', 'rb').read()).hexdigest()[0:7]
        # }
    }

    print("\033[A\033[KStarting API | Checking JSON schemas validity... Can take a while... [3/3]")
    # DICTIONARIES["remede"]["valid"] = check_validity('data/remede.db', True)
    DICTIONARIES["remede"]["valid"] = check_validity('data/remede.db', schema='docs/1.2.3.schema.json')
    DICTIONARIES["remede.legacy"]["valid"] = check_validity('data/remede.legacy.db', schema='docs/1.2.3.schema.json')

    SHEETS = get_sheets()
    SHEETS_BY_SLUG = {f"{sheet['slug']}": sheet for sheet in SHEETS}

    print("\033[A\033[KStarting API | Done. [3/3]")
    uvicorn.run(app, host='0.0.0.0')
