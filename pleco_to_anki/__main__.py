import os
import sys
import re
import genanki

from datetime import datetime

from gtts import gTTS

from constants import css
from models import Phrase
from existing_phrases import get_existing_phrases


def save_extracted_phrases_as_json(phrases):
    # write to file
    import json
    import ast
    obj = ast.literal_eval(str(phrases))
    with open('./out/result.json', 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)

def talk(text,foldername,path,lan='zh'):
    if(text==None or text==''):
        return 
    if(''.join(re.findall(r'[\u4e00-\u9fffa-zA-Z0-9]+',text))=='' or ''.join(re.findall(r'[\u4e00-\u9fffa-zA-Z0-9]+',text))==None):
        return
    speech = gTTS(text=text, lang=lan, slow=False)
    ubication = path+"-"+lan+".mp3"
    speech.save(ubication)

def read_and_extract_phrases(path):
    with open(path, 'r+', encoding='utf-8-sig') as f:
        phrases = []
        for line in f.readlines():
            if line.startswith('//') or line == '\n' or line == '':
                continue
            phrases.append(Phrase.from_string(line))
        return phrases


def format_pleco_export(path, deck_name, categories):
    phrases = read_and_extract_phrases(path)
    mediaList = []
    file = lambda text : str(text)+'-zh.mp3'
    # save_extracted_phrases_as_json(phrases)
    #existing_phrases = get_existing_phrases(deck_name)
    #print(f'Found {len(existing_phrases)} phrases already in database')
    model = genanki.Model(
        hash(deck_name),
        name=deck_name + ' model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
            {"name": "audio"},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{audio}}{{Back}}',
            },
        ],
        css=css.CSS,
    )
    deck = genanki.Deck(hash(deck_name), deck_name)
    today='-'.join([str(i) for i in [datetime.now().year,datetime.now().month,datetime.now().day]])
    tags = []
    tags.append(today)
    [tags.append(i) for i in categories]
    for phrase in phrases:
        path=''.join(re.findall(r'[\u4e00-\u9fffa-zA-Z0-9]+',phrase.front_html())).split('spanclassverylargecenter')[1].split('span')[0]
        mediaName = file(path)
        mediaList.append(mediaName)
        soundName = '[sound:' + mediaName + ']'
        talk(''.join(re.findall(r'[\u4e00-\u9fffa-zA-Z0-9]+',phrase.front_html())).split('spanclassverylargecenter')[1].split('span')[0],'',path)
        #if phrase.chinese in existing_phrases:
            #continue
        note = genanki.Note(
            model=model,
            tags=tags,
            fields=[
                phrase.front_html(),
                phrase.back_html(),
                soundName,
            ],
        )
        deck.add_note(note)
    my_package = genanki.Package(deck)
    my_package.media_files = mediaList
    my_package.write_to_file( deck_name + '.apkg')


if __name__ == '__main__':
    wd = os.path.dirname(os.path.dirname(__file__))
    os.chdir(wd)
    args = sys.argv[1:3]
    cat = sys.argv[:3]
    if len(sys.argv[1:]) > 2:
        print('Usage: python3 pleco_to_anki <pleco_file> <deck_name> <category>')
    else:
        format_pleco_export(*args,cat)
