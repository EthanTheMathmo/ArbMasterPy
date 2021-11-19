import re
import difflib
from datetime import datetime
from .models import Result, User, User_search_count
from requests.sessions import Request

#best_items indices
best_items_indices = {"source_product":0, "target_price":1, "amz_link":2, "search_results":3} 
        #source product is amazon item, 
search_results_indices = {"retailer_name":0, "retailer_price":1, "web address":2, "product":3} 

def asin_element_to_amazon_links(asin_element):
#given the asin element, extracts the link to the amazon page

    return asin_element.find_all("a", {"class":"amazon-link btn btn-xs btn-primary"})[0]["href"]

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

def get_price(x):
    return float(re.search("[0-9]+[.][0-9]+", x).group())


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


        search = GoogleSearch(params)
        results = search.get_dict()

        try:
            source_and_price_and_link_and_title = [(result["source"], result["extracted_price"], result["link"], result["title"]) for result in results["shopping_results"]]
            source_and_price_and_link_and_title.sort(key=lambda x:1-difflib.SequenceMatcher(None,x[3], search_q).ratio())
            source_and_price = [(x[0],x[1]) for x in source_and_price_and_link_and_title]
        except Exception as e:
            #TO-DO keep track of exceptions and what caused the problem so we can improve code
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
        import sys
        sys.exit()
    

    return results, source_and_price_and_link_and_title, source_and_price



def apply_filters_to_source_price_link(source_price_link_title, target_price,too_good_to_be_true, blacklist):
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


def target_items(search_results_data, names_and_prices_filtered, num_results_shown, names_to_amz_link):
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
            return_list.append([name_price[0], name_price[1], names_to_amz_link[name_price[0]],source_price_link_title[:num_results_shown]])
        else:
            pass
    
    return return_list

def sort_best_items(row):
    target_name = row[best_items_indices["source_product"]]
    best_match = row[best_items_indices["search_results"]][0][search_results_indices["product"]]
    return 1-difflib.SequenceMatcher(None, target_name, best_match).ratio()





def scraping_results(request, source_html_code, blacklist, throttle_rate, 
            num_results_shown, too_good_to_be_true, search_param, api_key):

    products, product_names, names_prices, names_to_amz_link = get_products_and_product_names_and_names_prices(source_html_code=source_html_code)

    names_prices_filtered = [x for x in names_prices if "-" not in x[1] and x[1]!="N/A"]

    names_prices_filtered = [(x[0], get_price(x[1])) for x in names_prices_filtered]
    #All fine till here
    res=[]
    for name, price in names_prices_filtered:
        res.append(search_shopping(name, search_param))
    res = [x for x in res if x !=None] #remove search results where we had no results
    
    #All fine till here
    names_where_search_worked = set([res[j][0]["search_parameters"]["q"] for j in range(len(res))]) #get names where search results worked, so we can trim the name and price data

    names_prices_filtered = [x for x in names_prices_filtered if x[0] in names_where_search_worked] #i.e., only look at the results where our search had results
    
    filtered_results = [apply_filters_to_source_price_link(source_price_link_title=res[i][1], target_price=names_prices_filtered[i][1], too_good_to_be_true=too_good_to_be_true, blacklist=blacklist) for i in range(len(res))]
    #All fine till here
    best_items=target_items(filtered_results, names_prices_filtered, num_results_shown=num_results_shown, names_to_amz_link=names_to_amz_link)
    best_items.sort(key=sort_best_items)

    #updating databases
    User_Info = User.objects.get(username=request.user.username)
    current_result_count = User_Info.requests
    User_Info.requests += 1
    User_Info.save()


    current_date = datetime.now()

    for result in best_items:
        source_product = result[best_items_indices["source_product"]]
        target_price = result[best_items_indices["target_price"]]

        for search_result in result[best_items_indices["search_results"]]:
            result_entry = Result()

            result_entry.username = request.user.username
            result_entry.product  = search_result[search_results_indices["product"]]
            result_entry.retailer = search_result[search_results_indices["retailer_name"]]
            result_entry.retailer_price = search_result[search_results_indices["retailer_price"]]
            result_entry.web_address = search_result[search_results_indices["web address"]]
            
            result_entry.amz_link = names_to_amz_link[source_product]

            result_entry.source_product = source_product
            result_entry.target_price = target_price

            result_entry.date = current_date

            result_entry.result_id = current_result_count

            result_entry.save()

    update_user_search_count = User_search_count()
    update_user_search_count.username = request.user.username
    update_user_search_count.date = datetime.now()
    update_user_search_count.number_searches_run = len(names_prices_filtered)
    update_user_search_count.number_of_searches_completed = len(res)
    update_user_search_count.number_of_results = len(best_items)
    update_user_search_count.save()

    return best_items