try:
    from EasyWebdriver import Chrome
except ImportError:
    from selenium.webdriver import Chrome
from selenium.common.exceptions import StaleElementReferenceException
    
import time, requests, re
from path import Path as path

ALL_DONE = 1
SOME_DONE = 0
NO_DONE = -1

def download_image(imgurl, dest):
    res = requests.get(imgurl)
    res.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in res.iter_content(100000):
            f.write(chunk)

class Search:
    
    def __init__(self, terms, browser = None, imgtype = "photos", safesearch = True, delay = 0.5, downloads = None):
        if not browser:
            browser = Chrome()
        self.terms = terms
        if not downloads:
            downloads = "downloads/"
        path(downloads).mkdir_p()
        self.dest_folder = "downloads/{}".format(terms)
        path(self.dest_folder).mkdir_p()
        self.downloads = downloads
        self.load_database()
        self.baseurl = "https://pixabay.com/{}/search/{}/?&order=latest".format(imgtype, terms)
        self.imgtype = imgtype
        self.delay_time = delay
        browser.get(self.baseurl)
        tmp = browser.find_element_by_css_selector("span[class='total--2-kq8 hideMd--482UI']").\
                         get_attribute("innerHTML").replace("/ ","")
        self.pages = int(re.sub("[^0-9]", "", tmp))
        if safesearch:
            browser.find_element_by_css_selector("input[type='checkbox']").click()
        self.code_cache = [None]*(self.pages + 1)
        self.cur_page = 1
        self.browser = browser
        
    def add_item(self, item):
        if item not in self.database:
            self.database.add(item)
        
    def delay(self):
        time.sleep(self.delay_time)
        
    def download_all(self, smart = True, max_images = float('inf')):
        if smart:
            page = self.smart_find_start()
        else:
            page = self.pages
        downloaded = 0
        while (page > 0) & (downloaded < max_images):
            self.go_page(page)
            links = self.get_image_links()
            for link in links:
                if self.download_image(link):
                    downloaded += 1
            page -= 1
      
    def download_image(self, url):
        if not self.link_in_db(url):
            cur_url = self.browser.current_url
            self.delay()
            self.browser.get(url)
            img_tags = self.browser.find_elements_by_tag_name('img')
            for it in img_tags:
                for bit in it.get_attribute('srcset').split(" "):
                    if bit.endswith("_1280.jpg"):
                        img_id = self.get_image_id(url)
                        dest = "{}/{}.jpg".format(self.dest_folder, img_id)
                        self.add_item(img_id)
                        download_image(bit, dest)
            self.browser.get(cur_url)
            return True
        else:
            return False

    def get_image_links(self):
        try:
            elems = self.browser.find_elements_by_css_selector("a[class='link--h3bPW']")
            return [elem.get_attribute("href") for elem in elems]
        except StaleElementReferenceException:
            self.delay()
            return self.get_image_links()
    
    def get_image_id(self, url):
        chunks = url.split("/")
        i = -1
        if len(chunks[-1]) == 0:
            i = -2
        return chunks[i]
    
    def go_page(self, page):
        self.delay()
        newurl = "{}&pagi={}&".format(self.baseurl, page)
        self.browser.get(newurl)
        self.cur_page = page
    
    def link_in_db(self, url):
        if self.get_image_id(url) in self.database:
            return True
        return False
        
    def load_database(self):
        files = path(self.dest_folder).files()
        fnamebases = [f.namebase for f in files]
        self.database = set(fnamebases)
        
    def page_done_code(self, page = None):
        if page is not None:
            cached = self.code_cache[page]
            if cached is not None:
                return cached
            self.go_page(page)
        links = self.get_image_links()
        in_db = set()
        for link in links:
            if self.link_in_db(link):
                in_db.add(True)
            else:
                in_db.add(False)
        if True in in_db:
            if False in in_db:
                self.code_cache[self.page] = SOME_DONE
                return SOME_DONE
            else:
                self.code_cache[self.page] = ALL_DONE
                return ALL_DONE
        else:
            self.code_cache[self.page] = NO_DONE
            return NO_DONE

    def smart_find_start(self, start = 1, end = None):
        if not end:
            end = self.pages
        if self.page_done_code(end) != ALL_DONE:
            return end
        if self.page_done_code(start) != NO_DONE:
            return start
        if start == end - 1:
            return end
        else:
            midpoint = int(round((start + end)/2))
            midcode = self.page_done_code(midpoint)
            if midcode == SOME_DONE:
                return midpoint
            elif midcode == NO_DONE:
                return self.smart_find_start(midpoint, end)
            else:
                return self.smart_find_start(start, midpoint)
                