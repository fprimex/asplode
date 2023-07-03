from setuptools import setup

setup(
    name="asplode",
    version="1.0.1",
    description="Recursively decompress archives",
    long_description="Recursively decompress archives",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Utilities",
    ],
    keywords="decompression archives zip gzip tar",
    author="Brent Woodruff",
    author_email="brent@fprimex.com",
    url="http://github.com/fprimex/asplode",
    license="Apache",
    py_modules=["asplode"],
    zip_safe=False,
    install_requires=["plac"],
    entry_points={
        'console_scripts': [
            'asplode = asplode:main',
        ],
    },
)
