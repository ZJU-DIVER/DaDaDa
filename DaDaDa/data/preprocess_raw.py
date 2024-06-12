import pandas as pd
import re
import pycountry
def remove_special_chars(text):
    # Chinese characters, English uppercase and lowercase letters, digits, and both Chinese and English punctuation marks.
    pattern = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9，。？！：；“”‘’（）()《》、—…/.,:;!\'"`~@#$%^&+=|\\<>?\[\]\{\}_-]+\s')

    text_cleaned = re.sub(pattern, '', str(text))
    return text_cleaned

def convert_wan_to_number(text):
    multiplier = 10000
    if '万元' in text:
        num = re.search(r'(\d+(\.\d+)?)万', text)
        if num:
            base_price = float(num.group(1)) * multiplier
            # remove the '万'
            text = re.sub(r'(\d+(\.\d+)?)万', str(base_price), text)
    return text

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
def classify_price(text):
    # if not null, transfer to string
    if not isinstance(text, str):
        return 'free', 0.0

    text = convert_wan_to_number(text)
    if match := re.search(r'(免费)', str(text)):
        return 'free', 0.0
    elif match := re.search(r'(面议)', str(text)):
        return 'negotiation', 0.0
    elif match := re.search(r'(\d+(\.\d+)?)元\/(\d+)?次', text):
        times = int(match.group(3)) if match.group(3) else 1
        cost_per_time = float(match.group(1)) / times
        return 'usage-based', cost_per_time
    elif match := re.search(r'(\d+(\.\d+)?)元/(天|月|年)', text):
        price = float(match.group(1))
        period = match.group(3)
        if period == '天':
            return 'subscription', price * 365
        elif period == '月':
            return 'subscription', price * 12
        elif period == '年':
            return 'subscription', price
    elif match := re.search(r'(\d+(\.\d+)?)元', text):
        return 'one-off', float(match.group(1))
    elif is_float(text):
        return 'one-off', float(text)
    else:
        return 'free', 0.0

def handle_updatefrequency(text):
    if not isinstance(text, str):
        return 'no-update'
    if '按需更新' in text:
        return 'on-demand'
    if '小时' in text:
        return 'hourly'
    elif '天' in text or '日' in text:
        return 'daily'
    elif '周' in text:
        return 'weekly'
    elif '月' in text:
        return 'monthly'
    elif '季度' in text:
        return 'quarterly'
    elif '年' in text:
        return 'yearly'
    elif '不定期' in text or '不定时' in text:
        return 'irregular'
    elif '实时' in text:
        return 'real-time'
    else:
        return 'no-update'

def process_beijing():
    df = pd.read_csv('raw_data/beijing.csv')
    for column in df.columns:
        if column == 'price' or column == 'url':
            continue
        df[column] = df[column].apply(lambda x: remove_special_chars(x))

    df['price_mode'], df['price'] = zip(*df['price'].apply(classify_price))
    # rename
    df.rename(columns={'company_name': 'provider'}, inplace=True)

    df['coverage'] = 'CN'
    df['volume'] = 0
    df['size'] = 0
    df['update_frequency'] = 'no-update'
    df['platform'] = 'Beijing International Data Exchange'
    df['currency'] = 'RMB'
    df['data_sample'] = None
    # romove some column
    df.drop(columns=['type', 'offer_type', 'detail', 'limit'], inplace=True)
    df.to_csv('preprocess_data/beijing.csv', index=False)

def process_guangzhou():
    df = pd.read_csv('raw_data/guangzhou.csv')
    # change money column to price
    for column in ['outline', 'detail_description']:
        df[column] = df[column].apply(lambda x: remove_special_chars(x))

    df['update_frequency'] = df['update_frequency'].apply(lambda x: handle_updatefrequency(x))
    df.rename(columns={'company_name': 'provider'}, inplace=True)
    df['description'] = df['detail_description']
    df['price_mode'], df['price'] = zip(*df['price'].apply(classify_price))
    df['volume'] = df['size'] = df['dimension'] = 0
    df['coverage'] = 'CN'
    df['platform'] = 'Canton Data Exchange'
    df['currency'] = 'RMB'
    df['url'] = df['cur_url']
    df['data_sample'] = None
    df.drop(columns=['click_time', 'outline', 'application', 'type', 'subdivision_type', 'target_user', 'settlement_interval', 'delivery_type', 'cur_url', 'detail_description'], inplace=True)
    df.to_csv('preprocess_data/guangzhou.csv', index=False)

def handle_shanghai_coverage(text):
    if not isinstance(text, str):
        return 'CN'
    if '全国' in text:
        return 'CN'
    elif '韩国' in text:
        return 'KR'
    elif '全球' in text:
        # return all the country
        country_list = list(pycountry.countries)
        country_list = [country.alpha_2 for country in country_list]
        return ','.join(country_list)
    else:
        return 'CN'
def handle_shanghai_size(text):
    if not isinstance(text, str):
        return 0
    # remove the ','
    text = text.replace(',', '')
    # transfer the size to number, use B
    if 'KB' in text:
        return float(text.replace('KB', '')) * 1024
    elif 'MB' in text:
        return float(text.replace('MB', '')) * 1024 * 1024
    elif 'GB' in text:
        return float(text.replace('GB', '')) * 1024 * 1024 * 1024
    elif 'TB' in text:
        return float(text.replace('TB', '')) * 1024 * 1024 * 1024 * 1024
    elif '待完善' in text:
        return 0
    else:
        return 0

def process_shanghai():
    df = pd.read_csv('raw_data/shanghai.csv')
    for column in ['update_frequency', 'description', 'use_case']:
        df[column] = df[column].apply(lambda x: remove_special_chars(x))

    df['update_frequency'] = df['update_frequency'].apply(lambda x: handle_updatefrequency(x))
    df['coverage'] = df['coverage'].apply(lambda x: handle_shanghai_coverage(x))
    df['platform'] = 'Shanghai Data Exchange'
    df.rename(columns={'company_name': 'provider'}, inplace=True)
    df['currency'] = 'RMB'
    df['price_mode'] = 'negotiation'
    df['price'] = 0
    df['price'] = 0.0
    df['volume'] = 0
    df['size'] = df['storage'].apply(lambda x: handle_shanghai_size(x))
    df['data_sample'] = None
    df = df.drop(columns=['list_time', 'series_name', 'industry', 'data_type', 'product_type', 'keyword', 'use_case', 'storage', 'storage_incr'])
    df.to_csv('preprocess_data/shanghai.csv', index=False)

def process_zhejiang():
    df = pd.read_csv('raw_data/zhejiang.csv')
    for column in ['detail_description', 'price_type', 'api_info']:
        df[column] = df[column].apply(lambda x: remove_special_chars(x))

    df['update_frequency'] = df['update_frequency'].apply(lambda x: handle_updatefrequency(x))
    df['description'] = df['detail_description']
    df['category'] = df['new_category']
    df['size'] = df['data_size'].apply(lambda x: handle_shanghai_size(x))
    df['volume'] = 0
    df['price_mode'], df['price'] = zip(*df['price'].apply(classify_price))
    df['provider'] = ''
    df['coverage'] = 'CN'
    df['currency'] = 'RMB'
    df['dimension'] = 0
    df.rename(columns={'cur_url': 'url'}, inplace=True)
    df['platform'] = 'Zhejiang Big Data Exchange'
    df['data_sample'] = None
    df = df.drop(columns=['data_type', 'click_times', 'detail_description', 'deal_times', 'version', 'product_type', 'new_category', 'management', 'sample_time',
                          'data_size', 'data_form', 'price_type', 'api_info', 'classification'])
    df.to_csv('preprocess_data/zhejiang.csv', index=False)

def process_guiyang():
    df = pd.read_csv('raw_data/guiyang.csv')
    for column in ['description']:
        df[column] = df[column].apply(lambda x: remove_special_chars(x))

    df['category'] = df['new_category']
    df['volume'] = df['size'] = df['dimension'] = 0
    df['update_frequency'] = 'no-update'
    df.rename(columns={'company': 'provider'}, inplace=True)

    df['price_mode'], df['price'] = zip(*df['price'].apply(classify_price))
    df['coverage'] = 'CN'
    df['currency'] = 'RMB'
    df['platform'] = 'Guiyang Global Big Data Exchange'
    df['data_sample'] = None
    df = df.drop(columns=['new_category', 'create_time', 'update_time', 'view_count', 'score', 'deal_time'])
    df.to_csv('preprocess_data/guiyang.csv', index=False)

def process_aws_price(row):
    if row['pricing_type'] == 'Free':
        row['price_mode'] = 'free'
        row['price'] = 0.0
    elif row['subscription_fee'] != 0:
        row['price_mode'] = 'subscription'
        row['price'] = row['subscription_fee'] / row['subscription_period'] * 12
    elif row['pricing_type'] == 'USAGE_BASED':
        row['price_mode'] = 'usage-based'
        row['price'] = row['usage_based_cost']
    else:
        row['price_mode'] = 'free'
        row['price'] = 0
    return row

def process_aws_coverage(text):
    if not isinstance(text, str):
        return 0
    result = []
    for country in pycountry.countries:
        if country.name in text:
            result.append(country.alpha_2)
    # if US not in result,find the U.S.
    if 'US' not in result and 'U.S.' in text:
        result.append('US')

    if len(result) == 0:
        return 'US'
    # turn result to string
    return ','.join(result)

def process_aws():
    df = pd.read_csv('raw_data/aws.csv')

    # drop the item have same title and provider
    df = df.drop_duplicates(subset=['title', 'provider'])

    for column in ['description']:
        df[column] = df[column].apply(lambda x: remove_special_chars(x))

    df = df.apply(process_aws_price, axis = 1)

    # remove the meta_info column
    df.drop(columns=['meta_info'], inplace=True)

    df['category_aws'] = df['category']
    df['find_coverage'] = df['title'] + ' ' + df['description']
    df['coverage'] = df['find_coverage'].apply(lambda x: process_aws_coverage(x))
    df['platform'] = 'AWS Data Exchange'
    df['currency'] = 'USD' # dollar
    df['dimension'] = df['volume'] = df['size'] = 0
    df['update_frequency'] = 'no-update'
    df['data_sample'] = None
    df = df.drop(columns=['pricing_type', 'subscription_fee', 'subscription_period',
                          'usage_based_cost', 'fixed_fee', 'find_coverage'])
    df.to_csv('preprocess_data/aws.csv', index=False)

def process_datarade_update(row):
    if row['real-time'] == 1:
        row['update_frequency'] = 'real-time'
    elif row['secondly'] == 1:
        row['update_frequency'] = 'secondly'
    elif row['minutely'] == 1:
        row['update_frequency'] = 'minutely'
    elif row['hourly'] == 1:
        row['update_frequency'] = 'hourly'
    elif row['daily'] == 1:
        row['update_frequency'] = 'daily'
    elif row['weekly'] == 1:
        row['update_frequency'] = 'weekly'
    elif row['monthly'] == 1:
        row['update_frequency'] = 'monthly'
    elif row['quarterly'] == 1:
        row['update_frequency'] = 'quarterly'
    elif row['yearly'] == 1:
        row['update_frequency'] = 'yearly'
    elif row['on-demand'] == 1:
        row['update_frequency'] = 'on-demand'
    else:
        row['update_frequency'] = 'no-update'
    return row

def process_datarade_coverage(row):
    # column from 42 to 290, if column to true, add the column name to coverage
    coverage = []
    for column in row.index[41:290]:
        if row[column] == 1:
            coverage.append(column)
    if len(coverage) == 0:
        row['coverage'] = 'US'
    else:
        row['coverage'] = ','.join(coverage)
    return row

def process_datarade_price(row):
    if row['subscription_fee'] != 0:
        row['price_mode'] = 'subscription'
        row['price'] = row['subscription_fee'] / row['subscription_period'] * 12
    elif row['usage_based_cost'] != 0:
        row['price_mode'] = 'usage-based'
        row['price'] = row['usage_based_cost']
    elif row['fixed_fee'] != 0:
        row['price_mode'] = 'one-off'
        row['price'] = row['fixed_fee']
    else:
        row['price_mode'] = 'negotiation'
        row['price'] = 0
    return row

def process_datarade():
    df = pd.read_csv('raw_data/datarade.csv')
    # 查看某一列的object
    for column in ['description']:
        df[column] = df[column].apply(lambda x: remove_special_chars(x))
    df = df.apply(process_datarade_coverage, axis=1)
    df = df.apply(process_datarade_update, axis=1)
    df = df.apply(process_datarade_price, axis=1)
    df.rename(columns={'depth': 'dimension'}, inplace=True)
    df['platform'] = 'Datarade'

    # select the column
    df = df[['title', 'provider', 'description', 'price', 'price_mode', 'category',
             'dimension', 'volume', 'size', 'update_frequency',
             'coverage', 'platform', 'currency', 'url', 'category_aws','data_sample']]

    df.to_csv('preprocess_data/datarade.csv', index=False)


def process_snowflake_price(row):
    if row['subscription_fee'] != 0:
        row['price_mode'] = 'subscription'
        row['price'] = row['subscription_fee'] / row['subscription_period'] * 12
    elif row['usage_based_cost'] != 0:
        row['price_mode'] = 'usage-based'
        row['price'] = row['usage_based_cost']
    elif row['fixed_fee'] != 0:
        row['price_mode'] = 'one-off'
        row['price'] = row['fixed_fee']
    else:
        row['price_mode'] = 'free'
        row['price'] = 0
    return row
def process_snowflake():
    df = pd.read_csv('raw_data/snowflake.csv')
    df = df.drop_duplicates(subset=['title', 'provider'])

    for column in ['description']:
        df[column] = df[column].apply(lambda x: remove_special_chars(x))
    # exchange the content of the subscription_period and currency
    df['subscription_period'], df['currency'] = df['currency'], df['subscription_period']

    df = df.apply(process_datarade_coverage, axis = 1)
    df = df.apply(process_datarade_update, axis = 1)
    df = df.apply(process_snowflake_price, axis = 1)

    df['dimension'] = df['size'] = df['volume'] = 0
    df['platform'] = 'Snowflake'
    df['currency'] = 'USD'
    df['data_sample'] = None

    df = df[['title', 'provider', 'description', 'price', 'price_mode', 'category',
             'dimension', 'volume', 'size', 'update_frequency',
             'coverage', 'platform', 'currency', 'url', 'category_aws','data_sample']]
    df.to_csv('preprocess_data/snowflake.csv', index=False)

def process_databricks():
    df = pd.read_csv('raw_data/databricks.csv')
    df = df.drop_duplicates(subset=['title', 'provider'])

    for column in ['description']:
        df[column] = df[column].apply(lambda x: remove_special_chars(x))

    df = df.apply(process_datarade_coverage, axis=1)
    df = df.apply(process_datarade_update, axis=1)

    df['price'] = 0
    # if pricing_type = paid, price_mode = 'negotiation' else free
    df['price_mode'] = df['pricing_type'].apply(lambda x: 'negotiation' if x == 'paid' else 'free')
    df['dimension'] = df['size'] = df['volume'] = 0
    df['platform'] = 'Databricks'
    df['currency'] = 'USD'
    df['data_sample'] = None

    df = df[['title', 'provider', 'description', 'price', 'price_mode', 'category',
             'dimension', 'volume', 'size', 'update_frequency',
             'coverage', 'platform', 'currency', 'url', 'category_aws', 'data_sample']]
    df.to_csv('preprocess_data/databricks.csv', index=False)


if __name__ == '__main__':
    process_beijing()
    process_guangzhou()
    process_shanghai()
    process_zhejiang()
    process_guiyang()
    process_aws()
    process_datarade()
    process_snowflake()
    process_databricks()
