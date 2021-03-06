import warnings
from os import path
from rosey_power import __version__
from datetime import datetime
from setuptools import setup, find_packages


now = datetime.now()
if __version__.endswith(f'.{now.year}{now.month:02d}{now.day:02d}'):
    warnings.warn('WARNING! The package version number has not be updated')\

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
base_packages = [
    'numpy',
    'scipy',
    'pandas',
    'tqdm',
]
install_requires = base_packages


setup(
    name='rosey-power',
    version=__version__,
    description='Finally, easy power analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/arose13/rosey-power',
    download_url=f'https://github.com/arose13/rosey-power/tarball/{__version__}',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    keywords='statistics',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Stephen Anthony Rose',
    install_requires=install_requires,
    author_email='me@stephenro.se',
    zip_safe=False
)
