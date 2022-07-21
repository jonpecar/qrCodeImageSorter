# Will not test qr generator code as it is effectively tested
# where it is used in the sorter tests.
import pathlib
from qr_image_indexer import qr_generator
from os import path
from PIL import ImageChops

def build_demo_tsv(file_path : pathlib.Path):
    content = '''Level1-1
Level1-2
\tLevel2-1
\tLevel2-2
\t\tLevel3'''
    with open(file_path, 'w') as f:
        f.write(content)

def build_demo_tsv_four_spaces(file_path : pathlib.Path):
    content = '''Level1-1
Level1-2
    Level2-1
    Level2-2
        Level3'''
    with open(file_path, 'w') as f:
        f.write(content)


def demo_tsv_expected_data():
    data = []
    data.append(['Level1-1'])
    data.append(['Level1-2'])
    data.append(['', 'Level2-1'])
    data.append(['', 'Level2-2'])
    data.append(['', '', 'Level3'])
    return data


def demo_data_struct_include_headers():
    test_struct = {}
    test_struct['Level1-1'] = ({}, 'Level1-1' + path.sep)
    test_struct['Level1-2'] = ({}, 'Level1-2' + path.sep)
    test_struct['Level1-2'][0]['Level2-1'] = ({}, 'Level1-2' + path.sep + 'Level2-1' + path.sep)
    test_struct['Level1-2'][0]['Level2-2'] = ({}, 'Level1-2' + path.sep + 'Level2-2' + path.sep)
    test_struct['Level1-2'][0]['Level2-2'][0]['Level3'] = ({}, 'Level1-2' + path.sep + 'Level2-2' + path.sep + 'Level3' + path.sep)
    return test_struct

def demo_data_struct_include_headers_with_QRHeader():
    test_struct = {}
    test_struct['Level1-1'] = ({}, r'{image}Level1-1' + path.sep)
    test_struct['Level1-2'] = ({}, r'{image}Level1-2' + path.sep)
    test_struct['Level1-2'][0]['Level2-1'] = ({}, r'{image}Level1-2' + path.sep + 'Level2-1' + path.sep)
    test_struct['Level1-2'][0]['Level2-2'] = ({}, r'{image}Level1-2' + path.sep + 'Level2-2' + path.sep)
    test_struct['Level1-2'][0]['Level2-2'][0]['Level3'] = ({}, r'{image}Level1-2' + path.sep + 'Level2-2' + path.sep + 'Level3' + path.sep)
    return test_struct

def demo_data_struct_no_headers():
    test_struct = {}
    test_struct['Level1-1'] = ({}, 'Level1-1' + path.sep)
    test_struct['Level1-2'] = ({}, None)
    test_struct['Level1-2'][0]['Level2-1'] = ({}, 'Level1-2' + path.sep + 'Level2-1' + path.sep)
    test_struct['Level1-2'][0]['Level2-2'] = ({}, None)
    test_struct['Level1-2'][0]['Level2-2'][0]['Level3'] = ({}, 'Level1-2' + path.sep + 'Level2-2' + path.sep + 'Level3' + path.sep)
    return test_struct

def demo_data_struct_no_headers_images():
    test_struct = {}
    test_struct['Level1-1'] = ({}, qr_generator.build_qr('Level1-1' + path.sep))
    test_struct['Level1-2'] = ({}, None)
    test_struct['Level1-2'][0]['Level2-1'] = ({}, qr_generator.build_qr('Level1-2' + path.sep + 'Level2-1' + path.sep))
    test_struct['Level1-2'][0]['Level2-2'] = ({}, None)
    test_struct['Level1-2'][0]['Level2-2'][0]['Level3'] = ({}, qr_generator.build_qr('Level1-2' + path.sep + 'Level2-2' + path.sep + 'Level3' + path.sep))
    return test_struct

def test_build_indent_string_print():
    assert '' == qr_generator.build_indent_string_print(0)
    assert '|___' == qr_generator.build_indent_string_print(1)
    for i in range(2, 10):
        assert '\t' * (i-1) + '|___' == qr_generator.build_indent_string_print(i)

def test_print_struct_outline(capsys):


    expected_out = '''Level1-1
Level1-2
|___Level2-1
|___Level2-2
\t|___Level3
'''

    qr_generator.print_struct_outline(demo_data_struct_include_headers())

    captured = capsys.readouterr()
    assert expected_out == captured.out

def test_load_text_file(tmp_path : pathlib.Path):
    demo_file = tmp_path / 'file.txt'
    build_demo_tsv(demo_file)
    loaded_data = qr_generator.load_text_file(demo_file.as_posix())
    assert demo_tsv_expected_data() == loaded_data

def test_load_text_file_spaces(tmp_path : pathlib.Path):
    demo_file = tmp_path / 'file.txt'
    build_demo_tsv_four_spaces(demo_file)
    loaded_data = qr_generator.load_text_file(demo_file.as_posix())
    assert demo_tsv_expected_data() == loaded_data

def test_count_leading_indent():
    data = ['non_empty_string']
    for i in range(10):
        assert i == qr_generator.count_leading_indent(data)
        data.insert(0, '')

def test_unpack_data_include_headers():
    result_struct = {}
    qr_generator.unpack_data(demo_tsv_expected_data(), True, result_struct)

    assert demo_data_struct_include_headers() == result_struct

def test_unpack_data_no_headers():
    result_struct = {}
    qr_generator.unpack_data(demo_tsv_expected_data(), False, result_struct)

    assert demo_data_struct_no_headers() == result_struct

def test_unpack_data_include_headers_QRHeader():
    result_struct = {}
    qr_generator.unpack_data(demo_tsv_expected_data(), True, result_struct, r'{image}')

    assert demo_data_struct_include_headers_with_QRHeader() == result_struct

def test_structure_qr_builder():
    expected_struct = demo_data_struct_no_headers_images()
    generated_struct = qr_generator.generate_qr_code_structure(demo_data_struct_no_headers())
    assert not ImageChops.difference(expected_struct['Level1-1'][1], generated_struct['Level1-1'][1]).getbbox()
    assert not ImageChops.difference(expected_struct['Level1-2'][0]['Level2-1'][1], generated_struct['Level1-2'][0]['Level2-1'][1]).getbbox()
    assert not ImageChops.difference(expected_struct['Level1-2'][0]['Level2-2'][0]['Level3'][1], generated_struct['Level1-2'][0]['Level2-2'][0]['Level3'][1]).getbbox()
    assert expected_struct['Level1-2'][0]['Level2-2'][1] == generated_struct['Level1-2'][0]['Level2-2'][1]