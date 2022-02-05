from setuptools import setup

setup(
    requires=[
        'setuptools',
        'wheel'
    ],
    name='qrImageIndexer',
    version='0.1.1',
    author='Jonathan Pecar',
    author_email='Jonathan.Pecar@gmail.com',
    description='Tool for indexing images with QR codes',
    packages=['qr_image_indexer'],
    install_requires=[
        'pyzbar',
        'pillow',
        'reportlab',
        'qrcode'
    ],
    license='LICENSE'
)