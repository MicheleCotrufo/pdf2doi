import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'),encoding ='unicode_escape') as f:
    long_description = f.read()

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

setuptools.setup(name='pdf2doi',
      version='1.0rc2',
      description='A  python library/command-line tool to extract the DOI or other identifiers of a scientific paper from a pdf file.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/MicheleCotrufo/pdf2doi',
      author='Michele Cotrufo',
      author_email='michele.cotrufo@gmail.com',
      license='MIT',
      entry_points = {
        'console_scripts': ["pdf2doi = pdf2doi.main:main"],
      },
      packages=['pdf2doi'],
      install_requires= required_packages,
      zip_safe=False)