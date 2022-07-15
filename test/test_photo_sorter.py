from os import listdir
from qr_image_indexer import photo_sorter, qr_generator
import pathlib
import os

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

def test_is_image_true(tmp_path : pathlib.Path):
    image = qr_generator.build_qr('test')
    image.save(tmp_path / ('test.png'))
    
    assert photo_sorter.check_if_image((tmp_path / ('test.png')).as_posix())[0]

def test_is_image_false(tmp_path : pathlib.Path):
    temp_file = tmp_path /'test'
    temp_file.touch()
    
    assert not photo_sorter.check_if_image(temp_file.as_posix())[0] 
    
