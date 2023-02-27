from PIL import Image, ImageDraw, ImageFont
import os

def behind(source, target, prep):
    bound:list = []
    bound.append(source)
    bound.append(target)
    bound.append(prep)

    word_font = ImageFont.truetype('./font/Arial.ttf', 40)

    ##首先生成生成图的画布，若是考虑位置关系的话，画布大小需要更改    
    canvas_width = 800
    canvas_height = 1800
    canvas_img = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))

    img1 = Image.open('./foundImages/' + bound[1] + '.jpg')
    img1 = img1.resize((500, 500))    #调整图片大小
    img2 = Image.open('./foundImages/' + bound[0] + '.jpg')
    img2 = img2.resize((200, 200))
    canvas_img.paste(img2, (300, 550))#先画靠后的图片
    canvas_img.paste(img1, (150, 750))#再画靠前的图片
    d = ImageDraw.Draw(canvas_img)    #在图片下方显示对应的图片名
    d.text((150, 1700), bound[0] + ' ' + bound[2] + ' ' + bound[1], font=word_font, fill=(50, 50, 50))

    canvas_img.save(os.path.join('./foundImages/',bound[0] + ' ' + bound[2] + ' ' + bound[1] + '.jpg'))