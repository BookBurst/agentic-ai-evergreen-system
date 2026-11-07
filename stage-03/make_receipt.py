from PIL import Image, ImageDraw, ImageFont, ImageFilter

LINES = [
    ("CORNER HARDWARE", ""),
    ("Order 20417  Mar 08 2027", ""),
    ("", ""),
    ("Wood glue 8 oz", "6.49"),
    ("Sandpaper pack x3", "11.25"),
    ("Paint brush 2 in", "4.75"),
    ("Masking tape", "3.98"),
    ("", ""),
    ("Subtotal", "26.47"),
    ("Tax 7%", "1.85"),
    ("TOTAL", "28.32"),
]

def draw(path="receipt.png"):
    font = ImageFont.load_default(size=26)
    height = 150 + 44 * len(LINES)
    img = Image.new("RGB", (520, height), "white")
    pen = ImageDraw.Draw(img)
    y = 40
    for left, right in LINES:
        pen.text((30, y), left, fill="black", font=font)
        pen.text((420, y), right, fill="black", font=font)
        y += 44
    # Soften it and tilt it a little, like a phone photo
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    img.rotate(1.5, expand=True, fillcolor="white").save(path)

if __name__ == "__main__":
    draw()
