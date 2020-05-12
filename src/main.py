import json
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent # Will keep real user agents database updated


class Url():
    def __init__(self, web_config):
        self.page_multiplier = 0
        self.web_config = web_config
        self.url = ""

    def get_url(self):
        return self.url

    def set_url(self, category_id):
        base_url = self.web_config['base_url']
        params = ""
        for k, v in self.web_config['params'].items():
            params+="&"
            params+=k
            if k == 'categoryId=':
                params+=str(category_id)
            elif k == 'beginIndex=':
                params+=str(self.get_page_multiplier())
            else:
                params+=str(v)

        self.url = base_url + params

    def set_page_multiplier(self, multiplier=0):
        self.page_multiplier = multiplier

    def get_page_multiplier(self):
        return self.page_multiplier

class Website():

    def __init__(self):
        pass
        # self.web_config = web_config
        # self.page_multiplier = 0
    @staticmethod
    def get_source_code(url):
        
        try:
            user_agent = UserAgent(cache=False)
            
        except FakeUserAgentError:
            print("""ERROR - Unable to create fake user agent, it will default to
            'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'""")
            logger.critical("""Unable to create fake user agent, it will default to
            'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'""")
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'
        
        
        for counter in range(0,10):
            headers = {"User-Agent": user_agent.random,
                    "referer": url}
            data = requests.get(url, headers=headers) 
            if data.status_code == 403 and not isinstance(user_agent, str):
                
                print(f"Attempt #{counter} Access forbiden with this headers {headers}")
                # logger.warning(f"Attempt #{counter} Access forbiden with this headers {headers}")
                
            elif data.status_code != 200:
                # logger.critical(f"Error code {data.status_code}")
                # raise ResponseException(data.status_code)
                break
            
            # elif url != data.url:
            #     break
            # else:
            #     return BeautifulSoup(data.content, 'html.parser')
            #     break

        return BeautifulSoup(data.content, 'html.parser')
    
    def get_data(self, source, category):
        total = []
        container = source.find_all("li", {"class": "gridItem"})
        for cont in container:
            try:
                producto = {}
                product_info = cont.find("div", {"class": "productNameAndPromotions"})
                url = product_info.find("a")['href']
                title = product_info.a.text.strip()
                price_container = cont.find("div", {"class":"pricing"})
                price_unit = price_container.p.text.strip()
                producto['category'] = category
                producto['title'] = title
                producto['price_unit'] = price_unit
                producto['url'] = url
                # print(f"URL {url}")
                print(f"TItle {title}")
                print(f"PRice {price_unit}")
                if url.startswith("//cat"):
                    break
                else:
                    total.append(producto)
            except Exception as ex:
                print("ERROR -- " + str(ex))
        return total



def main():
    with open('config/sainbury.json', 'r') as fp:
        web_config = json.load(fp)
    url = Url(web_config)
    web = Website()

    total_products = []

    for category, value in web_config['categories'].items():
        for v in range(0,10):
            try:
                url.set_page_multiplier(v * web_config['page_multiplier'])
                url.set_url(str(value))
                full_link = url.get_url()
                multiplier = url.get_page_multiplier() + web_config['page_multiplier']
                url.set_page_multiplier(multiplier)
                print(f"Extracting data for this category {category}")
                print(full_link)
                source = Website.get_source_code(full_link)
                products = web.get_data(source, category)
                total_products.append(products)
            except Exception as ex:
                print('ERROR - ' + str(ex))

    with open('productos.json', 'w') as fp:
        json.dump(total_products, fp)

if __name__ == "__main__":
    main()