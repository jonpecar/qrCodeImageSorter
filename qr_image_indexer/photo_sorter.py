from pyzbar.pyzbar import decode, ZBarSymbol
import cv2
from typing import List, Tuple, Dict
from multiprocessing import Pool, cpu_count
import os
import shutil
from functools import partial
import tqdm

def read_qr_zbar(image_path : str, binarization : bool = False) -> List:
    """
        Loads and scans image for qr code using pyzbar. Processes raw image first. If it fails to find a QR code will
        try again with binarization using OpenCV with OTSU threshold finding.

        Arguments:
            image_path: path to image to scan
        
        Returns pyzbar results in list
    """
    im = cv2.imread(image_path)
    result = decode(im, symbols = [ZBarSymbol.QRCODE])
    if not result and binarization:
        im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        thres, im_binarized = cv2.threshold(im_gray, 128, 255, cv2.THRESH_OTSU)
        result = decode(im_binarized, symbols = [ZBarSymbol.QRCODE])
    return result

def get_qr(image_path : str, string_header : str = '', binarization : bool = False) -> str:
    """
        Loads image and attempts to find a QR code
    
        Arguments:
            image_path: string indicating path of photo to scan
            string_header: optional string that indicates the header to look  for if one was use
                if a header is passed only QR codes with this header will be returned

        Returns a string indicating content of found QR code. Returns None if nothing found.

        Does not currently handle multiple QR codes. Will raise exception
    """
    results = read_qr_zbar(image_path, binarization)
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

def get_qr_mt(image_path : str, string_header : str = '', binarization : bool = False) -> Tuple[str, str]:
    """
        Calls get_qr and returns image path and result of get_qr in a tuple to allow multiprocessing

        Arguments:
            image_path: string indicating path of photo to scan
            string_header: optional string that indicates the header to look  for if one was use
                if a header is passed only QR codes with this header will be returned

    """
    return image_path, get_qr(image_path, string_header, binarization)

def get_qr_for_files(files : List[str], string_header : str = '', verbose : bool = False, binarization : bool = False) -> Dict[str, str]:
    '''
        Process a list of files using multiprocessing. Will return dictionary of each images'
        result against it's filename as a key

        Arguments:
            files: list of file paths as string
            string_header: string header used in images if any
            verbose: boolean indicating whether to show progress updates to terminal

        Returns:
            Dictionary of (str, str) where key is file path and value is the result
    '''
    cores = cpu_count()
    func = partial(get_qr_mt, string_header=string_header, binarization=binarization)
    with Pool(processes=cores) as pool:
        if verbose:
            results = list(tqdm.tqdm(pool.imap(func, files), total=len(files)))
        else:
            results = pool.map(func, files)
    
    results_dict = {}
    for item in results:
        results_dict[item[0]] = item[1]

    return results_dict

    


def sort_directory(input_dir : str, output_dir : str, string_header : str = '', verbose : bool = False, binarization : bool = False) -> List[str]:
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
    image_paths = [os.path.join(input_dir, x) for x in images]
    
    if verbose:
        print('Scanning images for QR codes')
    results = get_qr_for_files(image_paths, string_header=string_header, verbose=verbose, binarization=binarization)
    os.makedirs(output_dir, exist_ok=True)


    if verbose:
        print('Sorting image files')
    current_path = os.path.join(output_dir, 'unsorted')
    for image in tqdm.tqdm(images) if verbose else images:
        image_path = os.path.join(input_dir, image)
        qr_string = results[image_path]
        if qr_string:
            current_path = os.path.join(output_dir, qr_string)
            if qr_string not in found_directories:
                found_directories.append(qr_string)
            
        os.makedirs(current_path, exist_ok=True)
        shutil.copyfile(image_path, os.path.join(current_path, image))

    found_directories.sort()
    return found_directories


