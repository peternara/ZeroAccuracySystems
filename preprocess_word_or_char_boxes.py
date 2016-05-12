import dirs
import os
import shutil
from PIL import Image
#import cv2

#def preprocess_image(image):
    # Otsu's thresholding after Gaussian filtering
    #blured_image = cv2.GaussianBlur(image,(5,5),0)
    #histogram,binary_image = cv2.threshold(blured_image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

#    return binary_image

source_dir_path = dirs.KNMP_CHAR_BOXES_DIR_PATH
target_dir_path = dirs.KNMP_PROCESSED_CHAR_BOXES_DIR_PATH
#source_dir_path = dirs.KNMP_WORD_BOXES_DIR_PATH
#target_dir_path = dirs.KNMP_PROCESSED_WORD_BOXES_DIR_PATH

# Delete target directory
if os.path.exists(target_dir_path):
    shutil.rmtree(target_dir_path)
os.makedirs(target_dir_path)

for source_label_dir_name in [f for f in os.listdir(source_dir_path) if os.path.isdir(os.path.join(source_dir_path, f))]:
    source_label_dir_path = os.path.join(source_dir_path, source_label_dir_name)
    target_label_dir_path = os.path.join(target_dir_path, source_label_dir_name)

    os.makedirs(target_label_dir_path)

    source_file_names = [f for f in os.listdir(source_label_dir_path) if f.endswith(".png")]
    for source_file_name in source_file_names:
        source_file_path = os.path.join(source_label_dir_path, source_file_name)
        target_file_path = os.path.join(target_label_dir_path, source_file_name)

        print(target_file_path)

        image = Image.open(source_file_path)
        image = image.convert("LA") # Greyscale

        #print("%d\t%d" % (image.width, image.height))

        # Word width: average 91.4, std 65.6
        # Word height: average 56.7, std 11.9

        # Char width: average 29.9, std 8.8
        # Char height: average 60.0, std 11.4

        resize_ratio = 0.5
        new_width = 28#int(image.width*resize_ratio)
        new_height = 28
        image = image.resize((new_width,new_height))

        image.save(target_file_path)

        #shutil.copyfile(source_file_path,target_file_path)