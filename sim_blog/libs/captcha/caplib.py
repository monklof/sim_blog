"""Captcha lib for generating random captcha"""

import random
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import string

class CaptchaGenerator:
    """Use gen() to create a new captcha"""

    def __init__(self, path="."):
        """@path: the path to store captcha pictures"""
        self.path = path
        if not os.path.exists(path):
            os.makedirs(path)

    def create_one(self):
        """gen a new captcha code picture
        @return (captcha, filename, absolute filename)
        """
        img, code = self._create_captcha()
        code = code.lower()
        filename = self._gen_filename(self.path, self._img_type)
        absname = os.path.join(self.path, filename)
        img.save(absname, self._img_type)
        return code, filename, absname

    def _gen_filename(self, path, extension, length=8):
        max_try = 10
        while True:
            f = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
            filename="{0}.{1}".format(f, extension)
            absname = os.path.join(path, filename)
            if not os.path.exists(absname):
                break;
            max_try -= 1
            if max_try < 0:
                raise Exception("captcha image filename resource exhausted")
        return filename

    _font = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Monaco.ttf")
    # remove confusing chars like 'i', 'l', 'o', 'z', '0', '1', '2'
    _chars = "abcdefghjkmnpqrstuvwxyABCDEFGHJKMNPQRSTUVWXY3456789"
    _img_type = "PNG"
    
    def _create_captcha(self,
                        code_len=4,
                        size=(120, 30),
                        chars=None,
                        img_type=None,
                        mode="RGB",
                        bg_color=(255, 255, 255),
                        fg_color=(0, 0, 255),
                        font_size=18,
                        font=None,
                        draw_lines=True,
                        n_line=(1, 2),
                        draw_points=True,
                        point_chance = 2):
        """generate a new captcha pic
        @param size: (width, height) of the captcha pic
        @param chars: the charset to create captcha pic
        @param img_type: in [GIF，JPEG，TIFF，PNG]
        @param mode: the mode of the captcha pic
        @param bg_color: 
        @param fg_color: 
        @param font_size: 
        @param font: 
        @param code_len: 
        @param draw_lines: draw disturbing lines
        @param n_lines: disturbing line number range 
        @param draw_points: draw disturbing points
        @param point_chance: the chance of disturbing points occuring, in [0, 100]
        @return: [0]: PIL Image instance
        @return: [1]: the capture code
        """
        if not chars: chars = CaptchaGenerator._chars
        if not img_type: img_type = CaptchaGenerator._img_type
        if not font: font=CaptchaGenerator._font
        
        width, height = size 
        img = Image.new(mode, size, bg_color)
        # paint brush
        draw = ImageDraw.Draw(img) 
        if draw_lines:
            # draw disturbing lines
            line_num = random.randint(n_line[0],n_line[1])
            for i in range(line_num):
                begin = (random.randint(0, width), random.randint(0, height))
                end = (random.randint(0, width), random.randint(0, height))
                draw.line([begin, end], fill=(0, 0, 0))
        if draw_points:
            chance = min(100, max(0, int(point_chance)))
            for w in range(width):
                for h in range(height):
                    tmp = random.randint(0, 100)
                    if tmp > 100 - chance:
                        draw.point((w, h), fill=(0, 0, 0))
        # draw code strs
        c_chars = random.sample(chars, code_len)
        strs = ' %s ' % ' '.join(c_chars) # 每个字符前后以空格隔开
        font = ImageFont.truetype(font, font_size)
        font_width, font_height = font.getsize(strs)
        draw.text(((width - font_width) / 3, (height - font_height) / 3),strs, font=font, fill=fg_color)
        code = "".join(c_chars)

        # image distort params
        params = [1 - float(random.randint(1, 2)) / 100,
                  0,
                  0,
                  0,
                  1 - float(random.randint(1, 10)) / 100,
                  float(random.randint(1, 2)) / 500,
                  0.001,
                  float(random.randint(1, 2)) / 500
              ]
        # distort the image
        img = img.transform(size, Image.PERSPECTIVE, params) 
        # 滤镜，边界加强（阈值更大）
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        return img, code

