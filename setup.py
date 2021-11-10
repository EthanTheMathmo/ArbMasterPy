from setuptools import setup, find_packages


requirements = ["xlwings==0.24.7","Excelutilities==0.0.11","openpyxl","PySimpleGUI", "pandas", "bs4", "google-search-results"]
#The xlwings version has to be strict to work with the workbook setup

setup(
    name="Arbitrage-Master-Sheet-Py",
    version="0.0.25",
    author="Ethan Horsfall",
    author_email="ethan.horsfall@gmail.com",
    description="Arbitrage master sheet for amazon",
    packages=find_packages(),
    install_requires=requirements,
    package_data={'': ['Amazon standard inventory - flat file.xlsm', 'CreateInboundPlanRequest.xlsx']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)