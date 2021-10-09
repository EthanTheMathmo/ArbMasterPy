import PySimpleGUI as sg



def return_existing_asins(inventory_sht):
    """
    given the inventory sheet (as an xlwings sheet object), returns a set of asins in the inventory sheet
    """
    asin_rows_to_index = {"asin1":16,"asin2":17,"asin3":18}
    row_num = inventory_sht.range('A1').current_region.last_cell.row
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




def export_data():
    product_id_types = {"ASIN":1,
    "ISBN":2,
    "UPC":3,
    "EAN":4}
    product_id_types_list = list(product_id_types.keys())

    product_id_to_data_skeleton = {"id_type":None, "PRODUCT NAME":None, "SKU":None, "Condition":None}
    product_id_to_data = {}


    col_names_to_indices = {"PRODUCT NAME":0, "ASIN":1, "ISBN":2, "UPC":3, "EAN":4, "SKU":5, "PURCHASE PRICE":6, 
                            "Qty":7, "ORDER DATE":8, "CONDITION":9, "PRICE":10}
    to_read_after_product_id = ["SKU","PURCHASE PRICE", "Qty", "ORDER DATE", "CONDITION", "PRICE"]
    import xlwings as xw
    default_file_loc = xw.apps.active.books.active.fullname
    layout = [[sg.Text('Select the file location of the master sheet'), sg.Input(default_file_loc),sg.FileBrowse(key="--input_file--")],
                [sg.OK(), sg.Cancel()]]
    event, values = sg.Window("",layout, no_titlebar=False, keep_on_top=True, grab_anywhere=True).read(close=True)

    xlsx_filename=values[0]
    
    import io

    with open(xlsx_filename, "rb") as f:
        #this needs to be done as well as wb.close to make sure the workbook doesnt get broken by saving and other actions
        
        in_mem_file = io.BytesIO(f.read())

    import openpyxl

    wb = openpyxl.load_workbook(in_mem_file, read_only=True)

    master_sheet = wb["Master"]

    sg.popup_ok(f"Please select the product keys for the items you wish to upload")


    current_address = xw.apps.active.books.active.selection.address

    from Excelutilities import index_helpers

    while index_helpers.is_from_single_col(current_address) == False:
        user_output = sg.popup_yes_no("Please select from a single column block.\nClick Yes to continue and reselect, or No to terminate the program")
        if user_output == "No":
            import sys
            sys.exit()
        else:
            current_address = xw.apps.active.books.active.selection.address
    
    first_and_lasts = [index_helpers.first_and_last_row_index(block) for block in current_address.split(",")]

    for first_row_index, last_row_index in first_and_lasts:
        
        address_for_master = "A" + str(first_row_index) + ":K"+str(last_row_index) 
        for row in master_sheet[address_for_master]:
            values = [cell.value for cell in row]
            product_id = None
            id_type = None
            for id_type in product_id_types_list:
                index  = col_names_to_indices[id_type]
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
                current_dict[attribute] = values[col_names_to_indices[attribute]]
            
        
    wb.close() #this needs to be done so that the workbook isn't broken. 


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

def generate_sku( sys, importing_data_helpers, xw, allowed_data_types = [str]):
    """
    PLACEHOLDER
    """
    sg.popup_ok(f"Please select the input product names and click 'ok' when finished")
    input_col_name_1 = xw.apps.active.books.active.selection.value
    input_col_name_1_address = xw.apps.active.books.active.selection.address
    sg.popup_ok(f"Please select the SKU column and click 'ok' when finished")
    active_cells = xw.apps.active.books.active.selection
    input_col_name_2 = active_cells.value
    input_col_name_2_address = active_cells.address


    def sanity_check_col_entries(entry1, entry2, addresses_and_names, sys=sys, importing_data_helpers=importing_data_helpers):
        #entry1 is a list of values
        #addresses_and_names is a list of tuples, first entry of tuple
        #is the address, and second is the name
        #implements some sanity checks
        if len(entry1) != len(entry2):
            sg.popup("Oops! Your two input columns of data are of different lengths.\nNow terminating...")
            sys.exit()


        for val1, val2 in zip(entry1, entry2):
            if type(val1) not in allowed_data_types and val1 != None:
                sg.popup(f"Oops you selected some data which we couldn' recognise\nValue: {val1}")
                sys.exit()

            if type(val2) not in allowed_data_types and val2 != None:
                sg.popup(f"Oops you selected some data which we couldn' recognise\n{val2}\n{type(val2)}")
                sys.exit()
        
        for address_and_name in addresses_and_names:
            address = address_and_name[0]
            name = address_and_name[1]
            if not importing_data_helpers.is_col_block_bool(address):
                print(address)
                sg.popup(f"Oops! Your {name} data wasn't from a single column")
                sys.exit()

    #sanity checks
    sanity_check_col_entries(entry1=input_col_name_1, entry2=input_col_name_2, 
                addresses_and_names=[(input_col_name_1_address, "col_name_1"),(input_col_name_2_address, "col_name_2")])

    
    def sku_helper(product_name):
        if product_name == None:
            return None
        else:
            return "".join([char for char in product_name if char.isalpha()])[:15]    
     
    active_cells.value = [[sku_helper(product_name)] for product_name in input_col_name_1]


if __name__ == "__main__":
    print("Uhhh")