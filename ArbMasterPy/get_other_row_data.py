def get_other_row_data(active_column_mapping, curr_attr, new_attr, target_sheet, target_address):
    """
    active_column_mapping maps from column names ('attributes') to indices

    curr_attr is the attribute (column name) the user selected
    
    new_attr is the different attribute we want to fetch
    
    Both curr_attr and new_attr should be in active_column_mapping
    
    target_address is the address the user selected.
    target_address can be multiple blocks from within the same column, but must only be from
    one column (e.g., A1:A6,A8:A12 is allowed, A1:A6,B7:B12 is not)

    target_sheet is an xlwings sheet object


    """
    def add_tuples(a,b):
        return tuple(p+q for p, q in zip(a, b))

    
    from Excelutilities.index_helpers import convert_to_tuple, convert_from_tuple, return_address_col_index
    address_as_list = target_address.split(",")

    curr_attr_index = active_column_mapping[curr_attr]
    new_attr_index = active_column_mapping[new_attr]

    diff= new_attr_index - curr_attr_index  

    new_address_as_list = []

    for chunk in address_as_list:
        first = chunk.split(":")[0]
        second = chunk.split(":")[1]
        first_new = convert_from_tuple(add_tuples(convert_to_tuple(first),(diff,0)))
        second_new = convert_from_tuple(add_tuples(convert_to_tuple(second),(diff,0)))
        tuple(p+q for p, q in zip(convert_to_tuple(first), (0,diff)))

        new_address_as_list.append(first_new+":"+second_new)
    
    target_address = ",".join(new_address_as_list)
    
    return target_sheet.range(target_address).value

    


