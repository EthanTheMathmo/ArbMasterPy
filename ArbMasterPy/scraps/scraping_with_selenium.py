from http import cookiejar
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options




opts = Options()
opts.add_argument("--headless")
# assert opts.headless  # Operating in headless mode
browser = Firefox(options=opts)
browser.get('https://duckduckgo.com')

search_form = browser.find_element_by_id('search_form_input_homepage')
search_form.send_keys('real python')
search_form.submit()

# html_source = browser.page_source

# print(html_source)