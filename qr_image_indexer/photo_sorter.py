from pyzbar.pyzbar import decode, ZBarSymbol
import cv2
from typing import List, Tuple, Dict
from multiprocessing import Pool, cpu_count
import os
import shutil
from functools import partial
import tqdm
import imghdr
import re

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

def sanitise_path(path : str) -> str:
    '''
        Function to remove invalid path characters from a path. Will prevent failure if user uses
        characters such as question marks in image strings.

        Arguments:
            path: path to sanitise

        Returns:
            sanitised path
    '''
    drive_designator_pos = path.find(':\\') + 2
    if drive_designator_pos > 0: #For windows with :\ in the tart of the path
        windows_drive_designator = path[:drive_designator_pos]
        remainder_path = path[drive_designator_pos:]
    else: #If windows drive designator not present (e.g. on Linux or with relative pathing)
        windows_drive_designator = ''
        remainder_path = path
    remainder_path = re.sub(r'[^\w\-_\. \\\/]', '_', remainder_path)
    return windows_drive_designator + remainder_path

def check_if_image(file_path : str) -> Tuple[bool, str]:
    '''
        Function to check if a file is an image. If the file is an image it will return True and the filepath,
        if it is not an image it will return False and the filepath.

        Arguments:
            file_path: path to item in question

        Returns:
            tuple of boolean and string indicating whether it is am image or not and the filepath of the associated check
    '''
    try:
        if imghdr.what(file_path):
            return (True, file_path)
    except:
        return (False, file_path)
    return (False, file_path)

def remove_non_images(files : List[str], verbose : bool, non_image_dir : str) -> List[str]:
    '''
        Function to remove items from the file list if they are not images. Non images files will be
        copied to the non-image directory so it is clear to the user what has happened with them.

        Parameters:
            files: list of files to check for image-ness
            verbose: indicates whether to provide verbose output to the user
            non_image_dir: directory to copy non-image files to for use feedback

        Returns:
            List of all files which are images
    '''
    if verbose:
        print("Checking for non-image files in the sorting directory. If any exist these will be saved to: " + non_image_dir)
    cores = cpu_count()
    with Pool(processes=cores) as pool:
        if verbose:
            results = list(tqdm.tqdm(pool.imap(check_if_image, files), total=len(files)))
        else:
            results = pool.map(check_if_image, files)

    new_files = []
    for is_image, file_path in results:
        if is_image:
            new_files.append(file_path)
        elif not os.path.isdir(file_path):
            os.makedirs(non_image_dir, exist_ok=True)
            _, file = os.path.split(file_path)
            shutil.copyfile(file_path, os.path.join(non_image_dir, file))
    
    return new_files



def get_image_paths(input_dir : str,  non_image_dir : str, verbose : bool = False) -> List[str]:
    """
        Gets all images in the provided input directory. Will exclude non-image files.

        Parameters:
            input_dir: Path to input directory containing photos as a string
            non_image_dir: Path to copy non-image files to
            verbose: Boolean indicating whether to print status information to command line

        Returns:
            List[str] of all iamge paths
    """
    images = os.listdir(input_dir)
    image_paths = [os.path.join(input_dir, x) for x in images]
    
    image_paths = remove_non_images(image_paths, verbose, non_image_dir)
    return image_paths


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

    non_image_dir = os.path.join(output_dir, 'non_image_files')

    image_paths = get_image_paths(input_dir, non_image_dir, verbose)

    if verbose:
        print('Scanning images for QR codes')
    results = get_qr_for_files(image_paths, string_header=string_header, verbose=verbose, binarization=binarization)
    os.makedirs(output_dir, exist_ok=True)


    if verbose:
        print('Sorting image files')
    current_path = os.path.join(output_dir, 'unsorted')
    for image_path in tqdm.tqdm(image_paths) if verbose else image_paths:
        _, image = os.path.split(image_path)
        qr_string = results[image_path]
        if qr_string:
            if qr_string.startswith(string_header):
                qr_string = qr_string[len(string_header):]
            qr_string = sanitise_path(qr_string)
            current_path = os.path.join(output_dir, qr_string)
            if qr_string not in found_directories:
                found_directories.append(qr_string)
            
        os.makedirs(current_path, exist_ok=True)
        shutil.copyfile(image_path, os.path.join(current_path, image))

    found_directories.sort()
    return found_directories


