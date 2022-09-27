from qrImageIndexer import generate_qr_wrapper
from unittest import mock

def mock_qr_generator_functions(mocker : mock):
    unpack_data = mocker.patch('qrImageIndexer.generate_qr_wrapper.unpack_data')
    generate_qr_structure = mocker.patch('qrImageIndexer.generate_qr_wrapper.generate_qr_code_structure')
    build_pdf = mocker.patch('qrImageIndexer.generate_qr_wrapper.build_pdf_report')

    return (unpack_data, generate_qr_structure, build_pdf)


def test_single_func_pdf_builder_all_true(mocker):
    (unpack_data, generate_qr_structure, build_pdf) = mock_qr_generator_functions(mocker)
    result = generate_qr_wrapper.generate_qr_pdf([['Line 1', ''], ['', 'Line 1 Indent']],
                                        True, True, True, r'{header}')
    
    unpack_data.assert_called_once_with([['Line 1', ''], ['', 'Line 1 Indent']], True, r'{header}')
    generate_qr_structure.assert_called_once_with(unpack_data.return_value)
    build_pdf.assert_called_once_with(generate_qr_structure.return_value, True, True)
    assert result == build_pdf.return_value

def test_single_func_pdf_builder_no_qr_heading(mocker):
    (unpack_data, generate_qr_structure, build_pdf) = mock_qr_generator_functions(mocker)
    result = generate_qr_wrapper.generate_qr_pdf([['Line 1', ''], ['', 'Line 1 Indent']],
                                        False, True, True, r'{header}')
    
    unpack_data.assert_called_once_with([['Line 1', ''], ['', 'Line 1 Indent']], False, r'{header}')
    generate_qr_structure.assert_called_once_with(unpack_data.return_value)
    build_pdf.assert_called_once_with(generate_qr_structure.return_value, True, True)
    assert result == build_pdf.return_value

def test_single_func_pdf_builder_no_title_all_heading(mocker):
    (unpack_data, generate_qr_structure, build_pdf) = mock_qr_generator_functions(mocker)
    result = generate_qr_wrapper.generate_qr_pdf([['Line 1', ''], ['', 'Line 1 Indent']],
                                        True, False, True, r'{header}')
    
    unpack_data.assert_called_once_with([['Line 1', ''], ['', 'Line 1 Indent']], True, r'{header}')
    generate_qr_structure.assert_called_once_with(unpack_data.return_value)
    build_pdf.assert_called_once_with(generate_qr_structure.return_value, False, True)
    assert result == build_pdf.return_value

def test_single_func_pdf_builder_not_sliceable(mocker):
    (unpack_data, generate_qr_structure, build_pdf) = mock_qr_generator_functions(mocker)
    result = generate_qr_wrapper.generate_qr_pdf([['Line 1', ''], ['', 'Line 1 Indent']],
                                        True, True, False, r'{header}')
    
    unpack_data.assert_called_once_with([['Line 1', ''], ['', 'Line 1 Indent']], True, r'{header}')
    generate_qr_structure.assert_called_once_with(unpack_data.return_value)
    build_pdf.assert_called_once_with(generate_qr_structure.return_value, True, False)
    assert result == build_pdf.return_value