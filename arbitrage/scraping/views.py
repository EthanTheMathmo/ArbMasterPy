from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout


# Create your views here.


def summary(request):
    if not request.user.is_authenticated:
        return render(request, "scraping/login.html")
    return render(request, "scraping/summary.html", {
        "best_items": best_items,
        "blacklist": blacklist
    })

def index(request):
    # If no user is signed in, return to login page:
    if not request.user.is_authenticated:
        return render(request, "scraping/login.html")
    return render(request, "scraping/index.html")

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

            blacklist.append(site)

            return render(request, "scraping/summary.html", {
                "best_items": best_items,
                "blacklist": blacklist
            })

        else:

            return render(request, "scraping/add_to_blacklist.html", {
                "form": form
            })

    return render(request, "scraping/add_to_blacklist.html", {
        "form": NewSiteForm()
    })

blacklist = ["ebay.com", "etsy.com", "alibaba.com", "idealo.com", "onbuy.com"]

class NewSiteForm(forms.Form):
    site = forms.CharField(label="site")

#So, we actually want to use the code, returning two things, some summary html and the html lines
#This means basically return best_items

best_items = [[' Thomas & Friends 4 in Box (12, 16, 20, 24 Piece) Jigsaw Puzzles for Kids Age 3 Years and Up', 3.02, [('Poundshop.com', 1.09, 'https://www.google.com/url?url=https://www.poundshop.com/princess-palace-45-piece-puzzle.html&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECNIM&usg=AOvVaw3iQHIJeVD3UuvspaQoaU4Q', 'Grafix Princess Palace Puzzle'), ('Wish', 1.95, 'https://www.google.com/url?url=https://www.wish.com/c/5f18eba2cdebcc1eb01074c0%3Fhide_login_modal%3Dtrue%26from_ad%3Dgoog_shopping_organic%26_display_country_code%3DGB%26_force_currency_code%3DGBP%26pid%3Dgoogleadwords_int%26c%3D%257BcampaignId%257D%26ad_cid%3D5f18eba2cdebcc1eb01074c0%26ad_cc%3DGB%26ad_curr%3DGBP%26ad_price%3D2.00&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QgOUECKML&usg=AOvVaw0pNMfl8NXdwfp3i8pfmEgS', 'Early Educational Toy Developing for Children Jigsaw Digital Number 1-16 Animal ...'), ('Plaza Japan', 3.49, 'https://www.google.com/url?url=https://www.plazajapan.com/4905096251229/%3FsetCurrencyId%3D1&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECPIK&usg=AOvVaw0f8khdaeyRNNBZvlQLbSDe', 'Apollo-sha 25-122 Jigsaw Puzzle Thomas & Friends Collection of Characters (85 ...'), ('Plaza Japan', 3.49, 'https://www.google.com/url?url=https://www.plazajapan.com/4905096251236/%3FsetCurrencyId%3D1&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECIcM&usg=AOvVaw3PYOmHgeIFFJYo9g7aP6Zg', 'Apollo-sha 25-123 Jigsaw Puzzle Thomas & Friends Collection of Characters (63 ...'), ('Early Learning Centre', 5.0, 'https://www.google.com/url?url=https://www.elc.co.uk/games-jigsaws/jigsaws/jigsaw-0-49/Ravensburger-My-First-Jigsaw-Puzzle---Thomas-%2526-Friends/p/547679%3Futm_source%3Dgoogle%26utm_medium%3Dorganic%26utm_campaign%3Dorganicshopping&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjTtNrP3JD0AhW9lmoFHQdpAe8QguUECJcI&usg=AOvVaw0ki0wrM1MuVcx19iLArN5U', 'Thomas & Friends My First Jigsaw Puzzles')]], ['Ravensburger Peppa Pig London Red Bus 24 Piece Giant Shaped Floor Jigsaw Puzzle for Kids Age 3 Years Up - Educational Toys for Toddlers', 4.73, [('Wish', 1.95, 'https://www.google.com/url?url=https://www.wish.com/c/5f18eba2cdebcc1eb01074c0%3Fhide_login_modal%3Dtrue%26from_ad%3Dgoog_shopping_organic%26_display_country_code%3DGB%26_force_currency_code%3DGBP%26pid%3Dgoogleadwords_int%26c%3D%257BcampaignId%257D%26ad_cid%3D5f18eba2cdebcc1eb01074c0%26ad_cc%3DGB%26ad_curr%3DGBP%26ad_price%3D2.00&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQgOUECN4L&usg=AOvVaw0frbXB3UPL2oATENRqGNg-', 'Early Educational Toy Developing for Children Jigsaw Digital Number 1-16 Animal ...'), ('The Range', 3.49, 'https://www.google.com/url?url=https://www.therange.co.uk/toys/cards-puzzles-and-board-games/children-s-puzzles/30-piece-peppa-pig-puzzle%23322009&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQgOUECJkL&usg=AOvVaw2w6QTTb7h7rjtXimF4qgY0', 'Trefl - 30 Piece Peppa Pig Puzzle'), ('MyTrendyPhone.co.uk', 4.6, 'https://www.google.com/url?url=https://www.mytrendyphone.co.uk/shop/9-piece-jigsaw-puzzle-kids-educational-toy-269541p.html&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQguUECLUM&usg=AOvVaw1mGICjtZBSisIU1h7TfnXy', '9-Piece Jigsaw Puzzle for Kids / Educational Toy - School Bus'), ('Fab Finds', 4.99, 'https://www.google.com/url?url=https://fabfinds.co.uk/products/cbeebies-giant-number-floor-puzzle-30-pieces&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQguUECNML&usg=AOvVaw1e5WtJHbKdtMK9XvU6PWQE', 'Cbeebies - Giant Number Floor Puzzle'), ('Smyths Toys', 5.0, 'https://www.google.com/url?url=https://www.smythstoys.com/uk/en-gb/toys/products/ravensburger-peppa-pig-4-in-a-box-jigsaw-puzzle/p/164273%3Futm_source%3Dgoogle%26utm_medium%3Dorganic%26utm_campaign%3Dsurfaces_across_google&rct=j&q=&esrc=s&sa=U&ved=0ahUKEwjwq8_R3JD0AhW9kWoFHZ99CcwQ_uQECIYJ&usg=AOvVaw3nkXizWejPrfiO-k-T0gD_', 'Ravensburger Peppa Pig 4 in a Box (12, 16, 20, 24 piece) Jigsaw Puzzles')]]]
