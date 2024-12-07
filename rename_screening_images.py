"""
rename images for screening experiments.

remove unused classification codes
change 'txt' to 'text' in file names for iconic text stimuli.

examples = [
    "lumpy_princess_adventure_001_time_005_id004107_1000000000000000000000110100.jpg",
    "adam_sandler_snl_001_id002040_1000001100000000000000110000.jpg",
    "adam_sandler_snl_001_txt_id002040_1000001100000000000000110000.jpg",
    "0_001_id003353_1000001100000000000000110010.jpg",
    "13_reasons_why_001_id002477_1000000100000000000000110000.jpg",
    "ayers_rock_text2_001_id004158_0100000000000010100000000010.jpg",
    "atlantis_1_001_id004483_0100000000000000000000000010_text.jpg",
    "eva-green-casino-royale-james_bond_vesper_lynd_01_001_id003287_1000000100000000000000110001.jpg",
    "modernfamily_cammitch.jpg_001_id001567_1000001100000000000000110000.jpg"
    "lora_parrot_spanish_text_1.jpg_001_id003358_0010000000000000000100010010.jpg",
    "sphinx-egypt_001_id001905_0100000000000011000000000000 2.jpg",
    "jim_hopper_stranger_things_text_1_001_id999999999999999983222784_1000001100000000000000111010.jpg",
]

"""

# TODO: use parallel jobs to copy files.
# TODO: create IO files to avoid duplicates.

import os
import re
import glob
import csv
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from mne.io.curry.curry import FILE_EXTENSIONS

INPUT_PATH = "/Users/XinNiuAdmin/Library/CloudStorage/Box-Box/finished_gallery_renamed_women_coded"
OUTPUT_PATH = "/Users/XinNiuAdmin/Library/CloudStorage/Box-Box/ScreeningStimuli/images"
LOG_FILE = "/Users/XinNiuAdmin/Library/CloudStorage/Box-Box/ScreeningStimuli/images_rename_log.csv"

CLASS_CODE_INDEX = [0, 2, 15, 6, 27]  # [People Animals Buildings Men Plants]
DELETE_EXISTING_FILES = True
FILE_EXTENSION = '.jpg'


def make_name(img_name:str, index:int, class_code:str, suffix:str) -> str:

    if re.search(r'te?xt_?\d', img_name) or suffix == '_text':
        text = "_text"
    else:
        text = ""

    img_name = re.sub(r'_\d{3}.*', '', img_name)
    img_name = re.sub(r'_?\.jpg.*', '', img_name)
    img_name = re.sub(r'_te?xt.*', '', img_name)
    img_name = img_name.replace('_', '-')

    # class_code = ''.join(class_code[i] for i in CLASS_CODE_INDEX)
    # add additional code 0 in the 4th position:
    if len(class_code) < 6:
        print("modify class code.")
        class_code = class_code[:4] + '0' + class_code[4:]
    else:
        print("use current class code.")

    new_name = f"{img_name}{text}_id{index:06d}_{class_code}{FILE_EXTENSION}"
    return new_name


def rename_image(img_path:str, image_id:int) -> Optional[str]:
    img = os.path.basename(img_path)
    # Update regex based on your requirements
    match = re.search(r'(^[\w.\'&()\[\]\u0300-\u036F-]*)_(i?d\d{6,24})_(\d{5,6})(.*)?.jpg', img)
    if match:
        img_name, id_code, class_code, suffix = match.groups()
        new_name = make_name(img_name, image_id, class_code, suffix)
        dest_file = os.path.join(OUTPUT_PATH, new_name)
        if os.path.exists(dest_file):
            print(f"skip exist: {new_name}")
        else:
            shutil.copy(img_path, dest_file)
            print(f"rename file: {img} to {new_name}")
            return new_name
    else:
        print(f"not matched: {img}")

    return None

if __name__ == "__main__":

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH, exist_ok=True)

    image_files = glob.glob(os.path.join(INPUT_PATH, f'*{FILE_EXTENSION}'))
    renamed_files = glob.glob(os.path.join(OUTPUT_PATH, '*'))
    if DELETE_EXISTING_FILES:
        for file in renamed_files:
            if os.path.isfile(file):
                print(f"remove existing file: {file}")
                os.remove(file)

        start_index = 0
    else:
        start_index = len(renamed_files)

    renamed_files = []
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(rename_image, img_path, start_index + idx): img_path
            for idx, img_path in enumerate(image_files)
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                renamed_files.append(result)

    with open(LOG_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(renamed_files)  # Write each tuple as a row

