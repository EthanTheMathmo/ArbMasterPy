import xlwings as xw
import PySimpleGUI as sg
import sys
from Excelutilities.index_helpers import is_col_block_bool,  is_row_block_bool
sg.popup_ok("Please select the input ASINs and click 'ok' when finished")
input_ASIN = xw.apps.active.books.active.selection.value
input_ASIN_address = xw.apps.active.books.active.selection.address
sg.popup_ok("Please select the input Price/Unit and click 'ok' when finished")
active_cells = xw.apps.active.books.active.selection
input_PRICE = active_cells.value
input_PRICE_address = active_cells.address


def sanity_check_col_entries(entry1, entry2, addresses_and_names):
    #entry1 is a list of values
    #addresses_and_names is a list of tuples, first entry of tuple
    #is the address, and second is the name
    #implements some sanity checks
    if len(entry1) != len(entry2):
        sg.popup("Oops! Your two input columns of data are of different lengths.\nNow terminating...")
        sys.exit()

    import decimal
    for val1, val2 in zip(entry1, entry2):
        if type(val1) not in [str, int, float, decimal.Decimal] and val1 != None:
            sg.popup(f"Oops you selected some data which we couldn' recognise\nValue: {val1}")
            sys.exit()

        if type(val2) not in [str, int, float, decimal.Decimal] and val2 != None:
            sg.popup(f"Oops you selected some data which we couldn' recognise\n{val2}\n{type(val2)}")
            sys.exit()
    
    for address_and_name in addresses_and_names:
        address = address_and_name[0]
        name = address_and_name[1]
        if not is_col_block_bool(address):
            print(address)
            sg.popup(f"Oops! Your {name} data wasn't from a single column")
            sys.exit()

#sanity checks
sanity_check_col_entries(entry1=input_ASIN, entry2=input_PRICE, 
            addresses_and_names=[(input_ASIN_address, "ASIN"),(input_PRICE_address, "PRICE")])





    


ASIN_to_PRICE = {}
for asin, price in zip(input_ASIN, input_PRICE):
    ASIN_to_PRICE[asin] = price
    

sg.popup_ok("Please select the output ASINs and click 'ok' when finished")
output_ASIN = xw.apps.active.books.active.selection.value


def helper_ASIN(x):
    if x in ASIN_to_PRICE:
        return ASIN_to_PRICE[x]
    else:
        return None
output_array = [[helper_ASIN(asin)] for asin in output_ASIN]

sg.popup_ok("Please select the output location for the price/unit and click ok when finished\nThis should be the same length as your input ASIN data!")
xw.apps.active.books.active.selection.value = output_array