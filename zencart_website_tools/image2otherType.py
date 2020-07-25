import os
import sys
import shutil

from PIL import Image


# Define the input and output image
output_dir = './media/'
if not os.path.exists(output_dir):
    os.mkdir(output_dir)


def image_to_other_type(dataset_dir, type):
    files = []
    image_list = os.listdir(dataset_dir)
    files = [os.path.join(dataset_dir, _) for _ in image_list]
    files_length = len(files)

    for index, old_type_img in enumerate(files):

        if index > 100000:
            break

        try:
            sys.stdout.write('\r>>Converting image %d/%d ' % (index + 1, files_length))
            sys.stdout.flush()
            im = Image.open(old_type_img)
            new_type_img = os.path.splitext(old_type_img)[0] + "." + type
            im.save(new_type_img)
            shutil.move(new_type_img, output_dir)

        except IOError as e:
            print('could not read:', old_type_img)
            print('error:', e)
            print('skip it\n')

    sys.stdout.write('Convert Over!\n')
    sys.stdout.flush()


if __name__ == "__main__":
    current_dir = os.getcwd()
    data_dir = os.sep.join([current_dir, 'media_untreated'])
    print(data_dir)

    image_to_other_type(data_dir, 'jpg')
