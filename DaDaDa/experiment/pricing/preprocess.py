import argparse
from sklearn.decomposition import PCA
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import re
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def get_config(config_choice):
    if config_choice == 'middle_layer':
        return 'embedding/xlm-r-large_12_embeddings.csv', 223, 'price_12.csv'
    elif config_choice == 'last_layer':
        return 'embedding/xlm-r-large_24_embeddings.csv', 55, 'price_24.csv'
    else:
        raise ValueError(f"Unknown config choice: {config_choice}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose a configuration for the task.")
    parser.add_argument('--config', type=str, required=True, choices=['middle_layer', 'last_layer'],
                        help="Configuration choice: 'middle_layer' or 'last_layer'")

    args = parser.parse_args()

    embedding_file, n_components, final_file = get_config(args.config)

    embedding_df = pd.read_csv(embedding_file)

    df = pd.read_csv('../../data/final_data.csv')
    # merge two df which have same 'title' and 'platform'
    embedding_df.drop(columns=['title', 'platform'], inplace=True)
    word_embeddings = embedding_df.to_numpy()
    scaler = MinMaxScaler()
    word_embeddings_standardized = scaler.fit_transform(embedding_df)
    pca = PCA(n_components=n_components)
    word_embeddings_pca = pca.fit_transform(word_embeddings_standardized)

    # transfer word_embeddings_pca to df
    df2 = pd.DataFrame(word_embeddings_pca)

    # concate two df
    df = pd.concat([df, df2], axis=1)
    print(df.shape)

    df = df.drop(columns=['url', 'platform', 'provider','title', 'description', 'data_sample'])
    # drop pricing_mode = 'negotiation' and 'free'
    df = df[df['price_mode'] != 'negotiation']
    df = df[df['price_mode'] != 'free']
    # drop price = 0
    df = df[df['price'] != 0]

    # transfer some column to one-hot
    df = pd.get_dummies(df, columns=['category', 'update_frequency', 'price_mode'])

    # use /(?<=\S),(?=\S)/g to split the string
    pattern = re.compile(r'(?<=\S),(?=\S)')
    df['coverage'] = df['coverage'].apply(lambda x: pattern.split(x))

    mlb = MultiLabelBinarizer()
    one_hot_encoded = mlb.fit_transform(df['coverage'])
    one_hot_df = pd.DataFrame(one_hot_encoded, columns=mlb.classes_)

    # standardize numerical columns
    scaler = MinMaxScaler()
    columns = ['dimension', 'size', 'volume']
    df[columns] = scaler.fit_transform(df[columns])

    # log transform price
    df['price_log'] = np.log(df['price'] + 1)
    df.drop(columns=['price'], inplace=True)
    df.drop(columns=['coverage'], inplace=True)
    print(df.shape)
    print(one_hot_df.shape)
    # merge by columns
    df_one_hot = pd.concat([df.reset_index(drop=True), one_hot_df], axis=1)

    df_one_hot.to_csv(final_file, index = False)
    print(df_one_hot.shape)

