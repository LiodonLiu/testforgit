# from toward import toward
# a = 'room'
# toward(a)

from PIL import Image, ImageDraw, ImageFont
import os

def toward(target):

    word_font = ImageFont.truetype('./font/Arial.ttf', 40)

    canvas_width = 900
    canvas_height = 1800
    canvas_img = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))

    img1 = Image.open('./foundImages/' + target + '.jpg')
    img1 = img1.resize((500, 500))    #调整图片大小
    img2 = Image.open('./foundImages/' + 'arrowhead' + '.jpg')
    img2 = img2.resize((50, 100))
    img2 = img2.transpose(Image.ROTATE_270)

    canvas_img.paste(img1, (250, 650))
    canvas_img.paste(img2, (150, 875))

    d = ImageDraw.Draw(canvas_img)    #在图片下方显示对应的图片名
    d.text((150, 1700), 'toward ' + target, font=word_font, fill=(50, 50, 50))

    canvas_img.save(os.path.join('./foundImages/toward ' + target + '.jpg'))