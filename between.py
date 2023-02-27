# from between import between
# between('cat','house','hill','between')

from PIL import Image, ImageDraw, ImageFont
import os

def between(source, target1,target2, prep):
    bound:list = []
    bound.append(source)
    bound.append(target1)
    bound.append(target2)
    bound.append(prep)

    word_font = ImageFont.truetype('./font/Arial.ttf', 40)

    ##首先生成生成图的画布，若是考虑位置关系的话，画布大小需要更改    
    canvas_width = 1800
    canvas_height = 1800
    canvas_img = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))

    img1 = Image.open('./foundImages/' + bound[0] + '.jpg')
    img1 = img1.resize((500, 500))    #调整图片大小
    img2 = Image.open('./foundImages/' + bound[1] + '.jpg')
    img2 = img2.resize((500, 500))
    img3 = Image.open('./foundImages/' + bound[2] + '.jpg')
    img3 = img3.resize((500, 500))
    img4 = Image.open('./foundImages/' + 'arrowhead' + '.jpg')
    img4 = img4.resize((50, 100))
    img4 = img4.transpose(Image.ROTATE_180)

    canvas_img.paste(img1, (650, 650))
    canvas_img.paste(img2, (150, 650))
    canvas_img.paste(img3, (1150, 650))
    canvas_img.paste(img4, (875, 550))

    d = ImageDraw.Draw(canvas_img)    #在图片下方显示对应的图片名
    d.text((150, 1700), bound[0] + ' ' + bound[3] + ' ' + bound[1] + ' and ' + bound[2], font=word_font, fill=(50, 50, 50))

    canvas_img.save(os.path.join('./foundImages/',bound[0] + ' ' + bound[3] + ' ' + bound[1] + ' and ' + bound[2] + '.jpg'))