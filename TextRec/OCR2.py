import os
import numpy as np
import cv2
import pytesseract


def main():
    img = cv2.imread('/home/felipe/Downloads/20.jpg')
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.threshold(img_gray, 156, 255, cv2.THRESH_TOZERO)[1]
    kernel = np.ones((3, 3), np.uint8)
    img_gray = cv2.dilate(img_gray, kernel, iterations=1)
    img_gray = cv2.erode(img_gray, kernel, iterations=1)
    img_gray = cv2.medianBlur(img_gray, 3)
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, img_gray)
    text = pytesseract.image_to_string(img_gray)
    print(text)


if __name__ == '__main__':
    main()
