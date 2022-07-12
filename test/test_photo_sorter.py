from qr_image_indexer import photo_sorter

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