from fpdf import FPDF
from typing import Dict, List, Tuple
from PIL.Image import Image
from qrcode.image.pil import PilImage
from math import ceil
from copy import copy
import io

TARGET_ROWS_PER_PAGE = 6

def build_pdf_report(data_struct : Dict[str, Tuple[Dict, Image]], repeat_headings : bool = False, order_for_slicing : bool = False) -> FPDF:
    '''
        Builds a PDF report using FPDF2

        Arguments:
        data_struct : Dict[str, Tuple[Dict, Image]]: Input recursive data structure
        path: str: save path for PDF
        repeat_headings: bool: Indicates whether headings to be reapeated on each row or only at top level
        order_for_slicing: bool: whether to reorder table for slicing or have it down the page

    '''
    pdf = FPDF(orientation='portrait', format='A4')
    pdf.set_font('helvetica')
    pdf.add_page()
    data_table = build_data_table(data_struct, repeat_headings)
    if order_for_slicing:
        data_table = sort_table_for_slicing(data_table, TARGET_ROWS_PER_PAGE)
    
    cols = len(data_table[0])
    col_width = pdf.epw / cols
    line_height = (pdf.eph / (TARGET_ROWS_PER_PAGE)) * 0.99 #Going exact will cause a cautious page break

    for row in data_table:
        first_elem = True
        for datum in row:
            if first_elem:
                pdf.set_font(style='B')
                first_elem = False
            else:
                pdf.set_font(style='')
            if type(datum) is PilImage:
                f = io.BytesIO()
                temp : PilImage = datum
                temp.save(f)
                pdf.image(f, x=pdf.get_x(), y=pdf.get_y(), w=min(col_width, line_height))
                pdf.multi_cell(col_width, line_height, '', border = 1,
                    new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
            else:
                pdf.multi_cell(col_width, line_height, datum, border = 1,
                    new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
        pdf.ln(line_height)
    return pdf

def build_data_table(data_struct: Dict[str, Tuple[Dict, Image]], pass_headings : bool = False, existing_data : List = []) -> List[List]:
    '''
        Function to recursively turn the data structure into a nested list. Will include headings if required

        Arguments:
        data_struct: Dict[str, Tuple[Dict, Image]]: Nested data structure containing headings and QR images as appropriate.
        pass_headings: bool: Indicates whether headings to be included at each subsequent level
        existing_data: List: For recursive calls. Includes either heading data or empty strings depending on status of pass_headings argument

        Returns:
        List[List]: Containing data to be written to PDF table
    '''
    result = []

    for key in data_struct:
        row = copy(existing_data)
        result.append(row)
        row.append(key)

        if data_struct[key][0]:
            passed_row = copy(row)
            if not pass_headings:
                passed_row = ['' for _ in passed_row]
            for sub_row in build_data_table(data_struct[key][0], pass_headings, passed_row):
                result.append(sub_row)

        if data_struct[key][1]:
            row.append(data_struct[key][1])
        else:
            row.append('')

    max_cols = max([len(r) for r in result])
    for row in result:
        while len(row) < max_cols:
            row.insert(-1, '') # Pad out columns before QR for shorter rows so QRs are always in the last cell and each row is equal
    
    return result

def sort_table_for_slicing(input_table : List[List], rows_per_page : int) -> List[List]:
    '''
        Function to sort table so that it will be in an order that will allow
        easy sorting of QR code strips through the page. I.e. at the top of each
        page will be QR code 1, 2, 3, 4 etc. instead of down the page, such that when
        sliced into strips they will be in order when stacked.

        Arguments:
        input_table: List[List]: Table to be sorted. Expected that all rows same length and of at least length 1
        rows_per_page: int: Number of rows to be sorted for each page

        Returns
        List[List]: Sorted list of same number of elements as input sorted down the page
    '''    
    total_rows = len(input_table)
    page_count = ceil(total_rows/rows_per_page) # Need an extra full page if any remainder
    output = []
    for page in range(page_count):
        for line in range(rows_per_page):
            index = page + line * page_count
            if index < total_rows:
                output.append(input_table[index])
            else:
                output.append(['' for _ in input_table[0]])
    
    return output
    

