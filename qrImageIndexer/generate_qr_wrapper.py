from distutils.command import build
from typing import List
from fpdf import FPDF
from qrImageIndexer.qr_generator import unpack_data, generate_qr_code_structure
from qrImageIndexer.write_pdf_fpf2 import build_pdf_report

def generate_qr_pdf(text_data: List[List[str]], qr_for_headings : bool,
                    repeat_headings : bool, sort_sliceable : bool, string_header : str = '') -> FPDF:
    data_struct = unpack_data(text_data, qr_for_headings, string_header)
    iamge_struct = generate_qr_code_structure(data_struct)
    return build_pdf_report(iamge_struct, repeat_headings, sort_sliceable)