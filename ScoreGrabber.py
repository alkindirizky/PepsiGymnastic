import pyscreenshot
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import time

# various part coordinate (left, upper, right, lower) for 1440 x 1080
_coor_scene = (795, 224, 870, 283)
_coor_score = (900, 546, 1320, 612)
_coor_time = (850, 790, 1310, 860)

# ideal aspect ratio
_ideal_width = 1440
_ideal_height = 1080
_ideal_aspect = _ideal_width / float(_ideal_height)

def _get_score(im, debug = False):
    start = time. time()
    im = _rescale_screen(im, debug)

    #crop to various part
    im_scene = im.crop(_coor_scene)
    im_score = im.crop(_coor_score)
    im_time = im.crop(_coor_time)

    #image echancement
    im_scene = im_scene.filter(ImageFilter.GaussianBlur(3))
    im_score = im_score.filter(ImageFilter.GaussianBlur(3))
    im_time = im_time.filter(ImageFilter.GaussianBlur(3))

    #thresholding
    im_scene = _white_thresholding(im_scene, 130)
    im_score = _white_thresholding(im_score, 130)
    im_time = _white_thresholding(im_time, 130)

    #resampling
    im_scene = im_scene.resize(tuple([8 * x for x in im_scene.size]), Image.BILINEAR)
    im_score = im_score.resize(tuple([8 * x for x in im_score.size]), Image.BILINEAR)
    im_time = im_time.resize(tuple([8 * x for x in im_time.size]), Image.BILINEAR)

    # obtain the text, currently whitelist doesnt work with v4.0
    # psm 7 -> Treat the image as a single text line
    # psm 10 ->as single character
    text_scene = pytesseract.image_to_string(im_scene, config=' --psm 10', lang = 'digits_comma')
    text_score = pytesseract.image_to_string(im_score, config='--psm 7', lang = 'eng')
    text_time = pytesseract.image_to_string(im_time, config='--psm 7', lang = 'eng')
    end = time.time()

    if debug:
        im_scene.save('scene.jpg')
        im_score.save('score.jpg')
        im_time.save('time.jpg')
        print(text_scene)
        print(text_score)
        print(text_time)
        print("Process Time : {0:.3f} secs".format(end - start))
    
    return text_scene, text_score, text_time

def _rescale_screen(im, debug = False):
    #rescale to 1080p
    if im.size[1] != _ideal_height:
        scale = _ideal_height / float(im.size[1]) 
        im = im.resize((int(scale * im.size[0]), 1080), Image.NEAREST)

    width = im.size[0]
    height = im.size[1]
    aspect = width / float(height)

    if aspect > _ideal_aspect:
        new_width = int(_ideal_aspect * height)
        offset = (width - new_width) / 2
        resize = (offset, 0, width - offset, height)

    im = im.crop(resize)
    if debug:
        im.save('rescale.jpg')
    
    return im

def _white_thresholding(im, white_lvl):
    pixels = im.getdata()
    newData = []
    for item in pixels:
        if item[0] >= white_lvl and item[1] >= white_lvl and item[2] >= white_lvl:
            newData.append((255, 255, 255))
        else:
            newData.append((0, 0, 0))

    im = Image.new(im.mode, im.size)
    im.putdata(newData)
    return im.convert('L')

def main():
    while True:
        data = _get_score(pyscreenshot.grab())
        slashidx = data[1].find('/')

        if slashidx > 0:
            try:
                score = int(data[1][:slashidx])
                print("Score", score)
            except:
                pass
        else:
            print("NO DATA")

        print(data)
        time.sleep(1)

if __name__ == "__main__":
    main()