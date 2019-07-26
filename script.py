from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
from time import sleep
from urllib.request import Request
from urllib.request import urlopen
#from fake_useragent import UserAgent

def get_html(url):
    html_content = ''
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_page = urlopen(req).read()
        html_content = BeautifulSoup(html_page, "html.parser")
    except Exception as e: 
        print(e)
        pass

    return html_content

def get_page_items(url):

    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('#content table tr'):
            if item.select('.searchimg'):
                items.append(item)
    except:
        pass

    try:
        next_items = html.select('p span a')
        for next_item in next_items:
            next_item_text = next_item.get_text().strip()
            if 'Next' in next_item_text:
                next_url = 'https://www.cherrystonestamps.com/' + next_item.get('href')
                break
    except:
        pass

    shuffle(items)

    return items, next_url

def get_categories():
    
    url = 'https://www.cherrystonestamps.com/'
    
    items = []
    try:
        html = get_html(url)
        category_cont = html.select('#sidebar ul')[0]
        category_items = category_cont.select('li ul li a')
        for category_item in category_items:
            parent_cat = category_item.parent.find('a').get_text().strip()
            item_url = category_item.get('href')
            if parent_cat != 'Literature/Catalogues' and item_url != '#':
                items.append(item_url)
    except: 
        pass

    return items

def get_details(html):

    stamp = {}
    
    try:
        td1 = html.select('td')[1]
        td2 = html.select('td')[2]
        td3 = html.select('td')[3]
    except:
        return stamp

    try:
        price = td3.select('.larger strong')[0].get_text()
        price = price.replace(",", "").strip()
        price = price.replace("$", "").strip()
        stamp['price'] = price
    except:
        stamp['price'] = None
        
    try:
        title = td1.select('strong')[0].get_text().strip()
        stamp['title'] = title
    except:
        stamp['title'] = None
        
    try:
        cat_temp = td2.get_text().strip()
        cat_parts = cat_temp.split('Cat. Val. ')
        cat_value = cat_parts[1].strip()
        scott_num = cat_parts[0].strip()
        stamp['scott_num'] = scott_num.replace('Cat.', '').strip()
        stamp['cat_value'] = cat_value
    except:
        stamp['scott_num'] = None 
        stamp['cat_value'] = None

    try:
        country = td1.select(".larger strong a")[0].get_text()
        stamp['country'] = country
    except:
        stamp['country'] = None
        
    try:
        if td1.select('strong'):
            raw_text_parts = td1.decode().split('</strong>')
            raw_text_html = raw_text_parts[-1]
            raw_text = BeautifulSoup(raw_text_html, "html.parser").get_text()
            stamp['raw_text'] = raw_text
    except: 
        stamp['raw_text'] = None
        
    stamp['currency'] = 'USD'
    
    # image_urls should be a list
    images = []
    try:
        image_items = html.select('.searchimg a')
        for image_item in image_items:
            img_href = image_item.get('href')
            if img_href != '#':
                img = 'https://www.cherrystonestamps.com' + img_href
                if img not in images:
                    images.append(img)
    except:
        pass

    stamp['image_urls'] = images

    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    print(stamp)
    print('+++++++++++++')
    #sleep(randint(25, 65))
    return stamp

# loop through all categories
categories = get_categories()
print(categories)
for category in categories:
    while(category):
        page_items, category = get_page_items(category)
        # loop through all items on current page
        for page_item in page_items:
            stamp = get_details(page_item)
