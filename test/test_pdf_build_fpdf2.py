from qrImageIndexer import write_pdf_fpf2
from .test_qr_generator import demo_data_struct_include_headers
from os import path
import pathlib
from PyPDF2 import PdfReader

def expected_table_include_headers_strings_repeat_headings():
    expected_structure = [
        ['Level1-1', '', '', 'Level1-1' + path.sep],
        ['Level1-2', '', '', 'Level1-2' + path.sep],
        ['Level1-2', 'Level2-1', '', 'Level1-2' + path.sep + 'Level2-1' + path.sep],
        ['Level1-2', 'Level2-2', '', 'Level1-2' + path.sep + 'Level2-2' + path.sep],
        ['Level1-2', 'Level2-2', 'Level3', 'Level1-2' + path.sep + 'Level2-2' + path.sep + 'Level3' + path.sep]
    ]
    return expected_structure

def expected_table_include_headers_strings_no_repeat_headings():
    expected_structure = [
        ['Level1-1', '', '', 'Level1-1' + path.sep],
        ['Level1-2', '', '', 'Level1-2' + path.sep],
        ['', 'Level2-1', '', 'Level1-2' + path.sep + 'Level2-1' + path.sep],
        ['', 'Level2-2', '', 'Level1-2' + path.sep + 'Level2-2' + path.sep],
        ['', '', 'Level3', 'Level1-2' + path.sep + 'Level2-2' + path.sep + 'Level3' + path.sep]
    ]
    return expected_structure

def test_build_table_repeat_headings():
    assert expected_table_include_headers_strings_repeat_headings() == write_pdf_fpf2.build_data_table(demo_data_struct_include_headers(), True)

def test_build_table_no_repeat_headings():
    assert expected_table_include_headers_strings_no_repeat_headings() == write_pdf_fpf2.build_data_table(demo_data_struct_include_headers(), False)

def test_sort_table_for_slicing_no_remainder():
    input = [
        [1],
        [2],
        [3],
        [4],
        [5],
        [6],
        [7],
        [8]
    ]

    expected = [
        [1],
        [3],
        [5],
        [7],
        [2],
        [4],
        [6],
        [8]
    ]

    assert expected == write_pdf_fpf2.sort_table_for_slicing(input, 4)

def test_sort_table_for_slicing_remainder():
    input = [
        [1],
        [2],
        [3],
        [4],
        [5],
        [6],
        [7],
        [8]
    ]

    expected = [
        [1],
        [4],
        [7],
        [2],
        [5],
        [8],
        [3],
        [6],
        ['']
    ]

    assert expected == write_pdf_fpf2.sort_table_for_slicing(input, 3)

def test_generated_pdf_text(tmp_path : pathlib.Path):
    data_dict = {
        'Line 1':
            ({'Indent 1' : 
                ({'Indent 2' : ({}, None)},
                    None)},
                None),
        'Line 2': 
            ({}, None)
    }
    path = tmp_path / 'test.pdf'
    pdf = write_pdf_fpf2.build_pdf_report(data_dict)
    pdf.output(path.as_posix())
    reader = PdfReader(path)
    page = reader.pages[0]
    text = page.extract_text()
    assert 'Line 1' in text
    assert 'Line 2' in text
    assert 'Indent 1' in text
    assert 'Indent 2' in text

    