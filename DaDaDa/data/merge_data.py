import pandas as pd
import glob
import pycountry

def get_country_name(country_code_list):
    # split by ,
    country_code = country_code_list.split(",")
    country_list = []
    for i in range(len(country_code)):
        country = pycountry.countries.get(alpha_2=country_code[i])
        country_list.append(country.name)

    return ','.join(country_list)

def process_currency_price(row):
    if row['currency'] == 'RMB':
        return row['price'] / 7.075
    elif row['currency'] == 'EUR':
        return row['price'] / 0.924
    elif row['currency'] == 'GBP':
        return row['price'] / 0.804
    elif row['currency'] == 'JPY':
        return row['price'] / 140.511
    else:
        return row['price']

def merge_data():
    # get all the CSV file paths
    #
    file_paths = ['preprocess_data/aws.csv', 'preprocess_data/zhejiang.csv', 'preprocess_data/snowflake.csv', \
                  'preprocess_data/guangzhou.csv', 'preprocess_data/shanghai.csv', 'preprocess_data/beijing.csv', \
                  'preprocess_data/datarade.csv', 'preprocess_data/databricks.csv', 'preprocess_data/guiyang.csv']

    # read all CSV files into a list of DataFrames
    dfs = [pd.read_csv(file) for file in file_paths]

    # show the column names of each DataFrame (for debugging)
    for i, df in enumerate(dfs):
        # print(dfs[i])
        print(f"DataFrame {i} columns: {df.columns.tolist()}")

    # merge by column name using pandas.concat, ignoring column order
    combined_df = pd.concat(dfs, ignore_index=True, sort=True)

    # change the coverage 2 letter code to country name
    combined_df['coverage'] = combined_df['coverage'].apply(get_country_name)

    # rmb 7.075, eur 0.924,  gbp 0.804, jpy 140.511
    # change the currency to USD
    combined_df['price'] = combined_df.apply(process_currency_price, axis=1)
    combined_df.drop(columns=['currency', 'category'], inplace=True)

    combined_df.rename(columns={'category_aws': 'category'}, inplace=True)

    # substitue the category & to and
    combined_df['category'] = combined_df['category'].str.replace('&', 'and')

    # if data_sample is none, set to 'N/A'
    combined_df['data_sample'].fillna('N/A', inplace=True)

    combined_df.to_csv('final_data.csv', index=False)

if __name__ == '__main__':
    merge_data()
