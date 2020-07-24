import os
import json
import random
import pymysql
import sqlite3

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def main():
    conn = pymysql.connect(host='localhost',
                           port=3306,
                           user='root',
                           password='123456',
                           db='pro_info',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    sql = 'SELECT pro_model, other_tag, all_img_new_path FROM products limit 3'
    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    if results:
        for pro_info in results:
            pro_model = pro_info['pro_model']
            other_tag = pro_info['other_tag']
            all_img_new_path = pro_info['all_img_new_path']
            watermark_word = random.choice(other_tag.split(',')).strip()
            all_img_new_path = json.loads(all_img_new_path)
            img_list = []
            for img_path in all_img_new_path:
                img = img_path.split('###')[0].strip()
                img_list.append(img)

            if len(img_list) >= 2:
                new_img_list = []
                for i in range(2):
                    new_img_list.append(random.choice(img_list))

            to_transpose = to_choice()
            to_add_watermark = to_choice()
            screenshot_image(to_transpose, to_add_watermark, new_img_list, watermark_word)


def to_choice():
    choice_list = [True, False]
    choice = random.choice(choice_list)

    return choice


def screenshot_image(to_transpose, to_add_watermark, new_img_list, watermark_word):
    temp_image_list = []
    for i in img_list:
        img = Image.open(i)
        size = img.size
        min_width = int(size[0]) / 12
        min_height = int(size[1]) / 12
        left, upper, right, lower = min_width * 3, 0, min_width * 9, size[1]
        cropped = img.crop((left, upper, right, lower))
        new_name = i.split('.')[0] + '_temp' + '.jpg'
        temp_image_path = './temp_images/' + new_name
        if to_transpose:
            cropped.transpose(Image.FLIP_LEFT_RIGHT).save(temp_image_path)
        else:
            cropped.save(temp_image_path)

        temp_image_list.append(temp_image_path)

    joint_image(temp_image_list[0], temp_image_list[1], to_add_watermark)


def joint_image(image1, image2, to_add_watermark, flag='horizontal'):
    sql = 'SELECT rgb_num FROM "color_library" ORDER BY RANDOM() LIMIT 1'
    sqlite_conn = sqlite3.connect("color_library.db")
    sqlite_cursor = sqlite_conn.cursor()
    rgb_num_r = sqlite_cursor.execute(sql)
    for i in rgb_num_r:
        rgb_num = eval(i[0])

    img1, img2 = Image.open(image1), Image.open(image2)
    size1, size2 = img1.size, img2.size
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
        joint.paste(img1, loc1)
        joint.paste(img2, loc2)
        if to_add_watermark:
            font_type = 'Inkfree.ttf'
            add_watermark(joint, height, font_type, watermark_word, rgb_num)
        joint.save('horizontal%s.jpg' % i)

        file_ex = os.path.exists('horizontal.jpg')
        if file_ex:
            print('Image is done!')
        else:
            print('Image is False!')

    elif flag == 'vertical':
        joint = Image.new('RGB', (size1[0] + size2[0], height), rgb_num)
        loc1, loc2 = (0, 0), (0, size1[1])
        joint.paste(img1, loc1)
        joint.paste(img2, loc2)
        joint.save('vertical.jpg')

        file_ex = os.path.exists('vertical.jpg')
        if file_ex:
            print('Image is done!')
        else:
            print('Image is False!')


def add_watermark(joint, height, font_type, watermark_word, rgb_num):
    draw = ImageDraw.Draw(joint)
    font = ImageFont.truetype(font_type, 80)
    draw.text((80, height - 300), watermark_word, rgb_num, font=font)


if __name__ == '__main__':
    main()
