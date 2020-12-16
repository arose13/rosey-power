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
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')


install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]


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
    dependency_links=dependency_links,
    author_email='me@stephenro.se',
    zip_safe=False
)
