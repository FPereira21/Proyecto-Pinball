import numpy as np
import cv2
import pytesseract
from time import time
from DB.ScoreAppend import add_score
from urllib.request import Request, urlopen
from os import environ
from slack_sdk import WebClient


def sanitize_img(img) -> np.ndarray:
    """Convert to B&W, remove dim pixels and fill holes"""
    # Aplica grayscale y elimina los pixeles con brillos bajos
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.threshold(img_gray, 175, 255, cv2.THRESH_TOZERO)[1]
    kernel = np.ones((3, 3), np.uint8)
    # Si un pixel tiene mas que cierto valor, le agrega a los pixeles cercanos brillo
    # Sirve para llenar pequenios espacios vacios en la imagen
    img_gray = cv2.dilate(img_gray, kernel, iterations=2)
    # Hace lo contrario de dilate
    # Si un pixel es 1, se fija si los cercanos son 1, si no todos son 1, lo hace 0
    # Sirve para deshacer las contras de dilate
    img_gray = cv2.erode(img_gray, kernel, iterations=1)
    # Borronea la imagen para hacerla mas suave y que tesseract sea mas preciso
    img_gray = cv2.medianBlur(img_gray, 3)
    cv2.imwrite('pingue.jpg', img_gray)
    return img_gray


def read_txt_from_img(sanitized_img) -> str:
    """Read text form sanitized image and return the text"""
    # Magia Negra
    text = pytesseract.image_to_string(sanitized_img)

    return text


def score_listening_mode(playerid: str) -> str:
    """Enter a listening state to wait for the score to show on the Pinball screen.
    Uploads the score to the given player id
    """
    video_capture = cv2.VideoCapture(0)
    frame_rate = 2
    prev = 0

    while True:
        time_elapsed = time() - prev
        ret, frame = video_capture.read()

        if time_elapsed > 1 / frame_rate:
            sanitized_img = sanitize_img(frame)
            text = read_txt_from_img(sanitized_img)
            lower_text = text.lower()
            no_spaces = lower_text.replace(' ', '')
            if no_spaces.find("gameover"):
                add_score(playerid)
                break

    video_capture.release()
    cv2.destroyAllWindows()

# ToDo retrieve images from SLACK
def score_from_slack_img(img_link: str):

    slack_bot_token = environ.get('SLACK_BOT_TOKEN')
    url = img_link
    req = Request(url)
    req.add_header('Authorization', f'Bearer {slack_bot_token}')
    content = urlopen(req).read()
    f = open('/home/felipe/Downloads/pinbolo.jpg', 'wb')
    f.write(content)
    f.close()


def main():
    score_from_slack_img()


if __name__ == '__main__':
    main()
