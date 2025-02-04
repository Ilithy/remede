import json


def get_words():
    with open('data/fr/words.txt') as file:
        return file.read().split(';')


def get_saved_wordlist():
    with open('data/missing-wordlist.txt') as file:
        return file.read().split(';')


def save_progression_wordlist(save: list):
    with open('data/missing-wordlist.txt', 'w+') as file:
        file.write(';'.join(save))


def get_custom_words():
    with open('data/custom_words.json') as file:
        return json.loads(file.read())


def get_word2ipa():
    with open('data/fr/ipa.json') as file:
        return json.loads(file.read())
