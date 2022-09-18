from typing import List
from fpdf import FPDF

def generate_qr_pdf(text_data: List[List[str]], string_header : str, qr_for_headings : bool,
                    repeat_headings : bool, sort_sliceable : bool, ) -> FPDF:
    raise NotImplementedError()