from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import Result, User, Blacklist
from datetime import datetime
import PySimpleGUI as sg
import pkg_resources
import os
import re
import difflib


#from ArbMasterPy.debug_wrapper import debug_basic


# Create your views here.




def summary(request):
    if not request.user.is_authenticated:
        return render(request, "scraping/login.html")
    return render(request, "scraping/summary.html", {
        "best_items": best_items,
        "blacklist": blacklist,
        "database_blacklist": Blacklist.objects.all()
    })

def index(request):
    # If no user is signed in, return to login page:
    if not request.user.is_authenticated:
        return render(request, "scraping/login.html")
    return render(request, "scraping/index.html", {
        "users": User.objects.all(),
        "results": Result.objects.all()
    })

def login_view(request):
    if request.method == "POST":
        # Accessing username and password from form data
        username = request.POST["username"]
        password = request.POST["password"]

        # Check if username and password are correct, returning User object if so
        user = authenticate(request, username=username, password=password)

        # If user object is returned, log in and route to index page:

        if user:
            login(request, user)
            return render(request, "scraping/summary.html")
        # Otherwise, return login page again with new context
        else:
            return render(request, "scraping/login.html", {
                "message": "Invalid Credentials"
            })
    return render(request, "scraping/login.html")

def logout_view(request):
    logout(request)
    return render(request, "scraping/login.html", {
                "message": "Logged Out"
            })

def add_to_blacklist(request):
    if not request.user.is_authenticated:
        return render(request, "scraping/login.html")
    if request.method == "POST":

        form = NewSiteForm(request.POST)

        if form.is_valid():
            site = form.cleaned_data["site"]
            b = Blacklist(username=request.user.username, url=site)
            b.save()
            blacklist.append(site)

            return render(request, "scraping/summary.html", {
                "best_items": best_items,
                "blacklist": blacklist,
                "database_blacklist": Blacklist.objects.all()
            })

        else:

            return render(request, "scraping/add_to_blacklist.html", {
                "form": form
            })

    return render(request, "scraping/add_to_blacklist.html", {
        "form": NewSiteForm()
    })

def remove_from_blacklist(request):
    if request.method == "POST":

        form = SelectForm(request.POST)

        if form.is_valid():
            

            Blacklist.objects.filter(url=form.cleaned_data["choice"]).delete()
            
            return render(request, "scraping/summary.html", {
                "best_items": best_items,
                "blacklist": blacklist,
                "database_blacklist": Blacklist.objects.all()
            })

        else:

            return render(request, "scraping/remove_from_blacklist.html", {
                "form": form
            })

    return render(request, "scraping/remove_from_blacklist.html", {
        "form": SelectForm(request.POST)
    })


def generate_results(request):


    
    throttle_rate = 1.2
    num_results_shown = 8
    too_good_to_be_true = 0.6
    search_param = "shop"
    api_key = "dbb87d1b21afef383ae66bf3cd90f73ce1c96bd12eefc379f8684b6fac1f6834"


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

    def sort_best_items(row):
        target_name = row[0]
        best_match = row[2][0][3]
        return 1-difflib.SequenceMatcher(None, target_name, best_match).ratio()




    form = ReadFileForm()
    if request.method == "POST":
        form = ReadFileForm(request.POST, request.FILES)
        if form.is_valid():
            html_file = request.FILES['file']
            source_html_code = html_file.read()
            #All fine till here
            
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
            
            filtered_results = [apply_filters_to_source_price_link(source_price_link_title=res[i][1], target_price=names_prices_filtered[i][1]) for i in range(len(res))]
            #All fine till here
            best_items=target_items(filtered_results, names_prices_filtered)
            best_items.sort(key=sort_best_items)


            return render(request, "scraping/summary.html", {
                "best_items": best_items,
                "blacklist": blacklist,
                "database_blacklist": Blacklist.objects.all()
            })




    return render(request, "scraping/generate_results.html", {
        "form": form
    
    })


########################################################################

BLACKLIST_CHOICES = []

for site in Blacklist.objects.all():
    BLACKLIST_CHOICES.append((site.url, site.url))


class NewSiteForm(forms.Form):
    site = forms.CharField(label="site")

class SelectForm(forms.Form):
    choice = forms.ChoiceField(choices = BLACKLIST_CHOICES, label="", initial='', widget=forms.Select(), required=True)

class ReadFileForm(forms.Form):
    file = forms.FileField()


blacklist = ["ebay.com", "etsy.com", "alibaba.com", "idealo.com", "onbuy.com"]


#So, we actually want to use the code, returning two things, some summary html and the html lines
#This means basically return best_items

best_items = [[' Thomas & Friends 4 in Box (12, 16, 20, 24 Piece) Jigsaw Puzzles for Kids Age 3 Years and Up', 3.02, [('Poundshop.com', 1.09, 'https://www.google.com/url?url=https://www.poundshop.com/princess-palace-45-piece-puzzle.html&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECNIM&usg=AOvVaw3iQHIJeVD3UuvspaQoaU4Q', 'Grafix Princess Palace Puzzle'), ('Wish', 1.95, 'https://www.google.com/url?url=https://www.wish.com/c/5f18eba2cdebcc1eb01074c0%3Fhide_login_modal%3Dtrue%26from_ad%3Dgoog_shopping_organic%26_display_country_code%3DGB%26_force_currency_code%3DGBP%26pid%3Dgoogleadwords_int%26c%3D%257BcampaignId%257D%26ad_cid%3D5f18eba2cdebcc1eb01074c0%26ad_cc%3DGB%26ad_curr%3DGBP%26ad_price%3D2.00&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QgOUECKML&usg=AOvVaw0pNMfl8NXdwfp3i8pfmEgS', 'Early Educational Toy Developing for Children Jigsaw Digital Number 1-16 Animal ...'), ('Plaza Japan', 3.49, 'https://www.google.com/url?url=https://www.plazajapan.com/4905096251229/%3FsetCurrencyId%3D1&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECPIK&usg=AOvVaw0f8khdaeyRNNBZvlQLbSDe', 'Apollo-sha 25-122 Jigsaw Puzzle Thomas & Friends Collection of Characters (85 ...'), ('Plaza Japan', 3.49, 'https://www.google.com/url?url=https://www.plazajapan.com/4905096251236/%3FsetCurrencyId%3D1&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECIcM&usg=AOvVaw3PYOmHgeIFFJYo9g7aP6Zg', 'Apollo-sha 25-123 Jigsaw Puzzle Thomas & Friends Collection of Characters (63 ...'), ('Early Learning Centre', 5.0, 'https://www.google.com/url?url=https://www.elc.co.uk/games-jigsaws/jigsaws/jigsaw-0-49/Ravensburger-My-First-Jigsaw-Puzzle---Thomas-%2526-Friends/p/547679%3Futm_source%3Dgoogle%26utm_medium%3Dorganic%26utm_campaign%3Dorganicshopping&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECJcI&usg=AOvVaw0ki0wrM1MuVcx19iLArN5U', 'Thomas & Friends My First Jigsaw Puzzles')]], ['Ravensburger Peppa Pig London Red Bus 24 Piece Giant Shaped Floor Jigsaw Puzzle for Kids Age 3 Years Up - Educational Toys for Toddlers', 4.73, [('Wish', 1.95, 'https://www.google.com/url?url=https://www.wish.com/c/5f18eba2cdebcc1eb01074c0%3Fhide_login_modal%3Dtrue%26from_ad%3Dgoog_shopping_organic%26_display_country_code%3DGB%26_force_currency_code%3DGBP%26pid%3Dgoogleadwords_int%26c%3D%257BcampaignId%257D%26ad_cid%3D5f18eba2cdebcc1eb01074c0%26ad_cc%3DGB%26ad_curr%3DGBP%26ad_price%3D2.00&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQgOUECN4L&usg=AOvVaw0frbXB3UPL2oATENRqGNg-', 'Early Educational Toy Developing for Children Jigsaw Digital Number 1-16 Animal ...'), ('The Range', 3.49, 'https://www.google.com/url?url=https://www.therange.co.uk/toys/cards-puzzles-and-board-games/children-s-puzzles/30-piece-peppa-pig-puzzle%23322009&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQgOUECJkL&usg=AOvVaw2w6QTTb7h7rjtXimF4qgY0', 'Trefl - 30 Piece Peppa Pig Puzzle'), ('MyTrendyPhone.co.uk', 4.6, 'https://www.google.com/url?url=https://www.mytrendyphone.co.uk/shop/9-piece-jigsaw-puzzle-kids-educational-toy-269541p.html&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQguUECLUM&usg=AOvVaw1mGICjtZBSisIU1h7TfnXy', '9-Piece Jigsaw Puzzle for Kids / Educational Toy - School Bus'), ('Fab Finds', 4.99, 'https://www.google.com/url?url=https://fabfinds.co.uk/products/cbeebies-giant-number-floor-puzzle-30-pieces&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQguUECNML&usg=AOvVaw1e5WtJHbKdtMK9XvU6PWQE', 'Cbeebies - Giant Number Floor Puzzle'), ('Smyths Toys', 5.0, 'https://www.google.com/url?url=https://www.smythstoys.com/uk/en-gb/toys/products/ravensburger-peppa-pig-4-in-a-box-jigsaw-puzzle/p/164273%3Futm_source%3Dgoogle%26utm_medium%3Dorganic%26utm_campaign%3Dsurfaces_across_google&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQ_uQECIYJ&usg=AOvVaw3nkXizWejPrfiO-k-T0gD_', 'Ravensburger Peppa Pig 4 in a Box (12, 16, 20, 24 piece) Jigsaw Puzzles')]]]
