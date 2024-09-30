from setuptools import setup, find_packages

setup(
    name="ImgTrans",
    version="1.0.0",
    description="(局域网)远程图传",
    long_description=open("README.rst").read(),
    long_description_content_type="text/markdown",
    author="IVEN-CN",
    author_email="13377529851@qq.com",
    url="https://github.com/Blue-Net-Team/remote-image-transmission.git",
    packages=find_packages(),
    install_requires=[
        "opencv-python==4.5.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
