import argparse
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import pandas as pd

def get_config(config_choice):
    if config_choice == 'config1':
        return 'xlm-r-large_12_embeddings.csv', 223
    elif config_choice == 'config2':
        return 'xlm-r-large_24_embeddings.csv', 55
    else:
        raise ValueError(f"Unknown config choice: {config_choice}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose a configuration for the task.")
    parser.add_argument('--config', type=str, required=True, choices=['middle_layer', 'last_layer'],
                        help="Configuration choice: 'middle_layer' or 'last_layer'")

    args = parser.parse_args()

    embedding_file, n_components = get_config(args.config)

    df = pd.read_csv(embedding_file)
    word_embeddings = df.drop(columns=['platform', 'title'])
    print(word_embeddings.shape)
    # 查看哪一行有nan值
    print(word_embeddings.isnull().any(axis=1))

    word_embeddings = word_embeddings.to_numpy()


    #
    scaler = StandardScaler()
    word_embeddings_standardized = scaler.fit_transform(word_embeddings)

    # compute PCA for all principal components
    pca = PCA()
    pca.fit(word_embeddings_standardized)

    # cumulative explained variance ratio
    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)

    # plot cumulative explained variance ratio
    plt.figure(figsize=(8, 6))
    plt.plot(cumulative_variance, marker='o')
    plt.xlabel('Number of Principal Components')
    plt.ylabel('Cumulative Explained Variance Ratio')
    plt.title('PCA Cumulative Explained Variance')
    plt.grid(True)
    plt.axhline(y=0.95, color='r', linestyle='--')  # 95%的阈值线
    plt.show()

    # find the minimum number of principal components needed to achieve 95% explained variance ratio
    num_components = np.argmax(cumulative_variance >= 0.95) + 1
    print(f"Number of components to explain 95% of variance: {num_components}")