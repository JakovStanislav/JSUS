from setuptools import setup
from main import __version__

setup(
    name='JSUS',
    version=__version__,

    url='https://github.com/JakovStanislav/JSUS',
    author='Jakov Stanislav Uglesic',
    author_email='jakov.stanislav@gmail.com',

    py_modules=['main', 'frontend', 'backend'],
    install_requires=['matplotlib', 'numpy', 'scipy', 'pandas',
                      'PyQt5', 'obspy'],
    #data_files=[('', ['ColorMaps.csv'])],
)