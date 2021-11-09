import PySimpleGUI as sg

import traceback

column_mappings = {'Order Date': 0,
 'Order ID': 1,
 'Item Name': 2,
 'ASIN': 3,
 'SKU': 4,
 'STORE': 5,
 'COST PER UNIT': 6,
 'INDV ITEMS QTY': 7,
 'SELLABLE QTY': 8,
 'Condition': 9,
 'ORDER COST': 10,
 'PRICE': 11,
 'ISBN': 12,
 'USPC': 13,
 'EAN': 14}

def debug_basic(value):
    if value:
        def decorate(f):
            def wrap(*args, **kwargs):
                try:
                    return f(*args,**kwargs)
                except Exception as e:
                    tb = traceback.format_exc()
                    sg.Print(f'An error happened.  Here is the info:', e, tb)
                    sg.popup_error(f'AN EXCEPTION OCCURRED!', "Please send us a screenshot of the error message to the side, and then click on the button to make it disappear")
            return wrap

        return decorate
    else:
        def decorate(f):
            def wrap(*args, **kwargs):
                return f(*args,**kwargs)
            return wrap



master_col_names_to_indices = {"PRODUCT NAME":2, "ASIN":3, "ISBN":12, "UPC":13, "EAN":14, "SKU":4, "PURCHASE PRICE":6, 
                            "Qty":8, "ORDER DATE":0, "CONDITION":9, "PRICE":11}


master_data_last_letter = "O"

def get_input_user_wrapper(input_function):
    def wrapper(*args, **kwargs):
        output = input_function(*args, **kwargs)
        if output not in kwargs.get("affirmative_response"):
            event = sg.popup_yes_no("Press 'Yes' to terminate the process, or press 'No' to repeat the last step",
            keep_on_top=True)
            if event == "Yes":
                from sys import exit
                exit()
            else:
                return wrapper(*args, **kwargs)
        else:
            return output
    return wrapper



@get_input_user_wrapper
def select_name_and_click_ok_or_terminate(name, keep_on_top, affirmative_response):
    #affirmative_response is required for the decorator to work
    event = sg.popup(f"Please select {name} and click 'OK' when finished",
    keep_on_top=keep_on_top)
    return event

@get_input_user_wrapper
def ask_to_go_to_wb_click_ok_or_terminate(name, keep_on_top, affirmative_response):
    #affirmative_response is required for the decorator to work and cannot be gieven a 
    #default argument, but "OK" should always be passed in as a keyword argument for it
    event = sg.popup(f"Please make {name} your active Excel sheet and click 'OK' when finished",
    keep_on_top=keep_on_top)
    return event

@get_input_user_wrapper
def get_file(text, affirmative_response, value_dict):
    #to make this work with the decorator used for the other GUIs, we mutate a dictionary
    #to return the values, and return the event
    layout = [[sg.Text(f'Select the file location of {text}'), sg.Input(),sg.FileBrowse(key="--input_file--")],
                [sg.OK(), sg.Cancel()]]
    event, values = sg.Window("",layout, keep_on_top=True, grab_anywhere=True).read(close=True)
    value_dict["val"] = values["--input_file--"]
    return event

def open_amazon_inventory_page():
    import webbrowser
    webbrowser.open(r"https://sellercentral.amazon.co.uk/listing/reports/ref=xx_invreport_dnav_xx")


@debug_basic(True)
def re_import_inventory_data():
    value_dict = {"val":None}
    get_file(text="the .txt inventory file you downloaded from amazon", 
    affirmative_response="OK", value_dict=value_dict)
    fileloc=value_dict["val"]

    import pandas as pd
    data = pd.read_csv(fileloc,sep="\t", header=None)

    
    ask_to_go_to_wb_click_ok_or_terminate("Arbitrage Master Sheet", 
    keep_on_top=True, affirmative_response="OK")
    import xlwings as xw
    xw.apps.active.books.active.sheets["Inventory"].range("A1").options(index=False, header=False).value = data
    return


def set_python_path():
    import platform
    import xlwings as xw
    if platform.system() == "Windows":
        addin_book = xw.Book(r"C:\Users\ethan\AppData\Roaming\Microsoft\Excel\XLSTART\master_sheet_addin.xlam")
        value_dict = {"val":None}
        get_file(text="location of the python EXE", affirmative_response="OK", value_dict=value_dict)
        from pathlib import Path
        path=Path(value_dict["val"])
        addin_book.sheets["xlwings.conf"].range("B1").value = str(path)

    elif platform.system() == "Darwin":
        sg.popup("Implementation for Mac doesn't exist yet")
        import sys
        sys.exit
    else:
        sg.popup("Oops, we only support Mac and Windows")
        import sys
        sys.exit()

def read_python_path():
    import platform
    import xlwings as xw
    if platform.system() == "Windows":
        addin_book = xw.Book(r"C:\Users\ethan\AppData\Roaming\Microsoft\Excel\XLSTART\master_sheet_addin.xlam")
        val = addin_book.sheets["xlwings.conf"].range("B1").value
        sg.popup(f"current value is {val}")

    elif platform.system() == "Darwin":
        sg.popup("Implementation for Mac doesn't exist yet")
        import sys
        sys.exit
    else:
        sg.popup("Oops, we only support Mac and Windows")
        import sys
        sys.exit()

def return_existing_asins(inventory_sht):
    """
    given the inventory sheet (as an xlwings sheet object), returns a set of asins in the inventory sheet
    """
    asin_rows_to_index = {"asin1":16,"asin2":17,"asin3":18}
    row_num = inventory_sht.range('A1').current_region.last_cell.row
    sg.popup(f"row_num is {row_num}")
    existing_asins = set()

    if row_num == 1:
        return existing_asins
    
    values = inventory_sht.range("A2:AE"+str(row_num)).value

    if row_num == 2:
        values = [values] #this is because we assume values is a list of lists,
        #but if there is only one row, 

    for row in values:
        asin_rows_index = [asin_rows_to_index["asin1"], asin_rows_to_index["asin2"], asin_rows_to_index["asin3"]]
        for index in asin_rows_index:    
            if row[index] != None:
                existing_asins.add(row[index])
            else:
                pass    
    return existing_asins


@debug_basic(True)
def export_data(use_Process=False):
    ask_to_go_to_wb_click_ok_or_terminate(name="the Arbitrage Master Sheet", keep_on_top=True, 
    affirmative_response="OK")

    import xlwings as xw

    master_sheet = xw.apps.active.books.active.sheets.active

    product_id_types = {"ASIN":1,
    "ISBN":2,
    "UPC":3,
    "EAN":4}
    product_id_types_list = list(product_id_types.keys())

    product_id_to_data_skeleton = {"id_type":None, "PRODUCT NAME":None, "SKU":None, "Condition":None}
    product_id_to_data = {}

    to_read_after_product_id = ["SKU","PURCHASE PRICE", "Qty", "ORDER DATE", "CONDITION", "PRICE"]
    


    select_name_and_click_ok_or_terminate("ASINs", keep_on_top=True, affirmative_response={"OK"})


    current_address = xw.apps.active.books.active.selection.address

    from Excelutilities import index_helpers
    while index_helpers.is_from_single_col(current_address) == False:
        user_output = sg.popup_yes_no("Please select from a single column block.\nClick Yes to continue and reselect, or No to terminate the program",
        keep_on_top=True)
        if user_output == "No":
            import sys
            sys.exit()
        else:
            current_address = xw.apps.active.books.active.selection.address
    


    first_and_lasts = [index_helpers.first_and_last_row_index(block) for block in current_address.split(",")]

    for first_row_index, last_row_index in first_and_lasts:
        
        address_for_master = "A" + str(first_row_index) + ":O"+str(last_row_index) 
        for row in master_sheet.range(address_for_master).value:
            values = row
            product_id = None
            id_type = None
            for id_type in product_id_types_list:
                index  = master_col_names_to_indices[id_type]
                if values[index] != None:
                    product_id = values[index]
                    id_type = product_id_types[id_type]
                    break
            if product_id == None:
                print("Oops this row has no product_id")
                continue
            
            if product_id in product_id_to_data:
                current_dict = product_id_to_data[product_id]
            else:
                product_id_to_data[product_id] = product_id_to_data_skeleton.copy()
                current_dict = product_id_to_data[product_id]
                
            current_dict["id_type"] = id_type
            
            for attribute in to_read_after_product_id:
                current_dict[attribute] = values[master_col_names_to_indices[attribute]]
            
        

    amazon_flat_loader_output_cols = {'sku':0,
    'product-id':1,
    'product-id-type':2,
    'price':3,
    'minimum-seller-allowed-price':4,
    'maximum-seller-allowed-price':5,
    'item-condition':6,
    'quantity':7,
    'add-delete':8,
    'will-ship-internationally':9,
    'expedited-shipping':10,
    'item-note':11}

    output_cols = ['sku',
    'product-id',
    'product-id-type',
    'price',
    'minimum-seller-allowed-price',
    'maximum-seller-allowed-price',
    'item-condition',
    'quantity',
    'add-delete',
    'will-ship-internationally',
    'expedited-shipping',
    'item-note']

    def reversed_dict(dictionary):
        """
        reverses the keys of a dictionary which are hashable and assumes the mappings are one to one
        """
        return_dict= {}
        for key in dictionary:
            return_dict[dictionary[key]] = key
        return return_dict

    internal_names_to_output_names = {"id_type":"product-id-type", "SKU":"sku", "CONDITION":"item-condition", "PRICE":"price"}
    output_names_to_internal_names = reversed_dict(internal_names_to_output_names)

    import pkg_resources

    AMAZON_MASTER_FILE = pkg_resources.resource_filename('ArbMasterPy', 'data/Amazon standard inventory - flat file.xlsm')
    src_path = AMAZON_MASTER_FILE
    layout = [[sg.Text('Select the output location of your master sheet'), sg.Input(),sg.FolderBrowse(key="--input_file--")],
                [sg.OK(), sg.Cancel()]]
    event, values = sg.Window("",layout, no_titlebar=False, keep_on_top=True, grab_anywhere=True).read(close=True)

    import os

    dest_path=os.path.join(values[0], "amazon_master_output.xlsm")

    import shutil

    shutil.copyfile(src_path, dest_path)

    existing_asins = return_existing_asins(inventory_sht=xw.apps.active.books.active.sheets["Inventory"])


    return_array = []
    for product_id in product_id_to_data:
        if product_id in existing_asins:
            continue
        else:
            current_dict = product_id_to_data[product_id]
            row = [current_dict[output_names_to_internal_names[col]] if col in output_names_to_internal_names else None for col in output_cols]
            row[amazon_flat_loader_output_cols['product-id']] = product_id
            return_array.append(row)

    xw.Book(dest_path)
    xw.apps.active.books.active.sheets["Master"]["A2"].value = return_array

    xw.Book(dest_path)


def export_data_process(use_process=False):
    import platform
    if platform.system() == "Windows" and use_process==False:
        from multiprocessing import Process
        p = Process(target=export_data_process, args=(True,));p.start() #pass it into process, but with instructions now to skip the system check as we know we are using a process
        return
    elif platform.system() == "Darwin":
        pass
    else:
        pass
    export_data()
    

@debug_basic(True)
def generate_sku(allowed_data_types = [str]):
    """
    PLACEHOLDER
    """
    select_name_and_click_ok_or_terminate("input product names", keep_on_top=True, affirmative_response={"OK"})
    import xlwings as xw
    input_col_name_1 = xw.apps.active.books.active.selection.value
    input_col_name_1_address = xw.apps.active.books.active.selection.address
    asin_list = input_col_name_1


    from ArbMasterPy.get_other_row_data import get_other_row_data
    date_list=get_other_row_data(column_mappings, curr_attr="ASIN", new_attr="Order Date", 
    target_sheet=xw.apps.active.books.active.sheets.active,
    target_address=input_col_name_1_address)
    

    sku_list = []
    from ArbMasterPy.inventory_data import get_attribute
    asin_sku_dict = get_attribute('seller-sku') #Ethan
    import datetime
    select_name_and_click_ok_or_terminate("SKU column", keep_on_top=True, affirmative_response={"OK"})
    active_cells = xw.apps.active.books.active.selection


    import sys
    from Excelutilities import importing_data_helpers
    def sanity_check_col_entries(entry1, entry2, addresses_and_names, sys=sys, importing_data_helpers=importing_data_helpers):
        #entry1 is a list of values
        #addresses_and_names is a list of tuples, first entry of tuple
        #is the address, and second is the name
        #implements some sanity checks
        if len(entry1) != len(entry2):
            sg.popup("Oops! Your two input columns of data are of different lengths.\nNow terminating...",
            keep_on_top=True)
            sys.exit()


        for val1, val2 in zip(entry1, entry2):
            if type(val1) not in allowed_data_types and val1 != None:
                sg.popup(f"Oops you selected some data which we couldn' recognise\nValue: {val1}",
                keep_on_top=True)
                sys.exit()

            if type(val2) not in allowed_data_types and val2 != None:
                sg.popup(f"Oops you selected some data which we couldn' recognise\n{val2}\n{type(val2)}",
                keep_on_top=True)
                sys.exit()
        
        for address_and_name in addresses_and_names:
            address = address_and_name[0]
            name = address_and_name[1]
            if not importing_data_helpers.is_col_block_bool(address):
                print(address)
                sg.popup(f"Oops! Your {name} data wasn't from a single column",
                keep_on_top=True)
                sys.exit()

    #sanity checks


    for asin,date in zip(asin_list,date_list):
        date = datetime.datetime.strftime(date, '%d-%m-%Y')
        if asin in asin_sku_dict:
            sku_list.append([asin_sku_dict[asin]])
        else:
            sku_list.append([str(asin) + '-'+str(date)])

    active_cells.value = [sku for sku in sku_list]


    #def sku_helper(product_name):
    #    if product_name == None:
    #        return None
    #    else:
    #        return "".join([char for char in product_name if char.isalpha()])[:15]    
     
    #active_cells.value = [[sku_helper(product_name)] for product_name in input_col_name_1]


def generate_sku_process(use_process=False):
    """
    a wrapper to use for if the underlying function has a decorator, so we can pass into multithreading.Process
    """
    import platform
    if platform.system() == "Windows" and use_process==False:
        from multiprocessing import Process
        p = Process(target=generate_sku_process, args=(True,));p.start() #pass it into process, but with instructions now to skip the system check as we know we are using a process
        return
    elif platform.system() == "Darwin":
        pass
    else:
        pass
    generate_sku()

@debug_basic(True)
def export_shipping_sheet():
    max_num_asins_shipping = 500
    max_num_asins_master = 5000
    select_name_and_click_ok_or_terminate(name="the shipping address data", keep_on_top=True,affirmative_response="OK")
    import xlwings as xw
    wb = xw.apps.active.books.active
    shipping_data_block = wb.selection.value
    sg.popup(f"Currently, this only works with a max of {max_num_asins_shipping} ASINs")
    asin_qty_data = wb.sheets["Shipment form"].range("A2:B"+str(2+max_num_asins_shipping)).value
    asin_qty_data = [row for row in asin_qty_data if row != [None, None]]
    sg.popup(f"This temporary solution assumes you have max {max_num_asins_master} ASINs in your MASTER sheet")
    master_data = wb.sheets["Master"].range("A2:"+master_data_last_letter+ str(max_num_asins_master)).value
    asin_index = master_col_names_to_indices["ASIN"]
    sku_index = master_col_names_to_indices["SKU"]

    asins = [row[asin_index] for row in master_data]
    skus = [row[sku_index] for row in master_data]

    asins_to_skus = dict(zip(asins, skus))

    #Now we get SKUs from inventory, and it takes priority over asins got from the master
    max_num_asins_inventory = max_num_asins_master
    from ArbMasterPy.inventory_data import get_attribute
    inventory_asins_skus = get_attribute(attr='seller-sku')
    for asin in inventory_asins_skus.keys():
        if asin in asins_to_skus:
            asins_to_skus[asin] = inventory_asins_skus[asin]

    
    #we keep track of all asins we couldn't find an sku for
    asins_without_sku = []

    #we create an array, 2xN, with skus and qty data
    sku_qty_data = []
    for row in asin_qty_data:
        qty = row[1]
        asin = row[0]
        if asin in asins_to_skus:
            sku = asins_to_skus[asin]
            if sku != None:
                sku_qty_data.append([sku, qty])
            else:
                asins_without_sku.append([asin, qty])
        else:
            asins_without_sku.append([asin, qty])

    sku_qty_data += asins_without_sku #i.e. all the asins with no SKUs go at the end
    
    #when skus or asins appear twice, we add the quantities and remove the second appearace
    matching_index = 0 #This is collecting 0th column, i.e. the ASINs (could be selected)
    value_index = 1 #This is collecting the quantities which are added (could be selected)
    checking_list = []

    #Find all the locations

    for index, row in enumerate(sku_qty_data):
        if sku_qty_data[index][matching_index] in checking_list:
            pass
        else:
            checking_list.append(sku_qty_data[index][matching_index])


    #Produce the new values
    temp = 0
    outputs = []
    for asin in checking_list:
        for row in sku_qty_data:
            if row[matching_index] == asin:
                temp += row[value_index]
        outputs.append(temp)
        temp = 0

    #Replace the sku_qty_data with the new values

    sku_qty_data = [list(a) for a in zip(checking_list, outputs)]

    return_value = [["PlanName", "NOT AUTOMATED YET"], ["ShipToCountry", "UK"]] + shipping_data_block + [["AddressDistrct",None],[None,None], ["MerchantSKU", "Quantity"]] + sku_qty_data

    print(f"SHIPPING DATA BLOCK IS: {shipping_data_block}")

    print(f"SKU QTY DATA IS: {sku_qty_data}")


    import pkg_resources

    AMAZON_SHIPPING_TEMPLATE = pkg_resources.resource_filename('ArbMasterPy', 'data/CreateInboundPlanRequest.xlsx')
    src_path = AMAZON_SHIPPING_TEMPLATE
    layout = [[sg.Text('Select the output location of your shipping sheet'), sg.Input(),sg.FolderBrowse(key="--input_file--")],
                [sg.OK(), sg.Cancel()]]
    event, values = sg.Window("",layout, no_titlebar=False, keep_on_top=True, grab_anywhere=True).read(close=True)

    import os

    dest_path=os.path.join(values[0], "CreateInboundPlanRequest.xlsx")

    import shutil

    shutil.copyfile(src_path, dest_path)

    xw.Book(dest_path)

    xw.apps.active.books.active.sheets["Create Shipping Plan Template"]["A1"].value = return_value

def export_shipping_sheet_process(use_process=False):
    import platform
    if platform.system() == "Windows" and use_process==False:
        from multiprocessing import Process
        p = Process(target=export_shipping_sheet_process, args=(True,));p.start() #pass it into process, but with instructions now to skip the system check as we know we are using a process
        return
    elif platform.system() == "Darwin":
        pass
    else:
        pass
    export_shipping_sheet()


if __name__ == "__main__":
   export_shipping_sheet()