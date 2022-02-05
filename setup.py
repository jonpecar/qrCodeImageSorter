from setuptools import setup

setup(
    name='qrImageIndexer',
    version='0.1',
    packages=['.qr_image_indexer'],
    install_requires=[
        'pyzbar[PIL]',
        'pillow',
        'reportlab',
        'qrcode'
    ],
    license='LICENSE'
)