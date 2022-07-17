from os import listdir
from qr_image_indexer import photo_sorter, qr_generator
import pathlib
import os
from typing import Dict

def generate_image(tmp_path : pathlib.Path, string : str, filename : str = 'test') -> str:
    '''
        Generates a temporary image and returns the path to the image
        as a string.

        Arguments:
            tmp_path : pathlib.Path: Temporary path in which to create the image
            string : str: string to embed in qr code

        Returns path to image as str
    '''
    image = qr_generator.build_qr(string)
    image.save(tmp_path / (filename + '.png'))
    return (tmp_path / (filename + '.png')).as_posix()

def test_path_sanitise_already_clean():
    test_path_clean_windows = r'C:\Test_Path\No Invalid Characters\Test.File'
    sanitised = photo_sorter.sanitise_path(test_path_clean_windows)
    assert sanitised == test_path_clean_windows

    test_path_clean_unix = r'/usr/test/test_path/all valid chars.extn'
    sanitised = photo_sorter.sanitise_path(test_path_clean_unix)
    assert sanitised == test_path_clean_unix

def test_path_sanitise_unlcean():
    test_path_windows = r'C:\Test_Path\Bad:Chars\Test?'
    expected_path_windows = r'C:\Test_Path\Bad_Chars\Test_'
    assert photo_sorter.sanitise_path(test_path_windows) == expected_path_windows

    test_path_unix = r'/usr/test_path/test?invalid/Chars"'
    expected_path_unix = r'/usr/test_path/test_invalid/Chars_'
    assert photo_sorter.sanitise_path(test_path_unix) == expected_path_unix

''' 
    Acknowledge that this uses the image generation as an input and image generation uses this as a test,
    but it is vanishingly unlikely that zbar reads the QR code in the exactly incorrect way that the qr
    library generates it. Also assuming external libraries are OK.
'''
def test_read_qr_zbar(tmp_path : pathlib.Path):
    assert photo_sorter.read_qr_zbar(generate_image(tmp_path, 'test_string'))[0].data.decode('utf-8') == 'test_string'
    assert photo_sorter.read_qr_zbar(generate_image(tmp_path, 'test_string'))[0].data.decode('utf-8') == photo_sorter.read_qr_zbar(generate_image(tmp_path, 'test_string'), binarization=True)[0].data.decode('utf-8')

def test_get_qr_no_header(tmp_path : pathlib.Path):
    assert photo_sorter.get_qr(generate_image(tmp_path, 'test_string')) == 'test_string'

def test_get_qr_header(tmp_path : pathlib.Path):
    assert photo_sorter.get_qr(generate_image(tmp_path, r'{header}test_string'), r'{header}') == 'test_string'
    assert photo_sorter.get_qr(generate_image(tmp_path, r'{wrong_header}test_string'), r'{header}') == None
    assert photo_sorter.get_qr(generate_image(tmp_path, r'test_string'), r'{header}') == None

def test_get_qr_mt(tmp_path : pathlib.Path):
    path = generate_image(tmp_path, r'{header}test_string')
    assert photo_sorter.get_qr_mt(generate_image(tmp_path, r'{header}test_string'), r'{header}') == (path, 'test_string')
    assert photo_sorter.get_qr_mt(generate_image(tmp_path, r'{wrong_header}test_string'), r'{header}') == (path, None)
    assert photo_sorter.get_qr_mt(generate_image(tmp_path, r'test_string'), r'{header}') == (path, None)

def test_get_qr_for_files(tmp_path : pathlib.Path):
    files = []
    for i in range(5):
        content = 'content' + str(i)
        files.append(generate_image(tmp_path, content, str(i)))
    
    result : Dict[str, str] = photo_sorter.get_qr_for_files(files)
    for i in range(5):
        assert files[i] in result
        content = 'content' + str(i)
        assert result[files[i]] == content

    for i in range(5, 7):
        content = r'{content}' + str(i)
        files.append(generate_image(tmp_path, content, str(i)))

    result : Dict[str, str] = photo_sorter.get_qr_for_files(files, string_header=r'{content}')

    for i in range(5):
        assert files[i] in result
        assert result[files[i]] is None

    for i in range(5, 7):
        assert files[i] in result
        content = str(i)
        assert result[files[i]] == content


def test_is_image_true(tmp_path : pathlib.Path):
    image = qr_generator.build_qr('test')
    image.save(tmp_path / ('test.png'))
    
    assert photo_sorter.check_if_image((tmp_path / ('test.png')).as_posix())[0]

def test_is_image_false(tmp_path : pathlib.Path):
    temp_file = tmp_path /'test'
    temp_file.touch()
    
    assert not photo_sorter.check_if_image(temp_file.as_posix())[0] 

def test_remove_non_images(tmp_path : pathlib.Path):
    files = []
    
    non_image_dir = tmp_path/'non_image'
    non_image_dir.mkdir()

    im_path = generate_image(tmp_path, 'test')
    files.append(im_path)
    non_image_file = tmp_path/'non_image_file'
    non_image_file.touch()
    files.append(non_image_file.as_posix())

    results = photo_sorter.remove_non_images(files, False, non_image_dir.as_posix())

    assert len(results) == 1
    assert results[0] == im_path
    assert os.listdir(non_image_dir) == ['non_image_file']

def test_get_images(tmp_path : pathlib.Path):    
    non_image_dir = tmp_path/'non_image'
    non_image_dir.mkdir()

    im_path = generate_image(tmp_path, 'test')
    non_image_file = tmp_path/'non_image_file'
    non_image_file.touch()

    results = photo_sorter.get_image_paths(tmp_path.as_posix(), non_image_dir.as_posix())

    assert len(results) == 1
    assert results[0].replace('\\','/') == im_path # Since using os.join this will end up with Windows pathing in Windows - still OK
    assert os.listdir(non_image_dir) == ['non_image_file']

def test_qr_sorting(tmp_path : pathlib.Path):
    qr_strings = [r'Test1\subTest', r'Test1', r'Test2', r'Test?']
    inputs = tmp_path/'inputs'
    outputs = tmp_path/'outputs'
    outputs.mkdir()
    inputs.mkdir()
    for i in range(len(qr_strings)):
        image = qr_generator.build_qr(qr_strings[i])
        image.save(inputs / (str(i) + '.png'))


    found_dirs = photo_sorter.sort_directory(inputs.as_posix(), outputs.as_posix())

    assert found_dirs == [r'Test1', r'Test1\subTest', r'Test2', r'Test_']

    for i in range(len(qr_strings)):
        path = outputs/photo_sorter.sanitise_path(qr_strings[i])
        filecount = 0
        for filename in os.listdir(path.as_posix()):
            if os.path.isfile(path/filename): filecount += 1
        assert filecount == 1
        assert os.listdir(path.as_posix())[0] == (str(i) + '.png')
