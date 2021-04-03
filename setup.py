from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='pdf2doi',
      version='0.1',
      description='A python library/command-line tool to retrieve the DOI of a paper from a pdf file',
      url='https://github.com/MicheleCotrufo/pdf2doi',
      author='Michele Cotrufo',
      author_email='mcotrufo@gc.cuny.edu',
      license='MIT',
      packages=['pdf2doi'],
      install_requires= requirements,
      zip_safe=False)