from distutils.command.build import build

from setuptools import SetuptoolsDeprecationWarning
from qr_image_indexer.qr_generator import load_text_file
from qr_image_indexer.qr_generator import print_struct_outline
from qr_image_indexer.photo_sorter import sort_directory
from qr_image_indexer.write_pdf import build_pdf_report
import os

import argparse

IM_PATH = r'C:\Users\Jonat\repos\qrCodeImageSorter\test_images'
IM_PATH_OUT = r'C:\Users\Jonat\repos\qrCodeImageSorter\test_images_out'
TEXT_FILE = r'C:\Users\Jonat\repos\qrCodeImageSorter\demo_list.txt'

def main():
    parser = argparse.ArgumentParser()
    mutual_exclusive = parser.add_mutually_exclusive_group()
    mutual_exclusive.add_argument('--generate-pdf', help='Generate a PDF of QR codes from a given text file. Specify ',
            nargs=2, metavar=('INPUT_TEXT_FILE','OUTPUT_PDF'))
    mutual_exclusive.add_argument('--sort-photos', help='Sort photos based on QR codes found in photos. Once a QR code is found all photos will be sorted into the directory indicated by the code until subsequent codes found',
            nargs=2, metavar=('INPUT_DIR', 'OUTPUT_DIR'))

    parser.add_argument('--qr-for-headings', help='Generate a QR code for each heading, not just a code for the last items in a tree.',
            action='store_true')
    parser.add_argument('--repeat-table-headings', help='Repeat table headings on every line',
            action='store_true')

    parser.add_argument('--string-prefix', help='Specify a prefix for use in the generated QR codes to differentiate from codes that might also end up in photos')

    args = parser.parse_args()

    string_header = ''
    if args.string_prefix:
        string_header = args.string_prefix
    
    if not args.generate_pdf and not args.sort_photos:
        print("Neither sort photos or generate PDF was selected. No action performed.")
    if args.generate_pdf:
        input = args.generate_pdf[0]
        output = args.generate_pdf[1]

        data_struct = load_text_file(input, args.qr_for_headings, string_header)
        print('Loaded text file: ' + input)
        print('')
        print('Read data structure: ')
        print_struct_outline(data_struct)

        build_pdf_report(data_struct, output, args.repeat_table_headings)
    if args.sort_photos:
        input = args.sort_photos[0]
        output = args.sort_photos[1]

        found_dirs = sort_directory(input, output, string_header)

        print('Found directories from images:')
        [print(x) for x in found_dirs]
        
        


if __name__ == '__main__':
    main()