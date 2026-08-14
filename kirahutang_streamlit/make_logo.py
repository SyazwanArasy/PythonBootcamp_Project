from PIL import Image, ImageDraw, ImageFont
import os

# Create a transparent image, wide enough for the text
img = Image.new("RGBA", (300, 60), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Try to use a bold font; fall back to default if not found
try:
    font = ImageFont.truetype("arialbd.ttf", 28)  # Arial Bold, size 28
    print("Using Arial Bold font")
except Exception as e:
    font = ImageFont.load_default()
    print(f"Arial Bold not found, using default font. Reason: {e}")

# No emoji here - default fallback font can't render it and will error
draw.text((0, 20), "KiraHutang.com", font=font, fill="white")

# Make sure the static folder exists before saving
os.makedirs("static", exist_ok=True)

img.save("static/logo.png")

# Confirm the file was actually written and has content
if os.path.exists("static/logo.png") and os.path.getsize("static/logo.png") > 0:
    print("✅ Logo saved successfully to static/logo.png")
else:
    print("❌ Something went wrong - file is missing or empty")