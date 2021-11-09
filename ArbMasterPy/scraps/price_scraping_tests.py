from requests_html import HTMLSession

headers=headers = {  # <-- so the Google will treat your script as a "real" user browser.
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
}

import browser_cookie3
cj = browser_cookie3.load()
from bs4 import BeautifulSoup

headers = {  # <-- so the Google will treat your script as a "real" user browser.
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
}

session = HTMLSession()


r = session.get(r"https://sas.selleramp.com/sas/lookup?search_term=https%3A%2F%2Famazon.co.uk%2Fs%3Fi%3Dmerchant-items%26me%3DA3V7JCFX60RIEL%26marketplaceID%3DA1F83G8C2ARO7P")

r.html.render(sleep=10)
print(r.html.html)
r.html.search("Python")

# address1= 'http://python-requests.org/'
# address2 = "https://www.google.com/search?q=minecraft+toys&tbm=shop"
# address3="https://www.google.com/search?q=mathematics"
# r = session.get("https://www.bing.com/shop?q=lego&FORM=SHOPTB", cookies=cj,
# headers=headers)
# r.html.render(sleep=10)
# print(r.html.html)
# print("\n\n\n")
# print(r.html.full_text)