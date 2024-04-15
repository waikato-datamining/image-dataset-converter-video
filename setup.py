from setuptools import setup, find_namespace_packages


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="image-dataset-converter-video",
    description="Video support for the image-dataset-converter library.",
    long_description=(
            _read('DESCRIPTION.rst') + b'\n' +
            _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/waikato-datamining/image-dataset-converter-video",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Processing',
    ],
    license='MIT License',
    package_dir={
        '': 'src'
    },
    packages=find_namespace_packages(where='src'),
    install_requires=[
        "image-dataset-converter",
        "opencv-python",
        "termplotlib",
        "cap_from_youtube",
    ],
    version="0.0.1",
    author='Peter Reutemann',
    author_email='fracpete@waikato.ac.nz',
    entry_points={
        "idc.readers": [
            "idc_video_readers1=idc.video.reader:seppl.io.Reader",
        ],
        "idc.filters": [
            "idc_video_filters1=idc.video.filter:seppl.io.Filter",
        ],
        "idc.writers": [
            "idc_video_writers1=idc.video.writer:seppl.io.Writer",
        ]
    },
)
