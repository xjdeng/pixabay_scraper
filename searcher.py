try:
    from EasyWebdriver import Chrome
except ImportError:
    from selenium.webdriver import Chrome
    
import time

class Search:
    
    def __init__(self, terms, browser = None, imgtype = "photos", safesearch = True, delay = 0.5):
        if not browser:
            browser = Chrome()
        self.baseurl = "https://pixabay.com/{}/search/{}/?&order=latest".format(imgtype, terms)
        self.imgtype = imgtype
        self.delay = delay
        browser.get(self.baseurl)
        self.pages = int(browser.find_element_by_css_selector("span[class='total--2-kq8 hideMd--482UI']").\
                         get_attribute("innerHTML").replace("/ ",""))
        if safesearch:
            browser.find_element_by_css_selector("input[type='checkbox']").click()
        self.browser = browser
        
    def delay(self):
        time.sleep(self.delay())
        
    def get_image_links(self):
        return self.browser.find_elements_by_css_selector("a[class='link--h3bPW']")
    
    def go_page(self, page):
        newurl = "{}&pagi={}&".format(self.baseurl, page)
        self.browser.get(newurl)