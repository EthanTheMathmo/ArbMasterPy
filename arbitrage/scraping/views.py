from django.db.models.query_utils import RegisterLookupMixin
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from requests.sessions import Request
from .models import Result, User, Blacklist, User_search_count
from datetime import datetime
from .scraping_code import scraping_results
from .forms import ReadFileForm


#from ArbMasterPy.debug_wrapper import debug_basic
from datetime import date, datetime

#best_items indices
from .scraping_code import best_items_indices, search_results_indices
 
# Create your views here.
def summary(request, result_index=0):
    #calculation_index by default is 0. Then it renders the most recent result
    #e.g., if you set calculation_index=1, then it would render the calculation done before the most recent
    if not request.user.is_authenticated:
        return render(request, "scraping/login.html")
    else:
        #reconstruct best_items from the database
        User_Info = User.objects.get(username=request.user.username)
        current_result_count = User_Info.requests-1-result_index #as User_info.requests is always 1 ahead we adjust by -1, and then go back by the number needed to get the Nth last result
        user_results = Result.objects.filter(username=request.user.username, result_id=current_result_count)
        best_items = []
        current_source_product = None
        current_target_price = None


        for item in user_results:

            if current_source_product != item.source_product:
                #add a source_product to best_items
                current_source_product = item.source_product
                current_target_price = item.target_price
                best_items.append([current_source_product, current_target_price, []])

            res = [0 for i in range(len(search_results_indices))]
            res[search_results_indices["retailer_name"]] = item.retailer
            res[search_results_indices["retailer_price"]] = item.retailer_price
            res[search_results_indices["web address"]] = item.web_address
            res[search_results_indices["product"]] = item.product
            best_items[-1][best_items_indices["search_results"]].append(res)



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
    form = ReadFileForm()
    if request.method == "POST":
        form = ReadFileForm(request.POST, request.FILES)
        if form.is_valid():
            html_file = request.FILES['file']
            source_html_code = html_file.read()
            #All fine till here
            
            throttle_rate = 1.2
            num_results_shown = 8
            too_good_to_be_true = 0.6
            search_param = "shop"
            api_key = "dbb87d1b21afef383ae66bf3cd90f73ce1c96bd12eefc379f8684b6fac1f6834"

            best_items= scraping_results(request=request, source_html_code=source_html_code, blacklist=blacklist, 
            throttle_rate=throttle_rate, num_results_shown=num_results_shown, too_good_to_be_true=too_good_to_be_true, 
            search_param=search_param, api_key=api_key)

            return render(request, "scraping/summary.html", {
                "best_items": best_items,
                "blacklist": blacklist,
                "database_blacklist": Blacklist.objects.all()
            })


    return render(request, "scraping/generate_results.html", {
        "form": form
    
    })

def userpage(request):

    user_profile = User.objects.get(username=request.user.username)

    return render(request, "scraping/userpage.html", {
        "username": user_profile.username,
        "requests": user_profile.requests,
        "flagged_requests": user_profile.flagged_requests,
        "to_be_billed": user_profile.to_be_billed
        
    })


BLACKLIST_CHOICES = []

for site in Blacklist.objects.all():
    BLACKLIST_CHOICES.append((site.url, site.url))


class NewSiteForm(forms.Form):
    site = forms.CharField(label="site")

class SelectForm(forms.Form):
    choice = forms.ChoiceField(choices = BLACKLIST_CHOICES, label="", initial='', widget=forms.Select(), required=True)



blacklist = ["ebay", "etsy", "alibaba", "idealo", "onbuy"]
#So, we actually want to use the code, returning two things, some summary html and the html lines
#This means basically return best_items

best_items = [['Posh Paws 49003 Jurassic World Camp Cretaceous Chunky Blue Velociraptor Dinosaur 10" Soft Toy (25cm)', 6.95, [('Yes Bébé', 6.27, 'https://www.google.com/url?url=https://yesbebe.co.uk/posh-paws/46502-jurassic-world-camp-cretaceous-plush-chunky-t-rex/&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjT7ubJwJv0AhWnlGoFHXhDCvgQgOUECKYL&usg=AOvVaw2xdhGVH4JAKldySu9urrQV', 'Jurassic World Camp Cretaceous Plush - Chunky T-rex'), ('Smyths Toys', 4.99, 'https://www.google.com/url?url=https://www.smythstoys.com/uk/en-gb/toys/action-figures-and-playsets/jurassic-world/jurassic-world-captivz-camp-cretaceous-slime-egg-assortment/p/197460%3Futm_source%3Dgoogle%26utm_medium%3Dorganic%26utm_campaign%3Dsurfaces_across_google&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjT7ubJwJv0AhWnlGoFHXhDCvgQ_uQECK8O&usg=AOvVaw1c23pDrnN2XYU2P7l7_wNC', 'Jurassic World Captivz Camp Cretaceous Slime Egg Assortment')]]]
added_items_for_test=[[' Thomas & Friends 4 in Box (12, 16, 20, 24 Piece) Jigsaw Puzzles for Kids Age 3 Years and Up', 3.02, [('Poundshop.com', 1.09, 'https://www.google.com/url?url=https://www.poundshop.com/princess-palace-45-piece-puzzle.html&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECNIM&usg=AOvVaw3iQHIJeVD3UuvspaQoaU4Q', 'Grafix Princess Palace Puzzle'), ('Wish', 1.95, 'https://www.google.com/url?url=https://www.wish.com/c/5f18eba2cdebcc1eb01074c0%3Fhide_login_modal%3Dtrue%26from_ad%3Dgoog_shopping_organic%26_display_country_code%3DGB%26_force_currency_code%3DGBP%26pid%3Dgoogleadwords_int%26c%3D%257BcampaignId%257D%26ad_cid%3D5f18eba2cdebcc1eb01074c0%26ad_cc%3DGB%26ad_curr%3DGBP%26ad_price%3D2.00&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QgOUECKML&usg=AOvVaw0pNMfl8NXdwfp3i8pfmEgS', 'Early Educational Toy Developing for Children Jigsaw Digital Number 1-16 Animal ...'), ('Plaza Japan', 3.49, 'https://www.google.com/url?url=https://www.plazajapan.com/4905096251229/%3FsetCurrencyId%3D1&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECPIK&usg=AOvVaw0f8khdaeyRNNBZvlQLbSDe', 'Apollo-sha 25-122 Jigsaw Puzzle Thomas & Friends Collection of Characters (85 ...'), ('Plaza Japan', 3.49, 'https://www.google.com/url?url=https://www.plazajapan.com/4905096251236/%3FsetCurrencyId%3D1&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECIcM&usg=AOvVaw3PYOmHgeIFFJYo9g7aP6Zg', 'Apollo-sha 25-123 Jigsaw Puzzle Thomas & Friends Collection of Characters (63 ...'), ('Early Learning Centre', 5.0, 'https://www.google.com/url?url=https://www.elc.co.uk/games-jigsaws/jigsaws/jigsaw-0-49/Ravensburger-My-First-Jigsaw-Puzzle---Thomas-%2526-Friends/p/547679%3Futm_source%3Dgoogle%26utm_medium%3Dorganic%26utm_campaign%3Dorganicshopping&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECJcI&usg=AOvVaw0ki0wrM1MuVcx19iLArN5U', 'Thomas & Friends My First Jigsaw Puzzles')]], ['Ravensburger Peppa Pig London Red Bus 24 Piece Giant Shaped Floor Jigsaw Puzzle for Kids Age 3 Years Up - Educational Toys for Toddlers', 4.73, [('Wish', 1.95, 'https://www.google.com/url?url=https://www.wish.com/c/5f18eba2cdebcc1eb01074c0%3Fhide_login_modal%3Dtrue%26from_ad%3Dgoog_shopping_organic%26_display_country_code%3DGB%26_force_currency_code%3DGBP%26pid%3Dgoogleadwords_int%26c%3D%257BcampaignId%257D%26ad_cid%3D5f18eba2cdebcc1eb01074c0%26ad_cc%3DGB%26ad_curr%3DGBP%26ad_price%3D2.00&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQgOUECN4L&usg=AOvVaw0frbXB3UPL2oATENRqGNg-', 'Early Educational Toy Developing for Children Jigsaw Digital Number 1-16 Animal ...'), ('The Range', 3.49, 'https://www.google.com/url?url=https://www.therange.co.uk/toys/cards-puzzles-and-board-games/children-s-puzzles/30-piece-peppa-pig-puzzle%23322009&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQgOUECJkL&usg=AOvVaw2w6QTTb7h7rjtXimF4qgY0', 'Trefl - 30 Piece Peppa Pig Puzzle'), ('MyTrendyPhone.co.uk', 4.6, 'https://www.google.com/url?url=https://www.mytrendyphone.co.uk/shop/9-piece-jigsaw-puzzle-kids-educational-toy-269541p.html&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQguUECLUM&usg=AOvVaw1mGICjtZBSisIU1h7TfnXy', '9-Piece Jigsaw Puzzle for Kids / Educational Toy - School Bus'), ('Fab Finds', 4.99, 'https://www.google.com/url?url=https://fabfinds.co.uk/products/cbeebies-giant-number-floor-puzzle-30-pieces&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQguUECNML&usg=AOvVaw1e5WtJHbKdtMK9XvU6PWQE', 'Cbeebies - Giant Number Floor Puzzle'), ('Smyths Toys', 5.0, 'https://www.google.com/url?url=https://www.smythstoys.com/uk/en-gb/toys/products/ravensburger-peppa-pig-4-in-a-box-jigsaw-puzzle/p/164273%3Futm_source%3Dgoogle%26utm_medium%3Dorganic%26utm_campaign%3Dsurfaces_across_google&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQ_uQECIYJ&usg=AOvVaw3nkXizWejPrfiO-k-T0gD_', 'Ravensburger Peppa Pig 4 in a Box (12, 16, 20, 24 piece) Jigsaw Puzzles')]]]
best_items = best_items + added_items_for_test