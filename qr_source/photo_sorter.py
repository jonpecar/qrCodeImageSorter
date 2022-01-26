from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image
from typing import List
import os
import shutil

def read_qr_zbar(image_path : str):
    im = Image.open(image_path)
    result = decode(im, symbols = [ZBarSymbol.QRCODE])
    return result

def get_qr(image_path : str, string_header : str = ''):
    results = read_qr_zbar(image_path)
    valid_results : List(str) = []
    for result in results:
        str_data :str = result.data.decode('utf-8')
        if str_data.startswith(string_header):
            valid_results.append(str_data)
    
    if len(valid_results) > 1:
        raise Exception('Found multiple valid QR codes. Could not conclusively pick path')
    elif len(valid_results) == 1:
        return valid_results[0]
    else:
        return None

def sort_directory(input_dir : str, output_dir : str, string_header : str = ''):
    """
        Takes all images in a directory and sorts them by QR codes found in the images. Any
        images which are found before the first QR code will go into an "unsorted" folder in the directory.

        Parameters:
            input_dir: input directory containing photos as a string
            output_dir: target directory for photos, will be created if does not exist
            string_header: if a header is used in the QR codes to differentiate from other QR
                codes in the images, QR codes will be checked to ensure that the strings start
                with this substring
    """
    images = os.listdir(input_dir)
    os.makedirs(output_dir, exist_ok=True)

    current_path = os.path.join(output_dir, 'unsorted')
    for image in images:
        image_path = os.path.join(input_dir, image)
        if get_qr(image_path, string_header):
            current_path = os.path.join(output_dir, get_qr(image_path, string_header))
        os.makedirs(current_path, exist_ok=True)
        shutil.copyfile(image_path, os.path.join(current_path, image))


