from operator import itemgetter
from os import remove
import cv2
import numpy
import pytesseract
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter

headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 '
                      'Safari/537.36 '
    }


def get_img(s, captcha_url):
    file_name = 'captcha.jpg'
    captcha = s.get(captcha_url, headers=headers)
    f = open(file_name, 'wb')
    f.write(captcha.content)
    f.close()


def solve_captcha_simple():
    original = Image.open("captcha.jpg")
    original.save("original.png")
    black_and_white = original.convert("L")
    black_and_white.save("black_and_white.png")

    img = cv2.imread("black_and_white.png")
    text = pytesseract.image_to_string(img)

    remove_files()

    print(text)
    return text


def solve_captcha():
    th1 = 140
    th2 = 140
    sig = 1.5

    original = Image.open("captcha.jpg")
    original.save("original.png")
    black_and_white = original.convert("L")
    black_and_white.save("black_and_white.png")
    first_threshold = black_and_white.point(lambda p: p > th1 and 255)
    first_threshold.save("first_threshold.png")
    blur = numpy.array(first_threshold)
    blurred = gaussian_filter(blur, sigma=sig)
    blurred = Image.fromarray(blurred)
    blurred.save("blurred.png")
    final = blurred.point(lambda p: p > th2 and 255)
    final = final.filter(ImageFilter.EDGE_ENHANCE_MORE)
    final = final.filter(ImageFilter.SHARPEN)
    final.save("final.png")

    img = cv2.imread("final.png")
    text = pytesseract.image_to_string(img)

    remove('captcha.jpg')
    remove('original.png')
    remove('black_and_white.png')
    remove('first_threshold.png')
    remove('blurred.png')
    remove('final.png')
    print(text)
    return text


def remove_files():
    remove('captcha.jpg')
    remove('original.png')
    remove('black_and_white.png')
