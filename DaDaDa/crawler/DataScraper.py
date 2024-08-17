from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import time
import requests
class DatasetInfo: # Product info
    def __init__(self,title,url,meta_info,price_info,provider,tags,description,category,geo_cover=None,delivery_methods=None,formats=None,frequency=None) -> None:
        self.title = title
        self.url = url
        self.meta_info = meta_info
        self.price_info = price_info
        self.provider_name = provider
        self.tags = tags
        self.category = category
        self.description = description
        self.geo_cover = geo_cover
        self.delivery_methods = delivery_methods
        self.formats = formats
        self.frequency = frequency
        pass

    @classmethod
    def from_databricks(cls,product_info,provider): #product info from databricks
        from util import process_databricks_name
        summary = product_info['summary']
        detail = product_info['detail']
        provider_id = summary['provider_id']
        provider_name = provider[provider_id]
        id = product_info['id']
        category = summary['categories'][0]
        description = f"{summary['subtitle']} {detail['description']}"
        price_info = {'pricing_type':'paid' if summary['listingType'] == 'PERSONALIZED' else 'free'}
        name = summary['name']
        url = 'https://marketplace.databricks.com/details/' + id +'/' + process_databricks_name(provider_name)+'_'+process_databricks_name(name)
        return DatasetInfo(name,url,None,price_info,provider_name,None,description,category)
    
    @classmethod
    def from_aws(cls,title,provider,url,category):# partial product info from aws
        # c = [category]
        return DatasetInfo(title,url,None,None,provider,None,None,category)
    
    @classmethod
    def on_error(cls,url):
        return DatasetInfo(None,url,'Error while fetching this product',None,None,None,None,None)
    
    def to_dict(self): # save as json
        return {
            'title':self.title,
            'url':self.url,
            'meta_info':self.meta_info,
            'price_info':self.price_info,
            'provider_name':self.provider_name,
            'tags':self.tags,
            'description':self.description,
            'geo_cover':self.geo_cover,
            'delivery_method':self.delivery_methods,
            'formats':self.formats,
            'frequency':self.frequency,
            'category':self.category
        }
    
class MarketSite: # Data marketplaces website
    def __init__(self,domain,prod_list,xpath_max,xpath_detail=None,classname_detail=None) -> None:
        self.domain = domain
        self.prod_list_template = prod_list
        self.xpath_max = xpath_max
        self.prod_urls:dict[str,list] = {}
        self.max_page = 0
        self.xpath_datail = xpath_detail
        self.products:list[DatasetInfo] = []
        self.classname_detail = classname_detail
        pass
    
    def prod_urls_to_dict(self):# product urls of different type of pricing plan
        if self.domain == 'aws.amazon.com':
            d = {}
            for k in self.prod_urls.keys():
                d[k] = [x.url for x in self.prod_urls[k]]
            return d
        else:
            return self.prod_urls

    def set_max_page(self,max):
        self.max_page = max

    def add_prod_url(self,urls:dict[str,list]):
        for type,url_list in urls.items():
            if type not in self.prod_urls.keys():
                self.prod_urls[type] = []
            self.prod_urls[type].extend(url_list)
        
    def get_all_detail_xpath(self,category):
        if self.domain == 'datarade.ai':
            return self.xpath_datail[f'{category}-meta'],self.xpath_datail[f'{category}-title'],self.xpath_datail[f'{category}-pricing'],self.xpath_datail[f'{category}-provider'],self.xpath_datail[f'{category}-category']
    
    def get_detail_xpath(self,category,name):
        if category != None:
            if self.domain == 'datarade.ai':
                return self.xpath_datail[f'{category}-{name}']
            if self.domain == 'aws.amazon.com':
                return self.xpath_datail[f'{category}-{name}']
        else:
            return self.xpath_datail[f'{name}']
    
    def get_detail_classname(self,category,name):
        if self.domain=='datarade.ai':
            return self.classname_detail[f'{category}-{name}']
        
    def get_all_detail_classname(self,category):
        if self.domain == 'datarade.ai':
            return self.classname_detail[f'{category}-description_short'],self.classname_detail[f'{category}-description'],self.classname_detail[f'{category}-geo'],self.classname_detail[f'{category}-delivery']
        





# Datarade scarping info, might change over time
datarade = MarketSite('datarade.ai',
                       'https://datarade.ai/search/products?commit=Search&keywords=&page={}&search_type=homepage',
                       '//*[@id="app"]/main/div/div[2]/div/div[3]/div[3]/div/a[7]',
                       xpath_detail={
                           'dataset-meta':'//*[@id="app"]/main/div/div[3]/div/div[2]/div[1]/section[1]',
                           'data_product-meta':'//*[@id="app"]/main/div/div[4]/div/div/div[1]/div',
                           'dataset-title':'//*[@id="app"]/main/div/div[2]/div/div/div[2]/h1',
                           'data_product-title':'//*[@id="app"]/main/div/div[3]/div/div[1]/div/div[2]/h1',
                           'dataset-pricing':'//*[@id="app"]/main/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div/div[1]',
                           'data_product-pricing':'//*[@id="app"]/main/div/div[4]/div/div/div[2]/div/div[1]/div/div/div/table/tbody',
                           'dataset-tags':'//*[@id="app"]/main/div/div[3]/div/div[2]/div[1]/section[5]/div',
                           'data_product-tags':'//*[@id="app"]/main/div/div[4]/div/div/div[1]/section[11]/div/div',
                           'dataset-provider':'//*[@id="app"]/main/div/div[2]/div/div/div[2]/div/a',
                           'data_product-provider':'//*[@id="app"]/main/div/div[3]/div/div[1]/div/div[2]/div/a',
                           'dataset-category':'//*[@id="app"]/main/div/div[1]/div/div/div/a[2]',
                           'data_product-category':'//*[@id="app"]/main/div/div[1]/div/div/div/a[2]',
                           'dataset-description':'//*[@id="app"]/main/div/div[3]/div/div[2]/div[1]/section[3]/div'
                        },
                        classname_detail={
                            'data_product-description_short':'product-content__short-description',
                            'data_product-description':'product-content__description',
                            'data_product-geo':'countries-map',
                            'dataset-geo':'countries-map',
                            'data_product-delivery':'product-content__delivery'
                        }
)
# AWS scarping info, might change over time
aws = MarketSite('aws.amazon.com',
                 'https://aws.amazon.com/marketplace/search/?category={0}&PRICING_MODEL={1}&filters=PRICING_MODEL',
                 '/html/body/div[2]/div[1]/div/div/div/div/div/section/div/div/div[2]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div/div[1]/ul/li[last()]/button',
                 xpath_detail={
                    'UPFRONT_COMMITMENT-pricing':'/html/body/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/span[1]',
                    'USAGE_BASED-pricing':'/html/body/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/span[1]',
                    'USAGE_BASED-metered_cost':'/html/body/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div[2]/div/div/div[3]/div/div[2]/div/div[1]/div/div/div/div[1]',
                    'USAGE_BASED-metered_cost_div':'/html/body/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div[2]/div/div/div[3]',
                    'UPFRONT_COMMITMENT-metered_cost_div':'/html/body/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div[2]/div/div/div[3]',
                    'overview':'/html/body/div[2]/div[1]/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div'
                 })
# Scarping info of Databricks and Snowflake
databricks = MarketSite('marketplace.databricks.com',None,None)
snowflake = MarketSite('app.snowflake.com',None,None)

class DataScraper:
    def __init__(self,website=None,use_file=False) -> None:
        self.website:MarketSite = website # Configure which website to scrape
        
        # Crawler driver setup
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        
        # Timer setup
        self.start_time = time.perf_counter()
        self.last_checkpoint = self.start_time
        
        self.thres_partial_save = 100 # How often a partial result is saved(Number of products fetched)
        self.interval = 2 # Interval between two requests in seconds
        self.offset = 0 # For debug, start fetch from certain page, be aware of the number of products on a page
        
        self.processed_count = 0 # Fetched products
        self.use_urls_from_file = use_file # Use saved products urls instead of fetching new ones(Only for Datarade)
        pass
    
    def run(self):
        if self.website.domain in ['datarade.ai','aws.amazon.com']:
            if not self.use_urls_from_file:
                print("Fetching products from website.")
                self.get_product_urls()
            else:
                file_name = f'{self.website.domain}_urls.json'
                print(f'Loading cached urls from {file_name}')
                with open(file_name,'r') as f:
                    import json
                    self.website.prod_urls = json.load(f)
                ds_len = len(self.website.prod_urls['datasets'])
                dp_len = len(self.website.prod_urls['data_products'])
                to_skip = self.offset*10
                if ds_len<=to_skip:
                    self.website.prod_urls['datasets']=[]
                    to_skip-=ds_len
                    if to_skip>0:
                        self.website.prod_urls['data_products'] = self.website.prod_urls['data_products'][to_skip:]
                else:
                    self.website.prod_urls['datasets'] = self.website.prod_urls['datasets'][to_skip:]
        self.get_website_product_info()
        self.save_result()


    def save_urls(self):# Save fetched product urls
        import json
        with open(f'./{self.website.domain}_urls.json','w',encoding='utf-8') as f:
            json.dump(self.website.prod_urls_to_dict(),f)

    def save_result(self):# Save all result
        import json
        
        with open(f'./{self.website.domain}_result.json','w',encoding='utf-8') as f:
            results = {
                'results' : []
            }
            for i in range(1,self.offset*10,100):
                partial_file_name = f'./results/{self.website.domain}/{i}-{i+99}_result.json'
                with open(partial_file_name,'r',encoding='utf-8') as pf:
                    result = json.load(pf)['results']
                    results['results'].extend(result)
            for prod in self.website.products:
                pd = prod.to_dict()
                results['results'].append(pd)
            json.dump(results,f,ensure_ascii=False)
        print(f'Job done, saving {self.processed_count} products, overall running time: {time.perf_counter()-self.start_time} seconds.')
    
    def save_partial_result(self,start,end,offset=0): # Save partial result
        import os
        if not os.path.exists(f'./results/{self.website.domain}'):
            os.makedirs(f'./results/{self.website.domain}')
        import json
        with open(f'./results/{self.website.domain}/{start+1+offset*10}-{end+offset*10}_result.json','w',encoding='utf-8') as f:
            results = {
                'results' : []
            }
            for prod in self.website.products[start:]:
                pd = prod.to_dict()
                results['results'].append(pd)
            json.dump(results,f,ensure_ascii=False)
        time_now = time.perf_counter()
        print(f"Processed {self.processed_count} products, last 100 products takes {time_now-self.last_checkpoint}")
        self.last_checkpoint = time_now
        

    def should_save_partial(self,offset=0):
        if self.processed_count % self.thres_partial_save == 0:
            self.save_partial_result(self.processed_count-self.thres_partial_save,self.processed_count,offset)
        else:
            return

    def get_page_product_urls(self,category=None): # Get product urls on a page
        
        if self.website.domain == 'datarade.ai':
            urls = {
                'datasets':[],
                'data_products':[]
            }
            
            products = self.driver.find_elements(by=By.XPATH,value='//*[@id="app"]/main/div/div[2]/div/div[3]/div[2]/article')
            
            for p in products:
                # datarade
                prod_type = p.find_element(by=By.XPATH,value='./main/div[2]/div').get_attribute('class')
                if prod_type == 'dataset-card__title':
                    prod_href = p.find_element(by=By.XPATH,value="./main/div[2]/div/a").get_attribute('href')
                    urls['datasets'].append(prod_href)
                else:
                    prod_href = p.find_element(by=By.XPATH,value="./main/div[2]/a").get_attribute('href')
                    urls['data_products'].append(prod_href)
                # print(p,prod_type,prod_href)
        if self.website.domain == 'aws.amazon.com':
            urls = []
            xpath_products = '/html/body/div[2]/div[1]/div/div/div/div/div/section/div/div/div[2]/div/div/div/div[2]/div[1]/table/tbody/tr'
            try:
                products = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH,xpath_products)))
                for p in products:
                    prod = self.get_aws_url(p,category)
                    urls.append(prod)
            except StaleElementReferenceException as e:
                products = self.driver.find_elements(by=By.XPATH,value=xpath_products)
                urls=[]
                for p in products:
                    prod = self.get_aws_url(p,category)
                    urls.append(prod)
            return urls

        self.website.add_prod_url(urls)
        return

    def get_aws_url(self,p:WebElement,category):
        #elem_title = p.find_element(by=By.XPATH,value='./td[2]/div/div[2]/h2/div/a')
        elem_title = p.find_element(by=By.XPATH,value='./td[2]/span/div/div[2]/h2/div/a')
        # '    div/div/div/div[2]/div[1]/table/tbody/tr[1]/td[2]/span/div/div[2]/h2/div/a'
        prod_href = elem_title.get_attribute('href')
        try:
            provider_name = p.find_element(by=By.XPATH,value='./td[2]/span/div/div[2]/small/div/span/a/span').text
        except Exception as e:
            try:
                provider_name = p.find_element(by=By.XPATH,value='./td[2]/span/div/div[2]/small/div/span/span[2]/strong').text
            except:
                provider_name = 'Not provided'
        prod_name = elem_title.text
        prod = DatasetInfo.from_aws(prod_name,provider_name,prod_href,category)
        return prod
    
    def get_product_list_template(self):
        return self.product_list_template[self.domain]

    def get_product_urls(self): # Get all urls from Datarade and AWS
        debug=False
        import time
        if self.website.domain == 'aws.amazon.com':
            amaz_default_cat = 'd5a43d97-558f-4be7-8543-cce265fe6d9d'
            pricing_options = ['UPFRONT_COMMITMENT','FREE','USAGE_BASED']
            # pricing_options = ['FREE','USAGE_BASED']
            for op in pricing_options:
                self.website.prod_urls[op] = []
                self.driver.get(self.website.prod_list_template.format(amaz_default_cat,op))
                time.sleep(self.interval)
                xpath_category = '/html/body/div[2]/div[1]/div/div/div/div/div/section/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/ul/li'
                categories = self.driver.find_elements(by=By.XPATH,value=xpath_category)
                cats = []
                for cat in categories:# get product urls from different catgory under pricing type op
                    name = cat.find_element(by=By.XPATH,value='./a/div/span[1]').text
                    cat_id = eval(cat.find_element(by=By.XPATH,value='./a').get_attribute('data-metric-meta-data'))['ComponentId']
                    cats.append((name,cat_id))
                for cat in cats:
                    self.driver.get(self.website.prod_list_template.format(cat[1],op))
                    is_last = False
                    pages = 1
                    while not is_last:
                        try:
                            prods = self.get_page_product_urls(category=cat[0])
                        except NoSuchElementException as e:
                            print('Encountered NoSuchElementException!')
                            time.sleep(self.interval)
                            prods = self.get_page_product_urls()
                        self.website.prod_urls[op].extend(prods)
                        next_button = self.driver.find_element(by=By.XPATH,value=self.website.xpath_max)
                        is_last = next_button.get_property('disabled')
                        next_button.click()
                        pages += 1
                        time.sleep(1.5*self.interval)
                        if debug:
                            break
                    if debug:
                        break
            self.save_urls()
        else: # datarade.ai
            
            self.driver.get(self.website.prod_list_template.format(1))
            result = self.driver.find_element(by=By.XPATH,value=self.website.xpath_max)
            # print(result.text)
            self.website.set_max_page(eval(result.text))
            template = self.website.prod_list_template
            # offset = 10
            cur_page = 1 + self.offset
            page_limit = 1 if debug else self.website.max_page
            while cur_page <= page_limit:
            # while cur_page <= 25:
                self.driver.get(template.format(cur_page))
                self.get_page_product_urls()
                cur_page += 1
                time.sleep(self.interval)
            self.save_urls()    
            # print(self.website.prod_urls)
        time_now = time.perf_counter()
        count=0
        for k,v in self.website.prod_urls.items():
            count+=len(v)
        print(f'Url fetching done, {count} urls fetched, time elapsed: {time_now-self.start_time} seconds.')
        self.last_checkpoint = time_now
        return 

    def get_product_meta(self,meta_xpath): # Get product metadata for Datarade product
        elem_meta = self.driver.find_element(by=By.XPATH,value=meta_xpath)
        elems_facts = elem_meta.find_elements(by=By.CLASS_NAME,value='dataset__fact')
        facts = []
        for elem_fact in elems_facts:
            fact_item = {
                'name':elem_fact.find_element(by=By.CLASS_NAME,value='dataset__fact-name').text,
                'value':elem_fact.find_element(by=By.CLASS_NAME,value='dataset__fact-value').text,
                'label':elem_fact.find_element(by=By.CLASS_NAME,value='dataset__fact-label').text
            }
            facts.append(fact_item)
        return facts

    def get_product_price(self,category,pricing_plan=None): # Get product pricing info 
        if self.website.domain == 'datarade.ai':
            if category == 'dataset':
                # dataset
                price_xpath = self.website.xpath_datail['dataset-pricing']
                price = self.driver.find_element(by=By.XPATH,value=price_xpath).text
                pricing = {
                    'pricing_type':'paid',
                    'dataset':price
                }
            elif category == 'data_product':
                price_xpath = self.website.xpath_datail['data_product-pricing']
                try:
                    price_plan_table = self.driver.find_element(by=By.XPATH,value=price_xpath)
                    plans = price_plan_table.find_elements(by=By.TAG_NAME,value='tr')
                    pricing = {
                        'pricing_type':'paid',
                    }
                    for plan in plans:
                        plan_name = plan.find_element(by=By.TAG_NAME,value='th').text
                        plan_price = plan.find_element(by=By.TAG_NAME,value='td').text
                        # print(plan_name,' ',plan_price)
                        pricing[plan_name] = plan_price
                except NoSuchElementException as e:
                    pricing = {
                        'pricing_type':'paid',
                        'starts_at':'Pricing available upon request'
                    }
        if self.website.domain == 'app.snowflake.com':
            free_unit = 0
            if 'freeUnits' in pricing_plan.keys():
                free_unit = pricing_plan['freeUnits']
            if category == 'fixed_plus_usage':
                if 'usageUnitPrice' not in pricing_plan.keys():
                    billing_plan = pricing_plan["billingEvents"][0]
                    usage_unit_price = f'{billing_plan["billingQuantity"]} {pricing_plan["currency"]} {billing_plan["billingUnit"]}'
                else:
                    usage_unit_price = f' {pricing_plan["usageUnitPrice"]} {pricing_plan["currency"]} per {pricing_plan["usageUnitKind"]}'
                pricing = {
                    'pricing_type':'fixed_plus_usage',
                    'free_units':f'{free_unit} {pricing_plan["freeUnitKind"]}',
                    'usage_unit_price':usage_unit_price,
                    'base_fee':f'{pricing_plan["baseFee"]} {pricing_plan["currency"]}',
                    'duration':pricing_plan['billingDuration']
                }
            if category == 'fixed':
                pricing = {
                    'pricing_type':'fixed',
                    'base_fee':f'{pricing_plan["baseFee"]} {pricing_plan["currency"]}'
                }
            if category == 'usage_only':
                if 'usageUnitPrice' not in pricing_plan.keys():
                    billing_plan = pricing_plan["billingEvents"][0]
                    usage_unit_price = f'{billing_plan["billingQuantity"]} {pricing_plan["currency"]} {billing_plan["billingUnit"]}'
                else:
                    usage_unit_price = f' {pricing_plan["usageUnitPrice"]} {pricing_plan["currency"]} per {pricing_plan["usageUnitKind"]}'
                pricing = {
                    'pricing_type':'usage_only',
                    'free_units':f'{free_unit} {pricing_plan["freeUnitKind"]}',
                    'usage_unit_price':usage_unit_price,
                }

        return pricing

    def get_datarade_product_info(self,url,category):
        try:
            self.driver.get(url)
            x_facts,x_title,_,x_provider,x_category = self.website.get_all_detail_xpath(category)
            title = self.driver.find_element(by=By.XPATH,value=x_title).text
            p_category = self.driver.find_element(by=By.XPATH,value=x_category).text
            methods = []
            formats = []
            freqs = []
            des =""
            if category=='data_product':
                cname_des_s,cname_des,cname_geo,cname_delivery = self.website.get_all_detail_classname(category)
                try:
                    s_descrip = self.driver.find_element(by=By.CLASS_NAME,value=cname_des_s).text
                except NoSuchElementException as e:
                    s_descrip=""
                try:
                    descrip = self.driver.find_element(by=By.CLASS_NAME,value=cname_des).text
                except NoSuchElementException as e:
                    descrip=""
                des = s_descrip+" "+descrip
                try:
                    delivery = self.driver.find_element(by=By.CLASS_NAME,value=cname_delivery)
                    divs = delivery.find_elements(by=By.XPATH,value='./div')
                    len_ops = len(divs)/2
                    delivery_dict = {}
                    for i in range(len_ops):
                        delivery_dict[divs[i].text] = divs[2*i+1].find_elements(by=By.XPATH,value='./div')
                    for k,v in delivery_dict.items():
                        if k=='Methods':  
                            for method in v:  
                                methods.append(method.find_element(by=By.XPATH,value='./span').text)
                        if k=='Format':  
                            for format in v:  
                                formats.append(format.find_element(by=By.XPATH,value='./span').text)
                        if k=='Frequency':  
                            for freq in v:  
                                freqs.append(freq.find_element(by=By.XPATH,value='./span').text)
                except NoSuchElementException as e:
                    print("No delivery info")
            else:
                # x_des = self.website.get_detail_xpath(category,'description')
                sections = self.driver.find_elements(by=By.XPATH,value='//*[@id="app"]/main/div/div[3]/div/div[2]/div[1]/section')
                for section in sections:
                    try:
                        title = section.find_element(by=By.XPATH,value='./h3').text
                        if title == 'Details':
                            des = section.find_element(by=By.XPATH,value='./div').text
                    except:
                        continue
                cname_geo = self.website.get_detail_classname(category,'geo')
                # des = self.driver.find_element(by=By.XPATH,value=x_des).text
            
            facts = self.get_product_meta(x_facts)
            pricing = self.get_product_price(category=category)
            provider = self.driver.find_element(by=By.XPATH,value=x_provider).text
            tags = self.get_product_tags(category)
            try:
                geo_string = self.driver.find_element(by=By.CLASS_NAME,value=cname_geo).get_attribute('data-selected-regions')
                geo_list = geo_string.split(',')
            except NoSuchElementException as e:
                geo_string = None
            ds = DatasetInfo(title,url,facts,pricing,provider,tags,des,p_category,geo_cover=geo_string,formats=formats,delivery_methods=methods,frequency=freqs)           
        except Exception as e:
            ds = DatasetInfo.on_error(url)
        finally:
            self.website.products.append(ds)


    def get_aws_pricing_info(self,category):    
        prod_pricing = {}
        try:
            import time
            
            time.sleep(self.interval)
            pricing = self.driver.find_elements(by=By.XPATH,value=self.website.get_detail_xpath(category,'pricing'))
            for price in pricing:
                price_text = price.find_element(by=By.XPATH,value='./span/span[2]/span').text
                price_sec = [x.strip() for x in price_text.split('for')]
                prod_pricing[price_sec[1]] = price_sec[0]
                
            try:
                metered_cost_div = self.driver.find_element(by=By.XPATH,value=self.website.get_detail_xpath(category,'metered_cost_div'))
                metered_cost_div.click()
                metered_cost_text = self.driver.find_element(by=By.XPATH,value=self.website.get_detail_xpath(category,'metered_cost')).text
                metered_cost_sec = [x.strip() for x in metered_cost_text.split(' - ')]
                prod_pricing['metered_price'] = f'{metered_cost_sec[1]}({metered_cost_sec[0]})'
            except Exception as e:
                pass
            prod_pricing['pricing_type'] = category
        except Exception as e:
            prod_pricing['pricing_type'] = 'Error while fetching price of this product.'
        return prod_pricing

    def get_aws_product_info(self):
        result = {}
        try:
            des = self.driver.find_element(by=By.XPATH,value=self.website.get_detail_xpath(category=None,name='overview')).text
            result['description'] = des
        except:
            result['description'] = 'Error while fetching.'
        return result

    def get_snowflake_product_info(self,prod_info:dict,prod_id,business_needs_map,categories_map):
        provider = prod_info['profile']['name']
        if 'pricingPlan' in prod_info.keys():
            pricing = self.get_product_price(prod_info['pricingPlan']['type'],prod_info['pricingPlan'])
        else:
            pricing = {'pricing_type':'Free'}
        meta_data:dict = prod_info['metadata']
        title = meta_data['title']
        categories = meta_data['categories'].keys()
        categories_names = [categories_map[x] for x in categories]
        business_needs = []
        if 'businessNeeds' in meta_data.keys():
            business_needs = meta_data['businessNeeds']
        business_needs_names = []
        for need in business_needs:
            if need['type'] == 'standard':
                business_needs_names.append(business_needs_map[need['key']])
            elif need['type'] == 'custom':
                business_needs_names.append(need['name'])
        if 'refresh_rate' in meta_data.keys():
            refresh_rate = meta_data['refresh_rate']
        else:
            refresh_rate = ""
        url = f'https://app.snowflake.com/marketplace/listing/{prod_id}'
        return DatasetInfo(title,url,meta_data,pricing,provider,business_needs,meta_data['subtitle']+" "+meta_data['description'],categories_names[0],frequency=refresh_rate)

    def get_product_tags(self,category):
        if self.website.domain == 'datarade.ai':
            if category == 'dataset':
                classname = 'dataset__categories'           
            elif category == 'data_product':
                classname = 'product-content__categories'
            elem_tag = self.driver.find_element(by=By.CLASS_NAME,value=classname)
            tags = elem_tag.find_elements(by=By.TAG_NAME,value='a')
            tag_names = [tag.text for tag in tags]
        return tag_names
            

    def get_website_product_info(self):
        if self.website.domain == 'datarade.ai':
            # dataset

            datasets = self.website.prod_urls['datasets']
            data_products = self.website.prod_urls['data_products']

            for dataset in datasets:# Get metadata for dataset products
                self.get_datarade_product_info(dataset,'dataset')
                self.processed_count += 1
                self.should_save_partial(self.offset) 
                time.sleep(self.interval)
            for data_product in data_products:# Get metadata for other data products
                self.processed_count += 1
                self.get_datarade_product_info(data_product,'data_product')
                self.should_save_partial(self.offset)
                time.sleep(self.interval)
        if self.website.domain == 'marketplace.databricks.com':
            res = requests.get('https://marketplace.databricks.com/api/2.0/public-marketplace-listings')
            provider_list = requests.get('https://marketplace.databricks.com/api/2.0/public-marketplace-providers').json()['providers']
            provider_map = {}
            for provider in provider_list:
                provider_map[provider['id']] = provider['name']
            prod_list = res.json()['listings']
            for prod in prod_list:
                website_info = DatasetInfo.from_databricks(prod,provider_map)
                self.website.products.append(website_info)
        if self.website.domain == 'app.snowflake.com':
            import json
            from util import get_business_needs,get_categories
            catgories = get_categories()
            business_needs = get_business_needs()
            res = requests.get('https://app.snowflake.com/v0/guest/dx/SNOWFLAKE_DATA_MARKETPLACE/consumerlisting-mc').content
            prods:dict[str,dict] = json.loads(res)['ConsumerListingModel']
            for prod_id,prod in prods.items():
                res = self.get_snowflake_product_info(prod,prod_id,business_needs,catgories)
                self.website.products.append(res)
            return
        if self.website.domain == 'aws.amazon.com':
           
            free:list[DatasetInfo] = self.website.prod_urls['FREE']
            uc:list[DatasetInfo] = self.website.prod_urls['UPFRONT_COMMITMENT']
            ub:list[DatasetInfo] = self.website.prod_urls['USAGE_BASED']
            # free products
            for p in free:
                self.driver.get(p.url)
                p.price_info = {'pricing_type':'Free'}
                p.description = self.get_aws_product_info()
                self.website.products.append(p) 
                self.processed_count += 1
                self.should_save_partial(self.offset)
            # USAGE_BASED
            for p in ub:
                self.driver.get(p.url)
                p.price_info = self.get_aws_pricing_info('USAGE_BASED')
                p.description = self.get_aws_product_info()
                self.website.products.append(p)
                self.processed_count += 1
                self.should_save_partial(self.offset)
            # UPFRONT_COMMITMENT
            for p in uc:
                self.driver.get(p.url)
                p.price_info = self.get_aws_pricing_info('UPFRONT_COMMITMENT')
                p.description = self.get_aws_product_info()
                self.website.products.append(p)
                self.processed_count += 1
                self.should_save_partial(self.offset)
            
            
        return

d = DataScraper(databricks,False)
d.run()