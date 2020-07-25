import os
import json
import random
import pymysql
import sqlite3
import difflib

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def main():
    start_number = int(input('Input start number: '))
    end_number = int(input('Input end number: '))
    for folder_number in range(start_number, end_number + 1):
        conn = pymysql.connect(host='localhost',
                               port=3306,
                               user='root',
                               password='123456',
                               db='pro_info',
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        sql = 'SELECT pro_model, other_tag, all_img_new_path FROM products'
        cur = conn.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        cur.close()
        conn.close()
        if results:
            image_to_base_path = os.path.join('..', 'images', 'pinimg', str(folder_number))
            os.makedirs(image_to_base_path, exist_ok=True)
            image_from_base_path = os.path.join('..', 'images', 'media')

            for pro_info in results:
                pro_model = pro_info['pro_model']
                image_from_path = os.path.join(image_from_base_path, '%s.jpg' % pro_model)
                if not os.path.exists(image_from_path):
                    print('This product has no image skip!')
                    continue
                img_pinimg_path = os.path.join(image_to_base_path, '%s.jpg' % pro_model)
                if os.path.exists(img_pinimg_path):
                    print(pro_model, 'Is exists!')
                    continue
                other_tag = pro_info['other_tag']
                all_img_new_path = pro_info['all_img_new_path']
                watermark_word = random.choice(other_tag.split(',')).strip()
                all_img_new_path = json.loads(all_img_new_path)
                img_list = []
                for img_path in all_img_new_path:
                    img = img_path.split('###')[0].strip()
                    img_list.append(img)

                new_img_list = []
                while True:
                    if len(new_img_list) >= 2:
                        break
                    new_img = random.choice(img_list)
                    new_img_path = os.path.join(image_from_base_path, new_img)
                    if os.path.exists(new_img_path):
                        new_img_list.append(new_img_path)
                    else:
                        print('Unable to find image, rerandom!')
                        continue

                to_add_watermark = to_choice()
                screenshot_image(pro_model, to_add_watermark, new_img_list, watermark_word, image_to_base_path)


def to_choice():
    choice_list = [True, False]
    choice = random.choice(choice_list)

    return choice


def screenshot_image(pro_model, to_add_watermark, img_list, watermark_word, image_to_base_path, resize_num=0):
    cropped_list = []
    for i in img_list:
        to_transpose = to_choice()
        to_resize = to_choice()
        img = Image.open(i)
        size = img.size
        # 缩放 宽度大于1000 每组图只能缩放一个
        if to_resize and int(size[0]) >= 1000 and resize_num == 0:
            resize_width = 600
            resize_scale = resize_width / int(size[0])
            resize_height = int(int(size[1]) * resize_scale)
            img = img.resize((resize_width, resize_height), Image.ANTIALIAS) # Image.ANTIALIAS滤镜缩放，防止失真
            resize_num += 1
            size = (resize_width, resize_height)
        min_width = int(size[0]) / 12
        min_height = int(size[1]) / 12
        left, upper, right, lower = min_width * 3, 0, min_width * 9, size[1]
        cropped = img.crop((left, upper, right, lower))

        if to_transpose:
            cropped = cropped.transpose(Image.FLIP_LEFT_RIGHT)

        cropped_list.append(cropped)

    joint_image(pro_model, watermark_word, cropped_list[0], cropped_list[1], to_add_watermark, image_to_base_path)


def joint_image(pro_model, watermark_word, image1, image2, to_add_watermark, image_to_base_path, flag='horizontal'):
    sql = 'SELECT rgb_num FROM "color_library" ORDER BY RANDOM() LIMIT 1'
    sqlite_conn = sqlite3.connect("color_library.db")
    sqlite_cursor = sqlite_conn.cursor()
    rgb_num_r = sqlite_cursor.execute(sql)
    image_to_path = os.path.join(image_to_base_path, '%s.jpg' % pro_model)
    for i in rgb_num_r:
        rgb_num = eval(i[0])

    size1, size2 = image1.size, image2.size
    if flag == 'horizontal':
        if size1[1] >= size2[1]:
            height = size1[1]
            diff_heigh = size1[1] - size2[1]
            height1 = 0
            height2 = int(diff_heigh / 2)

        else:
            height = size2[1]
            diff_heigh = size2[1] - size1[1]
            height1 = int(diff_heigh / 2)
            height2 = 0
        joint = Image.new('RGB', (size1[0] + size2[0], height), rgb_num)
        loc1, loc2 = (0, height1), (size1[0], height2)
        joint.paste(image1, loc1)
        joint.paste(image2, loc2)
        if to_add_watermark:
            font_type = 'Inkfree.ttf'
            add_watermark(joint, height, font_type, watermark_word, rgb_num)
        joint.save(image_to_path)

        file_ex = os.path.exists(image_to_path)
        if file_ex:
            print(pro_model, 'Is done!')
        else:
            print(pro_model, 'Is False!')

    elif flag == 'vertical':
        joint = Image.new('RGB', (size1[0] + size2[0], height), rgb_num)
        loc1, loc2 = (0, 0), (0, size1[1])
        joint.paste(image1, loc1)
        joint.paste(image2, loc2)
        joint.save(image_to_path)

        file_ex = os.path.exists(image_to_path)
        if file_ex:
            print(pro_model, 'Is done!')
        else:
            print(pro_model, 'Is False!')


def add_watermark(joint, height, font_type, watermark_word, rgb_num):
    draw = ImageDraw.Draw(joint)
    font = ImageFont.truetype(font_type, 80)
    draw.text((80, height - 300), watermark_word, rgb_num, font=font)


if __name__ == '__main__':
    main()