import os
from setuptools import setup


def read(f_name):
    return open(os.path.join(os.path.dirname(__file__), f_name)).read()


setup(
    name='nwgcc',
    version='0.0.1',
    description='Simple control center for window managers',
    packages=['nwgcc'],
    include_package_data=True,
    url='https://github.com/nwg-piotr/nwgcc',
    license='GPL-3.0-or-later',
    author='Piotr Miller',
    author_email='nwg.piotr@gmail.com',
    python_requires='>=3.4.0',
    install_requires=[]
)
