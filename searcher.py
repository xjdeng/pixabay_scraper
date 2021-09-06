try:
    from EasyWebdriver import Chrome
except ImportError:
    from selenium.webdriver import Chrome
    
import time, requests

def download_image(imgurl, dest):
    res = requests.get(imgurl)
    res.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in res.iter_content(100000):
            f.write(chunk)

class Search:
    
    def __init__(self, terms, browser = None, imgtype = "photos", safesearch = True, delay = 0.5):
        if not browser:
            browser = Chrome()
        self.terms = terms
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
        elems = self.browser.find_elements_by_css_selector("a[class='link--h3bPW']")
        return [elem.get_attribute("href") for elem in elems]
    
    def go_page(self, page):
        newurl = "{}&pagi={}&".format(self.baseurl, page)
        self.browser.get(newurl)