from qr_image_indexer import write_pdf_fpf2
from .test_qr_generator import demo_data_struct_include_headers
from os import path

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