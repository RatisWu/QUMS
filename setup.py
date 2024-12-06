from setuptools import setup, find_packages

setup(
    name='UQMS',          # Replace with your package name
    version='0.0.1',
    author='Dai-Jia, Wu',
    author_email='porkface0301@gmail.com',
    description='United Quantum Measurement System',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/RatisWu/UQMS',
    packages=find_packages(),          # Automatically find package directories
    install_requires=[                 # Optional, if you have dependencies
        'qblox-instruments==0.12.0',
        'quantify-core==0.7.4',
        'quantify-scheduler==0.20.0',
        'qm-octave==1.2.0',
        'qm-qua==1.1.3',
        'qualang-tools==0.15.2',
        'netCDF4'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)