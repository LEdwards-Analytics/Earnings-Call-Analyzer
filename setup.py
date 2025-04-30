from setuptools import setup, find_packages

setup(
    name="earnings_call_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "beautifulsoup4",
        "requests",
        "nltk",
        "scikit-learn",
        "yfinance"
    ],
    description="Earnings Call Analysis Package",
)
