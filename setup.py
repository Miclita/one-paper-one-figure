"""
Setup script for creating Mac application bundle
"""
from setuptools import setup

APP = ['main.py']
DATA_FILES = [('', ['.env'])]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter', 'openai', 'PyPDF2', 'PIL', 'dotenv'],
    'iconfile': 'app.icns',  # 如果你有一个图标文件的话
    'plist': {
        'CFBundleName': 'PDF2Image',
        'CFBundleDisplayName': 'PDF to Image Generator',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright (c) 2025'
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'openai>=1.0.0',
        'PyPDF2',
        'Pillow',
        'python-dotenv'
    ]
)