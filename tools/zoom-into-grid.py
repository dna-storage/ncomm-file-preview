from PIL import Image,ImageFilter,ImageFont,ImageDraw
from numpy import mean
from scipy.fftpack import *
from numpy import *

from dnastorage.codec.huffman_table import *

from dnapreview.jpeg.DCT import dct2


import sys

Q = ones( (8,8) )

#bsize = (24,24)
bsize = (16,16)

def get_font(size=9):
    font = ImageFont.truetype("Arial.ttf",size) #ImageFont.load_default() ImageFont.load_default()
    return font

def color_pick(val):
    if val<128:
        val = 255
    else:
        val = 0
    return val

def getYpixels(image,x,yz):
    y = []
    #assert image.size[0] == 8
    #assert image.size[1] == 8
    #print x, yz, x+8, yz+8, image.size
    assert x % 8 == 0
    assert yz % 8 == 0
    assert x >= 0 and x+8 <= image.size[0] 
    assert yz >= 0 and yz+8 <= image.size[1]
    for j in range(yz,min(image.size[1],yz+8)):
        yy = []
        cbcb = []
        crcr = []
        for i in range(x,min(image.size[0],x+8)):
            p = image.getdata().getpixel( (i,j) )
            yy.append(p)
        while len(yy) < 8:
            yy.append( yy[-1] )
        y.append(yy)

    while len(y) < 8:
        y.append( y[-1] )
    return array(y)


def xxxdct2(y):
    #return DCT.dct2(y)
    global Q
    R = []
    for yy in y:
        # normalize vector to +-128
        a = array(yy) - 128
        # perform dct and divide by 16 (8*2)
        r = dct(a) / 16
        R.append(r)
    #print transpose(array(R))
    R = transpose(array(R))
    newR = []
    for r in R:
        rr = dct(r) / 16
        newR.append(rr)
    R = transpose(array(newR))
    R = rint( R / Q )
    R = R.astype(int)
    return R

def draw_matrix(imto,imfrom):
    draw = ImageDraw.Draw(imto)
    font = get_font()
    im2 = imfrom.resize( (8,8) )
    d = list(im2.getdata())
    #size = (24,24)
    size = bsize
    pos = (0,0)
    for i,data in enumerate(d):
        s = " {:x}".format(data)
        sz = font.getsize(s)
        draw.text( pos, s, (color_pick(data)), font=font )
        pos = ( pos[0] + size[0], pos[1] )
        if (i+1)%8 == 0:
            pos = ( 0 , pos[1]+size[1] )
        #print sz            

def draw_dct(im):
    im2 = im.resize( (8,8) )
    Y = getYpixels(im2,0,0)
    Yp = list(array(Y).flatten())
    Y_dct = list(array(dct2(Y)).flatten())
    #draw = ImageDraw.Draw(im)
    n = Image.new("L",im.size,color=255)
    draw = ImageDraw.Draw(n)
    font = get_font()
    #size = (24,24) 
    size = bsize
    pos = (0,0)
    for i,data in enumerate(zip(Y_dct,Yp)):
        s = " {:x}".format(data[0])
        sz = font.getsize(s)
        #draw.text( pos, s, (color_pick(data[1])) )
        draw.text( pos, s, (0), font=font )
        pos = ( pos[0] + size[0], pos[1] )
        if (i+1)%8 == 0:
            pos = ( 0 , pos[1]+size[1] )
        #print sz
    return n
    

def draw_bands(image,box,loc,size):
    Y, Cb, Cr = box.split()

    Y = Y.resize(size)
    Cb = Cb.resize(size)
    Cr = Cr.resize(size)

    lmstrBlank = "".join( [ chr(128) for x in range(Y.size[0]*Y.size[1])] )
    blank = Image.frombuffer('L',Y.size,lmstrBlank,"raw",'L',0,1)
    Cbshow = Image.merge('YCbCr', (blank,Cb,blank))
    Crshow = Image.merge('YCbCr', (blank,blank,Cr))

    font = get_font(14)
    draw = ImageDraw.Draw(image)
    pos = loc
    for im,la in zip([Y,Cbshow,Crshow],['Y','Cb','Cr']):
        image.paste(im, (pos[0],pos[1],pos[0]+im.size[0],pos[1]+im.size[1]))
        draw.rectangle( (pos[0]-1,pos[1]-1,pos[0]+im.size[0]+1,pos[1]+im.size[1]+1) )
        #draw.text( (pos[0]+15,pos[1]-20), la, (0,0,0), font=font )
        pos = ( pos[0]+im.size[1]+20, pos[1] )



if len(sys.argv)==1:
    filename = 'obama.jpg'
    f = 10
elif len(sys.argv) > 1:
    filename = sys.argv[1]
    f = 5
    if len(sys.argv) > 2:
        f = int(sys.argv[2])

imt = Image.open(filename).convert('YCbCr')
imt.thumbnail( (imt.size[0]/f, imt.size[1]/f) )

crop_box = (112,100,120,108)
#crop_box = (90,130,98,138)
#crop_box = (0,0,8,8)

box = imt.crop( crop_box )

#box = box.resize( (8*24,8*24) )
box = box.resize( (8*bsize[0],8*bsize[1]) )

Y, Cb, Cr = box.split()

lmstrBlank = "".join( [ chr(128) for x in range(Y.size[0]*Y.size[1])] )
blank = Image.frombuffer('L',Y.size,lmstrBlank,"raw",'L',0,1)

Cbshow = Image.merge('YCbCr', (blank,Cb,blank))
Crshow = Image.merge('YCbCr', (blank,blank,Cr))


size = (imt.size[0]*4+60, imt.size[1]+120)
imstr = "".join( [ chr(255) for x in range(size[0]*size[1]*3) ] )
image = Image.frombuffer('RGB',size,imstr,"raw",'RGB',0,1).convert('YCbCr')

image.paste(imt, (0,0,0+imt.size[0],0+imt.size[1]))

image.paste(box, (imt.size[0]+20,20,imt.size[0]+20+box.size[0],20+box.size[1]))

Y_dct = Y.copy()

draw_matrix(Y,Y)
draw_matrix(Crshow,Cr)
draw_matrix(Cbshow,Cb)
Y_dct = draw_dct(Y_dct)

draw = ImageDraw.Draw(image)
draw.rectangle((imt.size[0]+20,20,imt.size[0]+20+box.size[0],20+box.size[1]))

pos = (imt.size[0]+20+box.size[0]+20,20)
for im in [Y]:
    image.paste(im, (pos[0],pos[1],pos[0]+im.size[0],pos[1]+im.size[1]))
    draw.rectangle( (pos[0]-1,pos[1]-1,pos[0]+im.size[0]+1,pos[1]+im.size[1]+1) )
    pos = ( pos[0], pos[1]+im.size[1]+20 )

pos = (imt.size[0]+20+box.size[0]+Y.size[0]+40,20)
image.paste( Y_dct, (pos[0],pos[1],pos[0]+Y_dct.size[0],pos[1]+Y_dct.size[1]) )

draw.rectangle( (crop_box[0]-1,crop_box[1]-1,crop_box[2]+1,crop_box[3]+1)  )
draw.line( [(crop_box[2]+1,crop_box[1]-1), (imt.size[0]+20,20)] )
draw.line( [(crop_box[2]+1,crop_box[3]+1), (imt.size[0]+20,box.size[1]+20)] )

draw_bands(image,box,[imt.size[0]+20,imt.size[1]-10],(50,50))

image.show()
image.save("example.jpg")
