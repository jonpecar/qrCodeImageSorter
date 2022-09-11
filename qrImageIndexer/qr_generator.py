from io import TextIOWrapper
from turtle import fillcolor
import qrcode
from PIL import Image
from typing import Dict, List, Tuple
from os import path
from csv import reader

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

def load_text_file(path : str) -> List[List[str]]:
    """
        Builds a data structure from a text file

        Parameters:
            path: path to text file as a string
            qr_headers: boolean indicating whether headings in text file are to have QRs generated
            string_header: string to be set at the start of QR code data to help weed out other QR codes

        Returns:
            List of list for table-like file (e.g. CSV)
    """
    output_data_structure = []
    with open(path, 'r') as f:
        lines = []
        for row in f:
            lines.append(row.replace('    ', '\t'))
        csv = reader(lines , delimiter='\t')
        for row in csv:
            output_data_structure.append(row)

    return output_data_structure

def generate_qr_code_structure(data_structure : Dict[str, Tuple[Dict, str]]) -> Dict[str, Tuple[Dict, Image.Image]]:
    '''
        Converts a dictionary containing the QR code string into a dictionary with an Image in place of the string

        Parameters:
            data_structure: Data structure in format of dictionary with tuple containing a like dictionary and a string
            where the string is the data to be embedded in the QR code. If no QR code required string to be None

        Returns:
            Similar structure to input but with string replaced by an PIL image
    '''
    result = {}
    for key in data_structure:
        image = None
        if data_structure[key][1]:
            image = build_qr(data_structure[key][1])
        sub_struct = generate_qr_code_structure(data_structure[key][0])
        result[key] = (sub_struct, image)
    return result

def unpack_data(data : List[List[str]], gen_qr_headings : bool, data_structure : Dict[str, Tuple[Dict, str]], string_header : str = '',
    index : int = 0, previous_levels : str = '') -> int:
    """
    Function to unpack a tabulated text file where items are grouped by tab depth. Called recursively for each loweer level of
    the data structure.

    Inputs:
        data - List of string representing data
        gen_qr_headings - Boolean indicating if QR codes are to be built for headings or just for final elements
        data_structure - List where output data is to be stored. This will be altered by the function. Output dictionary will contain
            key of str and string for image in a touple of (Dict, str) where the Dict is the data structure for subsequent levels of the file and the
            str is the content for the QR code where relevent
        string_header - String to include as header for all QR code values to help distinguish from general QR codes
        index - Index to start at. Defaults to zero but non-zero values used for recursion
        previous_levels - String representing the folder paths represented by previous levels of the data structure. This is embedded in the QR
            code for sorting


    Returns:
        index - integer representing current index of the process

        
    """
    #Determine target indent from first entry. All subsequent should be the same.
    target_indent = count_leading_indent(data[index])
    while index < len(data):

        # Check if this index is less indented than the target. If so we need to return a level.
        if count_leading_indent(data[index]) < target_indent:
            return index

        # Get some data for this iteration
        raw_line = data[index][target_indent]
        next_data_struct = {}
        next_level_str = previous_levels + raw_line + path.sep

        # Get the difference between the current indent and next indent levels. If no further lines, then indent diff of zero
        if index == (len(data) - 1):
            indent_diff = 0
        else:
            indent_diff = target_indent - count_leading_indent(data[index + 1])

        # If for whatever reason the entry already exists then get the existing dictionary to pass to the next level in
        if raw_line in data_structure:
            next_data_struct = data_structure[raw_line][0]
        else:
            image_str = None
            if gen_qr_headings or indent_diff >= 0:
                image_str = string_header + next_level_str
            data_structure[raw_line] = (next_data_struct, image_str)

        # Check if the next line is further indented or if it is less indented. If more indented then recursively call function.
        # Otherwise increment
        if indent_diff < 0:
            index = unpack_data(data, gen_qr_headings, next_data_struct, string_header, index + 1, next_level_str)
        else:
            index += 1

        
    return index

def count_leading_indent(line : List[str]) -> int:
    """
        Counts leacding tabs in a passed string. Will convert sets of 4 spaces to a tab

        Argument:
            line: line to count tabs in

        Returns integer with number of tabs
    """
    for i in range(len(line)):
        if line[i] != '':
            return i
    return len(line)

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
