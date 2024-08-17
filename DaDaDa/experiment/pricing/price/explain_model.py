import argparse
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neighbors import KNeighborsRegressor
import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
import os
import shap
from sklearn.model_selection import KFold
def get_args(file_choice, seed):
    if file_choice == 'price_12':
        # best hyperparameters for each model using 12th layer embedding
        models = {
            'KNeighbors': KNeighborsRegressor(n_neighbors=5, metric='euclidean', weights='distance'),
            'RandomForest': RandomForestRegressor(bootstrap=True, max_depth=None, min_samples_leaf=2,
                                                  min_samples_split=2, n_estimators=300),
            'GradientBoosting': GradientBoostingRegressor(learning_rate=0.05, max_depth=5, min_samples_leaf=4,
                                                          min_samples_split=2, n_estimators=300,
                                                          subsample=0.8, random_state=seed),
            'XGBoost': xgb.XGBRegressor(learning_rate=0.1, max_depth=7, n_estimators=300, subsample=1.0,
                                        colsample_bytree=0.8, random_state=seed),
        }
        return '../price_12.csv', 'saved_models_12', models
    elif file_choice == 'price_24':
        # best hyperparameters for each model using 24th layer embedding
        models = {
            'KNeighbors': KNeighborsRegressor(n_neighbors=3, metric = 'euclidean', weights='distance'),
            'RandomForest': RandomForestRegressor(bootstrap = True, max_depth = None, min_samples_leaf = 1, min_samples_split = 2, n_estimators = 300),
            'GradientBoosting': GradientBoostingRegressor(learning_rate = 0.05, max_depth = 5, min_samples_leaf = 1, min_samples_split = 5, n_estimators = 300,
                                      subsample = 0.8, random_state=seed),
            'XGBoost': xgb.XGBRegressor(learning_rate = 0.1, max_depth = 7, n_estimators = 300, subsample = 1.0, colsample_bytree = 0.8, random_state=seed),
        }
        return '../price_24.csv', 'saved_models_24', models
    else:
        raise ValueError(f"Unknown file choice: {file_choice}")

if __name__ == '__main__':
    seed = 42

    parser = argparse.ArgumentParser(description="Choose a file to read.")
    parser.add_argument('--file', type=str, required=True, choices=['price_12', 'price_24'],
                        help="File choice: 'price_12' or 'price_24'")
    parser.add_argument('--mode', type=str, required=True, choices=['train', 'test'],
                        help="Mode choice: 'train' or 'test'")
    args = parser.parse_args()

    mode = args.mode
    file_path, save_path, models = get_args(args.file, seed)
    df = pd.read_csv(file_path)

    # Split the data into training and testing sets
    X = df.drop(columns=['price_log'])
    y = df['price_log']

    results = {}
    os.makedirs(save_path, exist_ok=True)

    # K-Fold cross-validation
    kf = KFold(n_splits=5, shuffle=True, random_state=seed)

    for model_name, model in models.items():

        fold = 1 # used to mark the fold number

        for train_index, test_index in kf.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            # if model_name != 'XGBoost':
            #     continue
            model = pickle.load(open(f'{save_path}/{model_name}_fold{fold}.pkl', 'rb'))
            if model_name == 'KNeighbors':
                continue
                explainer = shap.KernelExplainer(model, X_train)
            else:
                explainer = shap.TreeExplainer(model, X_train)
            shap_values = explainer.shap_values(X_test)
            # compute the mean shapley values of different feature
            shap_values = np.mean(np.abs(shap_values), axis=0)
            print(shap_values)
            # shap.summary_plot(shap_values, X_test, feature_names=X.columns, show=True)
            break;




