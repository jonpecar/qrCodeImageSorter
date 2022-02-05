from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image
from typing import List
import os
import shutil

def read_qr_zbar(image_path : str) -> List:
    """
        Loads and scans image for qr code using pyzbar

        Arguments:
            image_path: path to image to scan
        
        Returns pyzbar results in list
    """
    im = Image.open(image_path)
    result = decode(im, symbols = [ZBarSymbol.QRCODE])
    return result

def get_qr(image_path : str, string_header : str = '') -> str:
    """
        Loads image and attempts to find a QR code
    
        Arguments:
            image_path: string indicating path of photo to scan
            string_header: optional string that indicates the header to look  for if one was use
                if a header is passed only QR codes with this header will be returned

        Returns a string indicating content of found QR code. Returns None if nothing found.

        Does not currently handle multiple QR codes. Will raise exception
    """
    results = read_qr_zbar(image_path)
    valid_results : List(str) = []
    for result in results:
        str_data :str = result.data.decode('utf-8')
        if str_data.startswith(string_header):
            str_data_no_head = str_data[len(string_header):]
            valid_results.append(str_data_no_head)
    
    if len(valid_results) > 1:
        raise Exception('Found multiple valid QR codes. Could not conclusively pick path')
    elif len(valid_results) == 1:
        return valid_results[0]
    else:
        return None

def sort_directory(input_dir : str, output_dir : str, string_header : str = '') -> List[str]:
    """
        Takes all images in a directory and sorts them by QR codes found in the images. Any
        images which are found before the first QR code will go into an "unsorted" folder in the directory.

        Parameters:
            input_dir: input directory containing photos as a string
            output_dir: target directory for photos, will be created if does not exist
            string_header: if a header is used in the QR codes to differentiate from other QR
                codes in the images, QR codes will be checked to ensure that the strings start
                with this substring

        Returns:
            List[str] of all paths found in QR codes
    """

    found_directories = []

    images = os.listdir(input_dir)
    os.makedirs(output_dir, exist_ok=True)

    current_path = os.path.join(output_dir, 'unsorted')
    for image in images:
        image_path = os.path.join(input_dir, image)
        qr_string = get_qr(image_path, string_header)
        if qr_string:
            current_path = os.path.join(output_dir, qr_string)
            if qr_string not in found_directories:
                found_directories.append(qr_string)
            
        os.makedirs(current_path, exist_ok=True)
        shutil.copyfile(image_path, os.path.join(current_path, image))

    found_directories.sort()
    return found_directories


