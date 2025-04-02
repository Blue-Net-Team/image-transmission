from setuptools import setup, find_packages

setup(
    name="ImgTrans",
    version="2.0.0",
    description="远程图传",
    long_description=open("README.rst").read(),
    long_description_content_type="text/markdown",
    author="IVEN-CN",
    author_email="13377529851@qq.com",
    url="https://github.com/Blue-Net-Team/image-transmission.git",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.8.1.78",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
