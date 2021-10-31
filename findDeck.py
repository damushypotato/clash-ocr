import numpy as np
import cv2
# import easyocr
import pyautogui
from PIL import Image
from win32 import win32gui
import tkinter as tk
from tkinter import ttk
import requests
import os
from dotenv import load_dotenv
from urllib import parse
load_dotenv()

api_key = os.environ.get("API_KEY")

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

# reader = easyocr.Reader(['en'], gpu=False)

def getInfo():
    ss = screenshot('Bluestacks')

    if not ss:
        print('Bluestacks not found')
        exit()

    width, height = ss.size
    
    badgeOffset = int(width * 0.078)

    left = badgeOffset
    top = 33
    right = (width - 33) * 0.82
    bottom = height * 0.1

    ss = ss.crop((left, top, right, bottom))

    img = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2BGR)

    levelLabelX = int((width - 33) / 2) - badgeOffset

    cv2.rectangle(img, (levelLabelX - 40, 20), (levelLabelX + 40, 30), (0, 0, 0), -1)
    cv2.rectangle(img, (levelLabelX, 15), (levelLabelX + 40, 25), (0, 0, 0), -1)

    cv2.imwrite('test.png', img)

    # result = reader.readtext(img)

    # if len(result) != 2:
    #     print('Insufficient player data')
    #     return

    # data = (result[0][1], result[1][1])

    # print(f'Player: {data[0]}\nClan: {data[1]}')
    # clans = requests.get(f'https://proxy.royaleapi.dev/v1/clans?name={parse.quote_plus(data[1])}&limit=100', headers={'authorization': f'Bearer {api_key}'}).json()
    # print(clans)


root = tk.Tk()
root.geometry('300x200')
root.resizable(False, False)
root.title('AI-DeckSniper')

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

root.mainloop()