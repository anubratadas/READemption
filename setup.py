try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='READemption',
    version='0.4.0',
    packages=['reademptionlib', 'tests'],
    author='Konrad U. Förstner',
    author_email='konrad@foerstner.org',
    description='A RNA-Seq Analysis Pipeline',
    url='',
    install_requires=[
        "biopython >= 1.66",
        "matplotlib >= 1.5.1",
        "pandas >= 0.17.1",
        "pysam >= 0.9.0"
    ],
    scripts=['bin/reademption'],
    license='ISC License (ISCL)',
    long_description=open('README.rst').read(),
    classifiers=[
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ]
)
