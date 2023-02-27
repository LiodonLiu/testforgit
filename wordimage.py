# from wordimage import wordimage
# wordimage('duty')

from PIL import Image, ImageDraw, ImageFont
import os

def wordimage(word):
    ##首先生成生成图的画布，若是考虑位置关系的话，画布大小需要更改    
    width = 500
    height = 500
    img = Image.new('RGB', (width, height), color=(255, 255, 255))

    word_font = ImageFont.truetype('./font/Ruzicka.ttf', 100)
    d = ImageDraw.Draw(img)    #在图片下方显示对应的图片名
    d.text((0,225), word, font=word_font, fill=(50, 50, 50))

    img.save(os.path.join('./foundImages/', word + '.jpg'))