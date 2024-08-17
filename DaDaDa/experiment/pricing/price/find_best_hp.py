from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
import pandas as pd
from sklearn.model_selection import GridSearchCV
import xgboost as xgb
import argparse

seed = 42

def find_best_rf(X_train, X_test, y_train, y_test):
    rf_param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'bootstrap': [True, False]
    }

    rf = RandomForestRegressor()
    rf_grid_search = GridSearchCV(estimator=rf, param_grid=rf_param_grid, cv=5, n_jobs=-1, verbose=2,
                                  scoring='neg_mean_squared_error')
    rf_grid_search.fit(X_train, y_train)

    print("Best parameters found: ", rf_grid_search.best_params_)
    print("Best cross-validation score: ", rf_grid_search.best_score_)

    best_rf_model = rf_grid_search.best_estimator_
    print("Test set prediction score: ", best_rf_model.score(X_test, y_test))

def find_best_gb(X_train, X_test, y_train, y_test):
    gb_param_grid = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.1, 0.05],
        'max_depth': [3, 4, 5],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'subsample': [0.8, 1.0]
    }

    gb = GradientBoostingRegressor()

    gb_grid_search = GridSearchCV(estimator=gb, param_grid=gb_param_grid, cv=5, n_jobs=-1, verbose=2,
                                  scoring='neg_mean_squared_error')
    gb_grid_search.fit(X_train, y_train)

    print("Best parameters found: ", gb_grid_search.best_params_)
    print("Best cross-validation score: ", gb_grid_search.best_score_)

    best_gb_model = gb_grid_search.best_estimator_
    print("Test set prediction score: ", best_gb_model.score(X_test, y_test))

def find_best_kn(X_train, X_test, y_train, y_test):
    knn_param_grid = {
        'n_neighbors': [3, 5, 7, 10],
        'weights': ['uniform', 'distance'],
        'metric': ['euclidean', 'manhattan', 'minkowski']
    }

    knn = KNeighborsRegressor()

    knn_grid_search = GridSearchCV(estimator=knn, param_grid=knn_param_grid, cv=5, n_jobs=-1, verbose=2,
                                   scoring='neg_mean_squared_error')
    knn_grid_search.fit(X_train, y_train)

    print("Best parameters found: ", knn_grid_search.best_params_)
    print("Best cross-validation score: ", knn_grid_search.best_score_)

    best_knn_model = knn_grid_search.best_estimator_
    print("Test set prediction score: ", best_knn_model.score(X_test, y_test))

def find_best_xg(X_train, X_test, y_train, y_test):
    param_grid = {
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'n_estimators': [100, 200, 300],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0]
    }

    xgb_model = xgb.XGBRegressor(random_state=seed)

    grid_search = GridSearchCV(estimator=xgb_model, param_grid=param_grid, cv=5, scoring='neg_mean_squared_error',
                               n_jobs=-1, verbose=2)
    grid_search.fit(X_train, y_train)

    print("Best parameters found: ", grid_search.best_params_)
    print("Best cross-validation score: ", grid_search.best_score_)

    best_xgb_model = grid_search.best_estimator_
    print("Test set prediction score: ", best_xgb_model.score(X_test, y_test))

def get_file_path(file_choice):
    if file_choice == 'price_12':
        return '../price_12.csv'
    elif file_choice == 'price_24':
        return '../price_24.csv'
    else:
        raise ValueError(f"Unknown file choice: {file_choice}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose a file to read.")
    parser.add_argument('--file', type=str, required=True, choices=['price_12', 'price_24'],
                        help="File choice: 'price_12' or 'price_24'")

    args = parser.parse_args()

    file_path = get_file_path(args.file)

    df = pd.read_csv(file_path)
    X = df.drop(columns=['price_log'])
    y = df['price_log']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)

    find_best_rf(X_train, X_test, y_train, y_test)

    find_best_gb(X_train, X_test, y_train, y_test)

    find_best_kn(X_train, X_test, y_train, y_test)

    find_best_xg(X_train, X_test, y_train, y_test)