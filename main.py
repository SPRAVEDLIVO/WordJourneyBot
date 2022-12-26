import ctypes
import os
from collections import Counter
from math import sqrt
from time import perf_counter, sleep

import cv2
import numpy
import pyautogui
import pytesseract
from PIL import Image, ImageDraw
from pynput.mouse import Button, Controller
from sewar import mse
from vk_sdk.listExtension import ListExtension
from vk_sdk.thread import threaded

from bbox import bbox_letters
from rect import Rect

controller = Controller()

slider = Image.open("images/slider.png")
hint = Image.open("images/hint.png")
cell = Image.open("images/cell.png")
player = Image.open("images/player.png")

target = Image.open("images/target.png")
shuffle = Image.open("images/shuffle.png")
extra = Image.open("images/extra_words.png")
completed = Image.open("images/finalized.png")

letters = {os.path.splitext(x)[0] : Image.open(f"images/letters/{x}") for x in os.listdir("images/letters/")}

def letter_by_img(x):
    for y, z in letters.items():
        if z == x: return y

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def color_dist(rgb1, rgb2):
    rmean = 0.5*(rgb1[0]+rgb2[0])
    r = rgb1[0] - rgb2[0]
    g = rgb1[1] - rgb2[1]
    b = rgb1[2] - rgb2[2]
    d = sqrt((int((512+rmean)*r*r) >> 8) + 4*g*g + (int((767-rmean)*b*b) >> 8))
    return int(d)

def pil2cv2(pil_image):
    open_cv_image = numpy.array(pil_image) 
    # Convert RGB to BGR 
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return open_cv_image

def contours(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dst = cv2.Canny(gray, 0, 150)
    blured = cv2.blur(dst, (5,5), 0)    
    img_thresh = cv2.adaptiveThreshold(blured, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    Contours, Hierarchy = cv2.findContours(img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return Contours

def load_combinations(letters: ListExtension):
    t = perf_counter()
    d = []
    # lL = len(letters)
    mapped = letters.map(lambda it: it[0])
    _l = mapped.join('')
    counted = Counter(_l)
    with open("dict.txt", encoding="utf_8_sig") as f:
        for line in f.readlines():
            if len(line) <= 3: continue # \n
            line = line[:-1].upper()
            cl = Counter(line)
            fl = True  
            for letter, c in cl.items():
                if not ((dX := counted.get(letter, 0)) != 0 and c <= dX):
                    fl = False
                    break

            if fl:
                d.append(line)
    print(f"combinations took: {perf_counter() - t:.2f}s")
    return d

def load_combinations_fast(letters):
    d = []
    letters = set(letters)
    # lL = len(letters)
    with open("dict.txt", encoding="utf_8_sig") as f:
        for line in f.readlines():
            line = line[:-1].upper()
            if len((s := set(line))) == (lenLine := len(line)) and (lenLine > 2) and (letters | s == letters):
                d.append(line)
    return d


class GameManager:
    window_name = "NoxPlayer1"
    
    def find_hwnd(self):
        self.hwnd = ctypes.windll.user32.FindWindowW(0, self.window_name)
        if not self.hwnd:
            print("Process is not running!")
            sleep(5)
            self.find_hwnd()

    def get_rect(self):
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(self.hwnd, ctypes.pointer(rect))
        self.rect = Rect(rect.left, rect.top, rect.right, rect.bottom)
        return self.rect

    def show_window(self):
        ctypes.windll.user32.SetForegroundWindow(self.hwnd)
        ctypes.windll.user32.ShowWindow(self.hwnd, 9)

    def take_screenshot(self) -> Image.Image:
        
        self.game_area: Image.Image = pyautogui.screenshot(region=self.get_rect().to_pyautogui())
        p = Rect(pyautogui.locate(player, self.game_area, confidence= 0.8, grayscale=False))
        self.game_area = self.game_area.crop((2, p.bottom+2, self.game_area.width, self.game_area.height))

        self.rect.top += p.bottom + 2
        # self.rect.x += 2

        return self.game_area

    def crop_word_area(self):
        sl = Rect(pyautogui.locate(slider, self.game_area, confidence = 0.8, grayscale=False))
        h = Rect(pyautogui.locate(hint, self.game_area, confidence= 0.8, grayscale=True))
        return self.game_area.crop((0, sl.bottom, h.left, h.top))


    def crop_letters_area(self):
        s1 = Rect(pyautogui.locate(target, self.game_area, confidence = 0.6, grayscale=False))
        s2 = Rect(pyautogui.locate(shuffle, self.game_area, confidence = 0.6, grayscale=False))
        s3 = Rect(pyautogui.locate(extra, self.game_area, confidence = 0.6, grayscale=False))
        
        r = Rect(max(s1.right, s3.right), s1.top, s2.left, s2.bottom)

        img = self.game_area.crop(list(r))
        self.letters_rect = r
        img = img.convert("RGBA")
        pic = img.load()

        for x in range(img.width):
            for y in range(img.height):
                if pic[x, y] != (255, 255, 255, 255):
                    pic[x, y] = (0,0,0, 0)

        return img
        
    def find_letter(self, img, l): 
        _score = {}
        for path, im in letters.items():
            _img = numpy.array(img)
            comp = numpy.array(im.resize(img.size))
            _score[path] = mse(_img, comp)
        return min(_score, key=_score.get)

    @threaded()
    def work(self):
        self.crop_word_area()

        # word_area = self.crop_word_area()
        # word_area.save('2.png')
        
        letters_area = self.crop_letters_area()
        letters_area.save("3.png")

        # draw = ImageDraw.Draw(letters_area)

        #self.game_area.save("1.png")

        boxes = bbox_letters(letters_area)
        draw = ImageDraw.Draw(letters_area)

        l: ListExtension | dict = ListExtension()
        fast_mode = True
        for box in boxes:
            img = letters_area.crop(list(box))
            letter = self.find_letter(img, l)
            if l.find(lambda it: it[0] == letter):
                print("Duplications detected. Using slow mode.")
                fast_mode = False
            l.append([letter, self.rect.x + self.letters_rect.x1 + box.left, self.rect.y + self.letters_rect.top + box.top])
            draw.rectangle(list(box), (0, 0, 0, 0), (255,255,255, 255), 2)
        
        letters_area.save("3.png")    
        
        if fast_mode:
            l = {x[0]: [x[1], x[2]] for x in l}

        # for l1 in l.values():
        #     pyautogui.click(l1)
        
        print(f"Letters: {''.join(l.map(lambda it: it[0]) if not fast_mode else list(l))}. Loading dict...")
        combos = load_combinations(l) if not fast_mode else load_combinations_fast(l)
        print(f"Found {len(combos)} valid words. Executing...")

        for combo in combos:
            _l = ListExtension(list(l))
            for idx, letter in enumerate(combo):
                if fast_mode:
                    pos = l[letter]
                else:
                    pos = _l.find(lambda it: it[0] == letter)
                    _l.remove(pos)
                    pos = pos[1:3]
                pyautogui.moveTo(pos, duration=0.1)
                if idx == 0:
                    controller.press(Button.left)
                sleep(0.1)

            controller.release(Button.left)
            sleep(0.2)

    def __init__(self) -> None:
        self.find_hwnd()
        self.show_window()
        self.take_screenshot()
        self.work()
        # while True:
        #     loc = pyautogui.locateOnWindow(completed, self.window_name, confidence=0.8, grayscale=True)
        #     if loc:
        #         pass
        #     sleep(1)


GameManager()