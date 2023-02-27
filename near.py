# from near import near
# near('cat','apple','near')

from PIL import Image, ImageDraw, ImageFont
import os
import random

def near(source, target, prep):
    bound:list = []
    bound.append(source)
    bound.append(target)
    bound.append(prep)

    a = 0
    if bound[2] == 'left':
        a = 1
    elif bound[2] == 'right':
        a = 2
    else:
        a = random.randint(1,2)               #near并未指明左右关系，所以通过随机数生成左右关系

    word_font = ImageFont.truetype('./font/Arial.ttf', 40)

    ##首先生成生成图的画布，若是考虑位置关系的话，画布大小需要更改    
    canvas_width = 1300
    canvas_height = 1800
    canvas_img = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))

    if a == 1:
        img1 = Image.open('./foundImages/' + bound[1] + '.jpg')
        img1 = img1.resize((500, 500))    #调整图片大小
        img2 = Image.open('./foundImages/' + bound[0] + '.jpg')
        img2 = img2.resize((500, 500))
    else:
        img1 = Image.open('./foundImages/' + bound[0] + '.jpg')
        img1 = img1.resize((500, 500))    #调整图片大小
        img2 = Image.open('./foundImages/' + bound[1] + '.jpg')
        img2 = img2.resize((500, 500))

    canvas_img.paste(img1, (650, 650))#先画靠右的图片
    canvas_img.paste(img2, (150, 650))#再画靠左的图片
    
    d = ImageDraw.Draw(canvas_img)    #在图片下方显示对应的图片名
    d.text((150, 1700), bound[0] + ' ' + bound[2] + ' ' + bound[1], font=word_font, fill=(50, 50, 50))

    canvas_img.save(os.path.join('./foundImages/',bound[0] + ' ' + bound[2] + ' ' + bound[1] + '.jpg'))