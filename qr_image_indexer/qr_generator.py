from io import TextIOWrapper
from turtle import fillcolor
import qrcode
from PIL import Image
from typing import Dict, List, Tuple
from os import path

def build_qr(data : str) -> Image.Image:
    """
    Build a QR code with selected settings. Will use maximum error correction;
    this should reduce risk of errors when taking photos which may be blurry or
    have other issues.
    """
    qr = qrcode.QRCode(version=None,
                        error_correction=qrcode.constants.ERROR_CORRECT_H,
                        box_size=10,
                        border = 4)

    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color='black', back_color='white')

def load_text_file(path : str, qr_headers : bool = False, string_header : str = '') -> Dict[str, Tuple[Dict, Image.Image]]:
    """
        Builds a data structure from a text file

        Parameters:
            path: path to text file as a string
            qr_headers: boolean indicating whether headings in text file are to have QRs generated
            string_header: string to be set at the start of QR code data to help weed out other QR codes

        Returns:
            Dictionary data structure where Key is the heading for the level and data is a tuple containing
                a nested dictionary of the same structure in position 0 and QR code image in position 1. These
                will be None if either are not required
    """
    output_data_structure = {}
    with open(path, 'r') as f:
        data = f.readlines()
        data = [x.rstrip() for x in data]
        unpack_file(data, qr_headers, output_data_structure, previous_levels=string_header)
    
    return output_data_structure


def unpack_file(data : List[str], qr_headers : bool, data_structure : Dict[str, Tuple[Dict, Image.Image]],
    index : int = 0, previous_levels : str = '') -> int:
    """
    Function to unpack a tabulated text file where items are grouped by tab depth. Called recursively for each loweer level of
    the data structure.

    Inputs:
        data - List of string representing data
        qr_headers - Boolean indicating if QR codes are to be built for headers or just for final elements
        data_structure - Dictionary where output data is to be stored. This will be altered by the function. Output dictionary will contain
            key of str and data in a touple of (Dict, Image) where the Dict is the data structure for subsequent levels of the file and the
            image is the QR code where relevent
        index - Index to start at. Defaults to zero but non-zero values used for recursion
        previous_levels - String representing the folder paths represented by previous levels of the data structure. This is embedded in the QR
            code for sorting

    Returns:
        index - integer representing current index of the process
        
    """
    #Determine target indent from first entry. All subsequent should be the same.
    target_indent = count_leading_tabs(data[index])
    while index < len(data):

        # Check if this index is less indented than the target. If so we need to return a level.
        if count_leading_tabs(data[index]) < target_indent:
            return index

        # Get some data for this iteration
        raw_line = data[index].strip()
        next_data_struct = {}
        next_level_str = previous_levels + raw_line + path.sep

        # If at the last index and the entry does not already exist, then just create the entry and exit the function, returning
        # an incremented index which will cause the while loop to terminate for all remaining iterations.
        if index == (len(data) - 1) and not raw_line in data_structure:
            image = build_qr(next_level_str)
            data_structure[raw_line] = (next_data_struct, image)
            return index + 1

        # Get the difference between the current indent and next indent levels
        indent_diff = target_indent - count_leading_tabs(data[index + 1])

        # If for whatever reason the entry already exists then get the existing dictionary to pass to the next level in
        if raw_line in data_structure:
            next_data_struct = data_structure[raw_line][0]
        else:
            image = None
            if qr_headers or indent_diff >= 0:
                image = build_qr(next_level_str)
            data_structure[raw_line] = (next_data_struct, image)

        # Check if the next line is further indented or if it is less indented. If more indented then recursively call function.
        # Otherwise increment
        if indent_diff < 0:
            index = unpack_file(data, qr_headers, next_data_struct, index + 1, next_level_str)
        else:
            index += 1

        
    return index

def count_leading_tabs(line : str) -> int:
    """
        Counts leacding tabs in a passed string. Will convert sets of 4 spaces to a tab

        Argument:
            line: line to count tabs in

        Returns integer with number of tabs
    """
    line = line.replace(' ' * 4, '\t')
    return (len(line) - len(line.lstrip('\t')))

def print_struct_outline(data_structure : Dict, indent_level : int = 0):
    """
        Prints structure outline to command line to provide user output

        Arguments:
            data_structure: data structure to print
            indent_level: current level of indent for recursive purposes
    """
    for key in data_structure:
        line_string = build_indent_string_print(indent_level)
        line_string += key
        print(line_string)
        if data_structure[key][0]:
            print_struct_outline(data_structure[key][0], indent_level + 1)



def build_indent_string_print(indent_level : int):
    """
        Builds a visibile indent indication for printing to command line

        Arguments:
            indent_level: level of indentation for the symbol
    """
    result = ''
    if indent_level == 0:
        return result
    indent_level -= 1
    for _ in range(indent_level):
        result += '\t'
    result += '|___'
    return result
