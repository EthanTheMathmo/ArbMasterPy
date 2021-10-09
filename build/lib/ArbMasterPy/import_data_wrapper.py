from Excelutilities import importing_data_helpers 
add_col_data_from_another_sheet = importing_data_helpers.add_col_data_from_another_sheet
import decimal
import datetime
def import_data():
    add_col_data_from_another_sheet("ASIN data", "INPUT DATA", [float, int, decimal.Decimal,datetime.datetime, str])
