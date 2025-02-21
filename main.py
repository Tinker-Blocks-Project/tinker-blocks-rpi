import cv2
import pytesseract
import numpy as np
from tabulate import tabulate


def findLeftBorder(img, r, c):
    for i in range(r):
        for j in range(c):
            if img[i][j] < 5:
                return i, j


def findRightBorder(img, r, c):
    for j in range(c - 1, 0, -1):
        if img[r][j] < 5:
            return r, j


def findLowerBorder(img, r, c):
    for i in range(r - 1, 0, -1):
        if img[i][c] < 5:
            return i, c


def applyFilters(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply adaptive thresholding (Ensures binary image)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Invert image if needed (text is black, background is white)
    inverted = cv2.bitwise_not(binary)

    # **Detect Horizontal Lines**
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))  # Width affects sensitivity
    horizontal_lines = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, kernel_h, iterations=2)

    # **Detect Vertical Lines**
    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))  # Height affects sensitivity
    vertical_lines = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, kernel_v, iterations=2)

    # **Remove Lines while Keeping Text**
    mask = cv2.bitwise_or(horizontal_lines, vertical_lines)  # Combine detected lines
    cleaned = cv2.bitwise_and(inverted, cv2.bitwise_not(mask))  # Remove lines

    # Invert back to original format (black text, white background)
    final_img = cv2.bitwise_not(cleaned)
    return final_img


img_readed = cv2.imread("assets/simple_image.png", 1)
row_size, column_size, _ = img_readed.shape
img = cv2.cvtColor(img_readed, cv2.COLOR_BGR2GRAY)

x1, y1 = findLeftBorder(img, row_size, column_size)
x2, y2 = findRightBorder(img, x1, column_size)
x3, y3 = findLowerBorder(img, row_size, y1)
x4, y4 = x3, y2  # fourth point does not need a function

rows = 8
columns = 8
width = y2 - y1
height = x3 - x1
cell_width = width // columns
cell_height = height // rows

result = [[0] * columns for i in range(rows)]

for i in range(rows):
    for j in range(columns):
        x, y = x1 + i * cell_height, y1 + j * cell_width
        h, w = cell_height, cell_width
        img_cropped = img_readed[x:x + h, y:y + w]
        final_img = applyFilters(img_cropped)
        # Resize for better OCR accuracy
        resized = cv2.resize(final_img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

        # OCR Processing
        custom_config = r'--oem 3 --psm 6'  # Set OCR mode
        text = pytesseract.image_to_string(resized, config=custom_config, lang="eng").strip()

        print(f"Extracted Text: {text}")
        result[i][j] = text

        #cv2.imshow('window', resized)
        #cv2.waitKey(0)

cv2.destroyAllWindows()

print(tabulate(result, tablefmt="grid"))