import json

def process_databricks_name(string:str): # Used to generate product url
    cur_pos = 0
    while cur_pos < len(string):
        cur_char = string[cur_pos]
        if cur_char.isalnum():
            cur_pos += 1
        else:
            if cur_char == ' ':
                string = string[:cur_pos] +'-' + string[cur_pos + 1:]
                cur_pos += 1
            else:
                string = string[:cur_pos] + string[cur_pos + 1:]
    return string

def process_result(market): # convert data from .json to .csv
    import csv
    file_path = "./aws.amazon.com_result.json"
    file = open(file_path,'r',encoding='utf-8')
    data = json.load(file)
    results:list[dict] = data['results']
    fieldNames = ['title','url','meta_info','pricing_type','fixed_fee','usage_based_cost','subscription_fee','subscription_period','currency','category','provider','description']
    count=0
    save_file = f'{market}_result.csv'
    with open(save_file,mode='w',newline='',encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file,fieldnames=fieldNames)
        writer.writeheader()
        for prod in results:
            row = generate_row(market,prod)
            writer.writerow(row)
            count+=1
    print(f'{count} entries have been saved to {save_file}.')

    

def generate_row(market,prod:dict):
    row={
        'title':prod['title'],
        'url':prod['url'],
        'meta_info':prod['meta_info'],
        'pricing_type':prod['price_info']['pricing_type'],
    }
    if market=='aws.amazon.com':
        row['fixed_fee'],row['usage_based_cost'],row['subscription_fee'],row['subscription_period'],row['currency'] = handle_aws_pricing(prod['price_info'])
        row['category'] = prod['tags'][0]
        row['provider'] = prod['provider_name']
        row['description'] = prod['description']['description']
    return row

def handle_aws_pricing(price_info:dict[str,str]):
    fix=0
    u_based = 0
    sub = 0
    currency='$'
    sub_period = 0
    if price_info['pricing_type']=='UPFRONT_COMMITMENT':
        for k,v in price_info.items():
            if k=='pricing_type':
                continue
            period = k.split()[0]
            unit = k.split()[1]
            if unit!='month' and unit != 'months':
                print(f'Found different period:{unit}')
            price = extract_price(v)
            curr = v[0]
            sub = price
            currency = curr
            sub_period = period
    elif price_info['pricing_type']=='USAGE_BASED':
        for k,v in price_info.items():
            if k=='pricing_type':
                continue
            if k=='metered_price':
                u_based = extract_price(v.split()[0])
                continue
            period = k.split()[0]
            unit = k.split()[1]
            if unit!='month' and unit != 'months':
                print(f'Found different period:{unit}')
            price = extract_price(v)
            curr = v[0]
            sub = price
            currency = curr
            sub_period = period
    return fix,u_based,sub,sub_period,currency

def extract_price(price_str):
    import re
    return float(re.sub(r'[^\d.]','',price_str))




def get_business_needs():
    file = open('./resources/new_business.html','r',encoding='utf-8') # File contains business needs mappings of snowflake
    from lxml import etree
    
    text = file.read()
    root:etree.ElementBase = etree.HTML(text)
    
    # The following method might become invalid due to website change
    elems:list[etree.ElementBase] = root.xpath('//div[@role=\'option\']')
    buz_map = {}
    for elem in elems:
        id:str = elem.get('id')
        true_id = id.split('3952_')[1]
        name = elem.xpath('./div/div/div/text()')
        buz_map[true_id] = name[0]
    return buz_map

def get_categories():
    import requests
    import os
    category_file_path = './resources/snowflake_category.json' # File contains category mappings of snowflake
    if os.path.exists(category_file_path):
        with open(category_file_path,'r',encoding='utf-8')as rf:
            result = json.load(rf)['result']
    else:
        res = requests.get("https://app.snowflake.com/v0/guest/session/query?sqlText=show%20CATEGORIES%20in%20DATA%20EXCHANGE%20IDENTIFIER(%3F)&bindingsJSON=%5B%22%5C%22SNOWFLAKE_DATA_MARKETPLACE%5C%22%22%5D").content
        with open(category_file_path,'w',encoding='utf-8') as wf:
            json.dump(res,wf,ensure_ascii='false')
        result = json.loads(res)['result']
    cat = {}
    for row in result['rows']:
        cat[row[1]] = row[0]
    return cat

def analyse_datarade_frequency(file_path):
    import json
    with open(file_path,'r',encoding='utf-8') as f:
        prod_list = json.load(f)['results']
        freq_list = [prod['frequency'] for prod in prod_list]
        format_list = [prod['formats'] for prod in prod_list]
        method_list = [prod['delivery_method'] for prod in prod_list]
        freq_result={
            'freq':{},
            'form':{},
            'meth':{}
        }
        for prod in freq_list:
            for freq in prod:
                if freq in freq_result['freq'].keys():
                    freq_result['freq'][freq]+=1
                else:
                    freq_result['freq'][freq]=1
        for prod in format_list:
            for form in prod:
                if form in freq_result['form'].keys():
                    freq_result['form'][form]+=1
                else:
                    freq_result['form'][form]=1
        for prod in method_list:
            for meth in prod:
                if meth in freq_result['meth'].keys():
                    freq_result['meth'][meth]+=1
                else:
                    freq_result['meth'][meth]=1
        import os
        if not os.path.exists('./analyse'):
            os.mkdir('./analyse')
        with open('./analyse/result_freq.json','w',encoding='utf-8') as wf:
            json.dump(freq_result,wf)
        print(freq_result)


def analyse_datarade_meta(file_path): # Analyse the appearences of keys in meta 
    import json
    with open(file_path,'r',encoding='utf-8') as f:
        prod_list = json.load(f)['results']
        meta_list = [prod['meta_info'] for prod in prod_list]
        meta_result={}
        for meta in meta_list:
            for obj in meta:
                key = f'{obj["name"]}' 
                value = obj['value']
                if key in meta_result:
                    if value in meta_result[key]:
                        meta_result[key][f'{value} {obj["label"]}']+=1
                    else:
                        meta_result[key][f'{value} {obj["label"]}']=1
                else:
                    meta_result[key] = {
                        f'{value} {obj["label"]}':1
                    }
        import os
        if not os.path.exists('./analyse'):
            os.mkdir('./analyse')
        with open('./analyse/result_1.json','w',encoding='utf-8') as wf:
            json.dump(meta_result,wf)
        print(meta_result)

def analyse_datarade_pricing(file_path):  # Analyse the appearences of keys in pricing
    import json
    with open(file_path,'r',encoding='utf-8') as f:
        prod_list = json.load(f)['results']
        pricing_list:list[dict] = [prod['price_info'] for prod in prod_list]
        price_result={'starts_at':{}}
        for prod in pricing_list:
            if 'starts_at' in prod.keys():
                value = prod['starts_at']
                if value in price_result['starts_at']:
                    price_result['starts_at'][value] += 1
                else:
                    price_result['starts_at'][value]=1
                continue
            for k,v in prod.items():
                if k=='pricing_type':
                    continue
                if k in price_result.keys():
                    if v in price_result[k].keys():
                        price_result[k][v] += 1
                    else:
                        price_result[k][v] = 1
                else:
                    price_result[k] = {
                        v:1
                    }
        import os
        if not os.path.exists('./analyse'):
            os.mkdir('./analyse')
        with open('./analyse/result_price.json','w',encoding='utf-8',newline='') as wf:
            json.dump(price_result,wf,ensure_ascii=False)
        print(price_result)

def highlight_keywords(text, keywords, color_code='\033[94m'):
    import re
    reset_code = '\033[0m'
    pattern = re.compile('|'.join(re.escape(keyword) for keyword in keywords), re.IGNORECASE)
    highlighted_text = pattern.sub(lambda match: f"{color_code}{match.group(0)}{reset_code}", text)
    
    return highlighted_text

# analyse_datarade_frequency('./datarade.ai_patched.json')
# # process_result('aws.amazon.com')
# r = test_get('https://app.snowflake.com/v0/guest/dx/SNOWFLAKE_DATA_MARKETPLACE/consumerlisting-mc')
