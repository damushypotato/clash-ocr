import numpy as np
import cv2
import easyocr
import pyautogui
from PIL import Image, ImageTk, ImageFile
from win32 import win32gui
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

def screenshot(window_title=None) -> Image:
    if window_title:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            x, y, x1, y1 = win32gui.GetClientRect(hwnd)
            x, y = win32gui.ClientToScreen(hwnd, (x, y))
            x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
            im = pyautogui.screenshot(region=(x, y, x1, y1))
            return im
        else:
            print('Window not found!')
    else:
        im = pyautogui.screenshot()
        return im

reader = easyocr.Reader(['en'], gpu=False)

def getInfo():
    ss = screenshot('Bluestacks')

    if not ss:
        print('Bluestacks not found')
        exit()

    width, height = ss.size
    
    badgeOffset = int(width * 0.08)

    left = badgeOffset
    top = 33
    right = (width - 33) * 0.82
    bottom = height * 0.1

    ss = ss.crop((left, top, right, bottom))
    img = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2GRAY)

    levelLabelX = int((width - 33) / 2) - badgeOffset

    cv2.rectangle(img, (levelLabelX - 40, 20), (levelLabelX + 40, 30), (255, 255, 255), -1)
    cv2.rectangle(img, (levelLabelX, 15), (levelLabelX + 40, 25), (255, 255, 255), -1)

    img = cv2.bitwise_not(img)

    thresh = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,15,2)

    result = reader.readtext(img)

    if len(result) != 2:
        print('Insufficient player data')
        cv2.imshow('Data', thresh)
        cv2.waitKey(0)
        return

    data = (result[0][1], result[1][1])

    print(f'Player: {data[0]}\nClan: {data[1]}')

    # cv2.imshow('Data', thresh)
    # cv2.waitKey(0)

    displayDeck(data)


def displayDeck(data):
    clans: list = requests.get(f'https://proxy.royaleapi.dev/v1/clans?name={parse.quote_plus(data[1])}&limit=20', headers={'authorization': f'Bearer {api_key}'}).json()['items']
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
        ratio = fuzz.WRatio(data[0], m['name'])
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
    command=lambda: getInfo()
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
