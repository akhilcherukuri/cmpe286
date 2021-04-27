import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735
 
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
 
BAUDRATE = 24000000

spi = board.SPI()
 

disp = st7735.ST7735R(spi, rotation=90,           # 1.8" ST7735R
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height
image = Image.new("RGB", (width, height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
 
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)

# First define some constants to allow easy positioning of text.
padding = 6
x = 0

# Load a TTF Font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
 
while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
 
    Line1 = " AWS Status: Connected "
    Line2 = " Temperature: "
    Line3 = " Humditity: "
    Line0 = " Weather Station 1 "

    # Write four lines of text.
    y = padding
    draw.text((x, y), Line0, font=font, fill="#FFFFFF")
    y += font.getsize(Line0)[1]
    draw.text((x, y), Line1, font=font, fill="#FFFF00")
    y += font.getsize(Line1)[1]
    draw.text((x, y), Line2, font=font, fill="#00FF00")
    y += font.getsize(Line2)[1]
    draw.text((x, y), Line3, font=font, fill="#0000FF")
    y += font.getsize(Line3)[1]
 
    # Display image.
    disp.image(image)
    time.sleep(0.1)