import os
import re
import json
import random
import sqlite3
import pymysql
import configparser

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from dbconnection import op_select_one
from dbconnection import op_select_all
from dbconnection import op_commit


def main():
    start_number = int(input('Input start number: '))
    end_number = int(input('Input end number: '))
    compound_mode = 'vertical'
    image_base_folder_name = 'images'
    image_from_base_path = os.path.join('..', image_base_folder_name)
    conf = './config.ini'
    conf_conn = configparser.ConfigParser()
    conf_conn.read(conf, encoding='utf-8')
    wdweb_items = conf_conn.items('mysql_wdweb')
    wdweb_items = dict(wdweb_items)
    wdweb_conn = pymysql.connect(host='localhost',
                                 port=3306,
                                 db=wdweb_items['db'],
                                 user=wdweb_items['user'],
                                 password=wdweb_items['password'],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    sql = 'SELECT products_model, products_image, products_status FROM products WHERE products_status=1'
    results = op_select_all(wdweb_conn, sql)
    wdweb_conn.close()
    if results:

        read_flag = 1
        files = None
        for folder_number in range(start_number, end_number + 1):
            image_to_base_path = os.path.join(
                '..', image_base_folder_name, 'pinimg', str(folder_number))
            os.makedirs(image_to_base_path, exist_ok=True)

            for res in results:
                pro_model = res['products_model']
                pro_image = res['products_image']
                middle_path_split = pro_image.split('/')
                middle_path_split.pop()
                middle_path = '/'.join(middle_path_split)

                if read_flag == 1:
                    image_from_path_middle = os.path.join(
                        image_from_base_path, middle_path)
                    for root, dirs, files in os.walk(image_from_path_middle):
                        read_flag = 0

                if files:
                    img_list = list(filter(lambda x: re.match(
                        '%s.*' % pro_model, x) != None, files))
                    image_from_path = os.path.join(
                        image_from_base_path, pro_image)

                    if not os.path.exists(image_from_path):
                        print('%s has no image skip!' % pro_model)
                        continue
                    img_pinimg_path = os.path.join(
                        image_to_base_path, pro_image.split('/')[-1])

                    if os.path.exists(img_pinimg_path):
                        print(pro_model, 'Is exists!')
                        continue

                    # 水印功能已取消
                    watermark_word = ''
                    new_img_list = []
                    while True:

                        if len(new_img_list) >= 3:
                            break
                        new_img = random.choice(img_list)
                        new_img_path = os.path.join(
                            image_from_base_path, middle_path, new_img)
                        new_img_list.append(new_img_path)

                        if len(img_list) >= 2:
                            img_list.remove(new_img)

                    # to_add_watermark = to_choice()
                    to_add_watermark = False
                    screenshot_image(
                        pro_model, to_add_watermark, new_img_list, watermark_word, img_pinimg_path, compound_mode)

                else:
                    print('Folder empty!')
                    break


def to_choice():
    choice_list = [True, False]
    choice = random.choice(choice_list)

    return choice


def screenshot_image(pro_model, to_add_watermark, img_list, watermark_word, img_pinimg_path, compound_mode, resize_num=0):
    cropped_list = []
    width_1, height_1, width_2, height_2 = 0, 0, 0, 0
    to_vertical_height = 0
    number_of_processing = 1
    for i in img_list:
        to_transpose = to_choice()
        to_resize = to_choice()
        img = Image.open(i)
        size = img.size
        if compound_mode == 'horizontal':

            if number_of_processing > 2:
                break
            # 缩放 宽度大于1000 每组图只能缩放一个
            if to_resize and int(size[0]) >= 1000 and resize_num == 0:
                resize_width = 600
                resize_scale = resize_width / int(size[0])
                resize_height = int(int(size[1]) * resize_scale)
                img = img.resize((resize_width, resize_height),
                                 Image.ANTIALIAS)  # Image.ANTIALIAS滤镜缩放，防止失真
                resize_num += 1
                size = (resize_width, resize_height)
            min_width = int(size[0]) / 12
            min_height = int(size[1]) / 12
            left, upper, right, lower = min_width * \
                3, 0, min_width * 9, size[1]

        elif compound_mode == 'vertical':

            if number_of_processing == 1:
                width_1 = int(size[0])
                height_1 = int(size[1])
                left, upper, right, lower = 0, 0, size[0], size[1]

            elif number_of_processing == 2:
                width_2 = int(width_1 / 2)
                resize_scale = width_2 / int(size[0])
                height_2 = int(size[1] * resize_scale)
                img = img.resize((width_2, height_2), Image.ANTIALIAS)
                left, upper, right, lower = 0, 0, width_2, height_2

            elif number_of_processing == 3:
                resize_scale = width_2 / int(size[0])
                height_3 = int(size[1] * resize_scale)
                img = img.resize((width_2, height_3), Image.ANTIALIAS)
                left, upper, right, lower = 0, 0, width_2, height_3

            to_vertical_height = height_1 + height_2

        cropped = img.crop((left, upper, right, lower))

        if to_transpose:
            cropped = cropped.transpose(Image.FLIP_LEFT_RIGHT)

        cropped_list.append(cropped)
        number_of_processing += 1

    joint_image(pro_model, watermark_word,
                cropped_list, to_add_watermark, img_pinimg_path, compound_mode, width_1, height_1, width_2, to_vertical_height)


def joint_image(pro_model,
                watermark_word,
                cropped_list,
                to_add_watermark,
                img_pinimg_path,
                compound_mode,
                width_1,
                height_1,
                width_2,
                to_vertical_height):
    sql = 'SELECT rgb_num FROM "color_library" ORDER BY RANDOM() LIMIT 1'
    sqlite_conn = sqlite3.connect("color_library.db")
    sqlite_cursor = sqlite_conn.cursor()
    rgb_num_r = sqlite_cursor.execute(sql)
    image_to_path = os.path.join(img_pinimg_path)
    for i in rgb_num_r:
        rgb_num = eval(i[0])

    size1, size2 = cropped_list[0].size, cropped_list[1].size
    if len(cropped_list) > 2:
        size3 = cropped_list[2].size

    if compound_mode == 'horizontal':
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
        joint.paste(cropped_list[0], loc1)
        joint.paste(cropped_list[1], loc2)
        if to_add_watermark:
            font_type = 'Inkfree.ttf'
            add_watermark(joint, height, font_type, watermark_word, rgb_num)
        joint.save(image_to_path)

        file_ex = os.path.exists(image_to_path)

        if file_ex:
            print(pro_model, 'Is done!')
        else:
            print(pro_model, 'Is False!')

    elif compound_mode == 'vertical':
        joint = Image.new(
            'RGB', (width_1, to_vertical_height), rgb_num)
        loc1, loc2, loc3 = (
            0, 0), (0, height_1), (width_2, height_1)
        joint.paste(cropped_list[0], loc1)
        joint.paste(cropped_list[1], loc2)
        joint.paste(cropped_list[2], loc3)
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
