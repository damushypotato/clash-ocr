import numpy as np
import cv2
from PIL import Image, ImageTk, ImageFile
from tkinter import Tk, Canvas, constants
from tkinter import ttk
import requests
import os
from dotenv import load_dotenv
from urllib import parse, request
from fuzzywuzzy import fuzz
from io import BytesIO
load_dotenv()

api_key = os.environ.get("API_KEY")

ImageFile.LOAD_TRUNCATED_IMAGES = True

def displayDeck(data):
    clans: list = requests.get(f'https://proxy.royaleapi.dev/v1/clans?name={parse.quote_plus(data[1])}&limit=50', headers={'authorization': f'Bearer {api_key}'}).json()['items']
    if len(clans) == 0:
        print('Clan not found')
        return
    matches = []
    for c in clans:
        ratio = fuzz.WRatio(data[1], c['name'])
        if ratio == 100:
            matches.append(c)
    allMembers = []
    if len(matches) == 0:
        results = []
        for c in clans:
            ratio = fuzz.WRatio(data[1], c['name'])
            results.append(ratio)
            if ratio == 100:
                break
        i = len(results) - 1
        clan = None
        if results[i] == 100:
            clan = clans[i]
        else:
            clan = clans[results.index(max(results))]
        allMembers = requests.get(f'https://proxy.royaleapi.dev/v1/clans/{parse.quote_plus(clan["tag"])}', headers={'authorization': f'Bearer {api_key}'}).json()['memberList']
    else:
        for match in matches:
            members: list = requests.get(f'https://proxy.royaleapi.dev/v1/clans/{parse.quote_plus(match["tag"])}', headers={'authorization': f'Bearer {api_key}'}).json()['memberList']
            allMembers.extend(members)
    
    results = []
    for m in allMembers:
        ratio = fuzz.ratio(data[0], m['name'])
        results.append(ratio)
        if ratio == 100:
            break
    member = None
    i = len(results) - 1
    if results[i] == 100:
        member = allMembers[i]
    else:
        member = allMembers[results.index(max(results))]
    target = requests.get(f'https://proxy.royaleapi.dev/v1/players/{parse.quote_plus(member["tag"])}', headers={'authorization': f'Bearer {api_key}'}).json()
    deck = []
    deckImg = []
    for card in target['currentDeck']:
        deck.append(card['name'])
        deckImg.append(card['iconUrls']['medium'])
    print(', '.join(deck))
    canvas.delete("all")
    global cardImgs
    cardImgs = []
    for i, img in enumerate(deckImg):
        imgBytes = request.urlopen(img).read()
        img = Image.open(BytesIO(imgBytes))
        img = ImageTk.PhotoImage(img)
        cardImgs.append(img)
        x = i * 277
        y = 0
        if i >= 4:
            x = (i - 4) * 277
            y = 330
        canvas.create_image((x, y), image=cardImgs[i], anchor=constants.NW)
    print(target['name'], target['clan']['name'])


root = Tk()
root.resizable(False, False)
root.title('AI-DeckSniper')

cardImgs = []

button = ttk.Button(
    root,
    text='Snipe Deck',
    command=lambda: displayDeck(('Craktor','TEAM ROYAL'))
)

button.pack(
    ipadx=5,
    ipady=5,
    expand=True
)

canvas = Canvas(root, width=1108, height=660, background='white')
image: Image = Image.open('emptyDeck.png')
image = image.resize((1108, 660), Image.ANTIALIAS)
image = ImageTk.PhotoImage(image)
canvas.create_image(554, 330, image=image)

canvas.pack()

root.mainloop()
