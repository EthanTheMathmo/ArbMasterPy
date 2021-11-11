import PySimpleGUI as sg

from ArbMasterPy.debug_wrapper import debug_basic
import xlwings as xw

throttle_rate = float(xw.apps.active.books.active.sheets["API"].range("B4").value) #to control rate of requests to server so we dont get throttled
num_results_shown = int(xw.apps.active.books.active.sheets["API"].range("B2").value)
too_good_to_be_true = float(xw.apps.active.books.active.sheets["API"].range("B3").value)
search_param = xw.apps.active.books.active.sheets["API"].range("B5").value # search_param should be "" to use google search, and "shop" to use shopping

api_key = xw.apps.active.books.active.sheets["API"].range("B1").value

import pkg_resources
html_save_loc = pkg_resources.resource_filename('ArbMasterPy', 'data/arbitrage_results_html.html')

def asin_element_to_amazon_links(asin_element):
    #given the asin element, extracts the link to the amazon page
    return asin_element.find_all("a", {"class":"amazon-link btn btn-xs btn-primary"})[0]["href"]

import os
def newest(path):
    #from SO. Returns the newest file in a durectory
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

def get_html_code():
    from pathlib import Path
    downloads_path = str(Path.home() / "Downloads")
    file_loc = newest(downloads_path)
    if "SAS" not in file_loc:
        sg.popup("We couldn't recognize the most recent download - please check it and tell us what it is")
        import sys
        sys.exit()
    HtmlFile = open(file_loc, 'r', encoding='utf-8')
    source_html_code = HtmlFile.read() 
    return source_html_code

def extract_name_and_max_price(asin_element):
    name = asin_element.find("a")["data-original-title"]
    max_price = asin_element.find("span", {"class":"qi-max-cost pseudolink"}).text
    return (name, max_price)

def get_products_and_product_names_and_names_prices(source_html_code):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(source_html_code, "html.parser")
    # print(soup.get_text())
    b=soup.body
    products = b.find("div", {"id":"search-results"}).find_all("a")
    def sort_function(product):
        if product.has_attr("data-original-title"):
            if product["data-original-title"] != "":
                return True
        return False
        
    products = [product for product in products if sort_function(product)]
    product_names = [product["data-original-title"] for product in products]

    asin_elements = [element for element in b.find("div", {"id":"search-results"}).find_all("div") if element.has_attr("asin")]

    names_prices = [extract_name_and_max_price(asin_element) for asin_element in asin_elements]

    names_to_amz_link = dict(zip([name for name,price in names_prices], [asin_element_to_amazon_links(element) for element in asin_elements]))


    return products, product_names, names_prices, names_to_amz_link

import re
def get_price(x):
    return float(re.search("[0-9]+[.][0-9]+", x).group())

import difflib
def search_shopping(search_q, tbm_param="shop"):
    from serpapi import GoogleSearch
    import os 
    
    api_key = "ec63b5d769ebfe574934ac3816f218131cf92ccb461375aee6bc5926569f9933"
    
    if tbm_param == "shop":
    
        params = {
            "engine": "google",
            "q": search_q,
            "location":"United Kingdom",
            "gl": "uk",
            "tbm": "shop",
            "api_key": api_key,
        }

        print("INITIALIZING SEARCH")    

        search = GoogleSearch(params)
        results = search.get_dict()

        try:
            source_and_price_and_link_and_title = [(result["source"], result["extracted_price"], result["link"], result["title"]) for result in results["shopping_results"]]
            source_and_price_and_link_and_title.sort(key=lambda x:1-difflib.SequenceMatcher(None,x[3], search_q).ratio())
            source_and_price = [(x[0],x[1]) for x in source_and_price_and_link_and_title]
        except Exception as e:
            print(e)
            print(results)
            return None
        
    elif tbm_param == "":
        params = {
            "engine": "google",
            "q": search_q,
            "location":"United Kingdom",
            "gl": "uk",
            "api_key": api_key,
        }

        print("INITIALIZING SEARCH")    

        search = GoogleSearch(params)
        results = search.get_dict()
        try:
            organic_search = results["organic_results"]
            source_and_price_and_link_and_title = []
            for result in organic_search:
                try:
                    #this is bad form
                    price = result['rich_snippet']['top']['detected_extensions']['price']
                    link = result["link"]
                    title = result['title']
                    source = ""
                    source_and_price_and_link_and_title.append((source,price,link,title))                                                             
                except KeyError:
                    pass
            source_and_price_and_link_and_title.sort(key=lambda x:1-difflib.SequenceMatcher(None,x[3], search_q).ratio())
            source_and_price = [(x[0],x[1]) for x in source_and_price_and_link_and_title]
        except Exception as e:
            print(e)
            print(results)
            return None

        
    else:
        import PySimpleGUI as sg
        import sys
        sg.popup("did not recognise tbm param value")
        sys.exit()
        
    
    return results, source_and_price_and_link_and_title, source_and_price

def apply_filters_to_source_price_link(source_price_link_title, target_price, blacklist = ["ebay", "etsy", "alibaba", "idealo", "onbuy"]):
    new_return = []
    
    for source, price, link,title in source_price_link_title:
        trigger_activated=False
        if price < too_good_to_be_true*target_price or price > target_price:
            continue
            
        trigger_activated = False
        for trigger in blacklist:
            if trigger in link.lower() or trigger in source.lower():
                trigger_activated=True
                break
        
        if not trigger_activated:
            new_return.append((source, price, link, title))
            
    return new_return

def target_items(search_results_data, names_and_prices_filtered):
    """
    Given the results, and the names_price data we wanted to check, we return a list of those which meet the criterion
    
    search_results_data is a list of 3-tuples (results, source_and_price_and_link, source_and_price) of which we just need the second
    value
    """
    sources_and_prices_and_links_and_titles = search_results_data
    
    return_list = []
    
    for source_price_link_title, name_price in zip(sources_and_prices_and_links_and_titles, names_and_prices_filtered):
        target_price = name_price[1]
        result_prices = [x[1] for x in source_price_link_title]
        
        if sum([price < target_price for price in result_prices[:3]])>=2:
            #require 2 of the top 3 prices to be below 
            return_list.append([name_price[0], name_price[1], source_price_link_title[:num_results_shown]])
        else:
            pass
        
    return return_list

def generate_html_string(best_items, names_to_amz_link):
    return_string = ""
    for row in best_items:
        return_string += f"Item: {row[0]}<br>Target Price: {row[1]}<br><a href={names_to_amz_link[row[0]]}>Amazon link</a>"
        return_string += "<ol>"
        for item in row[2]:
            return_string += f"<li>Retailer: {item[0]}, Price: {item[1]}\n<a href={item[2]}>Website</a>\nTitle: {item[3]}</li>"
        return_string+="</ol>\n\n"
    return return_string

def sort_best_items(row):
    target_name = row[0]
    best_match = row[2][0][3]
    return 1-difflib.SequenceMatcher(None, target_name, best_match).ratio()

@debug_basic(value=True)
def user_function():
    sg.popup("Please download the html code and THEN click ok", keep_on_top=True)
    source_html_code = get_html_code()
    products, product_names, names_prices, names_to_amz_link = get_products_and_product_names_and_names_prices(source_html_code=source_html_code)
    
    names_prices_filtered = [x for x in names_prices if "-" not in x[1] and x[1]!="N/A"]

    names_prices_filtered = [(x[0], get_price(x[1])) for x in names_prices_filtered]

    res=[]
    i=0
    import time
    for name, price in names_prices_filtered:
        i+=1
        res.append(search_shopping(name, search_param))
        sg.one_line_progress_meter('One Line Meter Example', i + 1, len(names_prices_filtered))
        time.sleep(1)
    res = [x for x in res if x !=None] #remove search results where we had no results
    names_where_search_worked = set([res[j][0]["search_parameters"]["q"] for j in range(len(res))]) #get names where search results worked, so we can trim the name and price data
    names_prices_filtered = [x for x in names_prices_filtered if x[0] in names_where_search_worked] #i.e., only look at the results where our search had results

    filtered_results = [apply_filters_to_source_price_link(source_price_link_title=res[i][1], target_price=names_prices_filtered[i][1]) for i in range(len(res))]

    best_items=target_items(filtered_results, names_prices_filtered)

    best_items.sort(key=sort_best_items)

    import webbrowser


    f = open(html_save_loc,'w', encoding="utf-8")

    message = generate_html_string(best_items, names_to_amz_link)

    f.write(message)
    f.close()

    import platform
    if platform.system() == "Windows":
        webbrowser.open(f.name)
    elif platform.system() == "Darwin":
        import subprocess
        subprocess.call(('open', f.name))
    else:
        sg.popup("Oops, we only support Mac and Windows")
        import sys
        sys.exit()
    
if __name__ == "__main__":
    user_function()
