import setuptools
from pandas_pipeline import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pandas-pipeline",
    version=__version__,
    author="Raimi bin Karim",
    author_email="raimi.bkarim@gmail.com",
    description="Pandas Pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/remykarem/pandas-pipeline",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['numpy>=1.16.1', 'scikit-learn>=0.20.2']
)
