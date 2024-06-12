import argparse
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neighbors import KNeighborsRegressor
import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
import os
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
        r2_scores = []
        mae_scores = []
        mse_scores = []
        std_scores = []

        fold = 1  # used to mark the fold number

        for train_index, test_index in kf.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]

            if mode == 'train':
                model.fit(X_train, y_train)

                y_pred = model.predict(X_test)

                # compute scores
                r2_scores.append(r2_score(y_test, y_pred))
                mae_scores.append(mean_absolute_error(y_test, y_pred))
                mse_scores.append(mean_squared_error(y_test, y_pred))
                std_scores.append(np.std(y_test - y_pred))

                # store the model
                model_filename = f'{save_path}/{model_name}_fold{fold}.pkl'
                with open(model_filename, 'wb') as f:
                    pickle.dump(model, f)
            else:
                model = pickle.load(open(f'{save_path}/{model_name}_fold{fold}.pkl', 'rb'))
                y_pred = model.predict(X_test)
                # compute scores
                r2_scores.append(r2_score(y_test, y_pred))
                mae_scores.append(mean_absolute_error(y_test, y_pred))
                mse_scores.append(mean_squared_error(y_test, y_pred))
                std_scores.append(np.std(y_test - y_pred))

            fold += 1

        print(
            f"{model_name} - Average R2: {np.mean(r2_scores):.4f}, Average MAE: {np.mean(mae_scores):.4f}, Average MSE: {np.mean(mse_scores):.4f}, Average SD: {np.mean(std_scores):.4f}")



