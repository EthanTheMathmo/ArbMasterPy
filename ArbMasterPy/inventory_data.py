column_mappings = {'item-name': 0,
 'item-description': 1,
 'listing-id': 2,
 'seller-sku': 3,
 'price': 4,
 'quantity': 5,
 'open-date': 6,
 'image-url': 7,
 'item-is-marketplace': 8,
 'product-id-type': 9,
 'zshop-shipping-fee': 10,
 'item-note': 11,
 'item-condition': 12,
 'zshop-category1': 13,
 'zshop-browse-path': 14,
 'zshop-storefront-feature': 15,
 'asin1': 16,
 'asin2': 17,
 'asin3': 18,
 'will-ship-internationally': 19,
 'expedited-shipping': 20,
 'zshop-boldface': 21,
 'product-id': 22,
 'bid-for-featured-placement': 23,
 'add-delete': 24,
 'pending-quantity': 25,
 'fulfilment-channel': 26,
 'merchant-shipping-group': 27,
 'status': 28,
 'Minimum order quantity': 29,
 'Sell remainder': 30}

first_letter = "A"
last_letter = "AE"

def get_attribute(attr):
    import PySimpleGUI as sg
    sg.popup("Currently this feature works with a max of 5000 ASINs in the inventory")
    import xlwings as xw
    last_row = 5000
    data = xw.apps.active.books.active.sheets["Inventory"].range(f"A1:{last_letter +str(last_row)}").value
    asin_index = column_mappings["asin1"]
    target_index = column_mappings[attr]

    asins = [row[asin_index] for row in data]
    targets = [row[target_index] for row in data]

    for index, val in enumerate(targets):
        if type(val) == float:
            targets[index] = str(int(val))

    return dict(zip(asins, targets))

if __name__=="__main__":
    print(get_attribute('seller-sku'))
