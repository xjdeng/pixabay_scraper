try:
    from EasyWebdriver import Chrome
except ImportError:
    from selenium.webdriver import Chrome

class Search:
    
    def __init__(self, terms, browser = None, safesearch = True):
        if not browser:
            browser = Chrome()
        self.baseurl = "https://pixabay.com/photos/search/{}/?&order=latest".format(terms)
        browser.get(self.baseurl)
        self.pages = int(browser.find_element_by_css_selector("span[class='total--2-kq8 hideMd--482UI']").\
                         get_attribute("innerHTML").replace("/ ",""))
        if safesearch:
            browser.find_element_by_css_selector("input[type='checkbox']").click()
        self.browser = browser
    
    def go_page(self, page):
        newurl = "{}&pagi={}&".format(self.baseurl, page)
        self.browser.get(newurl)