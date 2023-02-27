from PIL import Image

def change(address):
    img = Image.open(address)
    img = img.convert('RGB')
    width = img.size[0]
    height = img.size[1]
    change = (img.getpixel((0,0)))
    for x in range(width):
        for y in range(height):
            data = (img.getpixel((x,y)))
            if (data[0]==change[0] and data[1]==change[1] and data[2]==change[2]):    #以图片第一个像素点的颜色作为背景主色
                img.putpixel((x,y),(255,255,255))
            elif (data[0]>=210 and data[1]>=210 and data[2]>=210):                    #考虑到网络上有很多RGBA截图生成的RGB图片可能被检索到，故将该种图片特有的灰色也作为修改色之一
                img.putpixel((x,y),(255,255,255))
    img.save(address)