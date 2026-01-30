import argparse
from matplotlib import pyplot as plt
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
            'KNeighbors': KNeighborsRegressor(n_neighbors=3, metric='euclidean', weights='distance'),
            'RandomForest': RandomForestRegressor(bootstrap=True, max_depth=None, min_samples_leaf=1,
                                                  min_samples_split=2, n_estimators=300),
            'GradientBoosting': GradientBoostingRegressor(learning_rate=0.05, max_depth=5, min_samples_leaf=1,
                                                          min_samples_split=5, n_estimators=300,
                                                          subsample=0.8, random_state=seed),
            'XGBoost': xgb.XGBRegressor(learning_rate=0.1, max_depth=7, n_estimators=300, subsample=1.0,
                                        colsample_bytree=0.8, random_state=seed),
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
    parser.add_argument('--by', type=str, required=False, choices=['all', 'category'],
                        help="Analyse by: 'all' or 'category", default='all')
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

    n_embedding = 55 if args.file == 'price_24' else 223
    category_names = ['Automotive Data', 'Environmental Data', 'Financial Services Data', 'Gaming Data',
                      'Healthcare and Life Sciences Data', 'Manufacturing Data', 'Media and Entertainment Data',
                      'Other', 'Public Sector Data', 'Resources Data', 'Telecommunications Data', 'Retail, Location and Marketing Data']
    frequency_names = ['daily', 'hourly', 'irregular', 'minutely', 'monthly', 'no-update', 'on-demand', 'quarterly',
                       'real-time', 'secondly', 'weekly', 'yearly']
    price_mode = ['usage-based', 'one-off', 'subscription']
    country_names = ['Afghanistan', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla',
                     'Antarctica', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria',
                     'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize',
                     'Benin', 'Bermuda', 'Bhutan', "Bolivia, Plurinational State of",
                     "Bonaire, Sint Eustatius and Saba", 'Bosnia and Herzegovina', 'Botswana', 'Bouvet Island',
                     'Brazil', 'British Indian Ocean Territory', 'Brunei Darussalam', 'Bulgaria', 'Burkina Faso',
                     'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Cayman Islands',
                     'Central African Republic', 'Chad', 'Chile', 'China', 'Christmas Island',
                     'Cocos (Keeling) Islands', 'Colombia', 'Comoros', 'Congo', "Congo, The Democratic Republic of the",
                     'Cook Islands', 'Costa Rica', 'Croatia', 'Cuba', 'Curaçao', 'Cyprus', 'Czechia', "Côte d'Ivoire",
                     'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador',
                     'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Falkland Islands (Malvinas)',
                     'Faroe Islands', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia',
                     'French Southern Territories', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar',
                     'Greece', 'Greenland', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea',
                     'Guinea-Bissau', 'Guyana', 'Haiti', 'Heard Island and McDonald Islands',
                     'Holy See (Vatican City State)', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India',
                     'Indonesia', "Iran, Islamic Republic of", 'Iraq', 'Ireland', 'Isle of Man', 'Israel', 'Italy',
                     'Jamaica', 'Japan', 'Jersey', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati',
                     "Korea, Democratic People\'s Republic of", "Korea, Republic of", 'Kuwait', 'Kyrgyzstan',
                     "Lao People's Democratic Republic", 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya',
                     'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macao', 'Madagascar', 'Malawi', 'Malaysia',
                     'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius',
                     'Mayotte', 'Mexico', "Micronesia, Federated States of", "Moldova, Republic of", 'Monaco',
                     'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru',
                     'Nepal', 'Netherlands', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue',
                     'Norfolk Island', 'North Macedonia', 'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan',
                     'Palau', "Palestine, State of", 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines',
                     'Pitcairn', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Romania', 'Russian Federation',
                     'Rwanda', 'Réunion', 'Saint Barthélemy', "Saint Helena, Ascension and Tristan da Cunha",
                     'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Martin (French part)',
                     'Saint Pierre and Miquelon', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino',
                     'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone',
                     'Singapore', 'Sint Maarten (Dutch part)', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia',
                     'South Africa', 'South Georgia and the South Sandwich Islands', 'South Sudan', 'Spain',
                     'Sri Lanka', 'Sudan', 'Suriname', 'Svalbard and Jan Mayen', 'Sweden', 'Switzerland',
                     'Syrian Arab Republic', "Taiwan, Province of China", 'Tajikistan', "Tanzania, United Republic of",
                     'Thailand', 'Timor-Leste', 'Togo', 'Tokelau', 'Tonga', 'Trinidad and Tobago', 'Tunisia',
                     'Turkmenistan', 'Turks and Caicos Islands', 'Tuvalu', 'Türkiye', 'Uganda', 'Ukraine',
                     'United Arab Emirates', 'United Kingdom', 'United States', 'United States Minor Outlying Islands',
                     'Uruguay', 'Uzbekistan', 'Vanuatu', "Venezuela, Bolivarian Republic of", 'Viet Nam',
                     "Virgin Islands, British", "Virgin Islands, U.S.", 'Wallis and Futuna', 'Western Sahara', 'Yemen',
                     'Zambia', 'Zimbabwe', 'Åland Islands']
    category_list = ["category_{}".format(cname) for cname in category_names]
    feature_groups = {
        'size': ['size'],
        'dimension': ['dimension'],
        'volume': ['volume'],
        'description': ['{}'.format(i) for i in range(n_embedding)],
        'category': category_list,
        'update_frequency': ['update_frequency_{}'.format(name) for name in frequency_names],
        'price_mode': ['price_mode_{}'.format(mode) for mode in price_mode],
        'coverage': [cname for cname in country_names]
    }
    if args.by == 'category':
        category = 'category_Retail, Location and Marketing Data'
        X = df[df[category] == 1].drop(columns=['price_log'])
        y = df[df[category] == 1]["price_log"]
        feature_groups.pop('category')



    for mode in price_mode:
        shap_result = []
        for model_name, model in models.items():
            fold = 1  # used to mark the fold number
            cur_mode = f"price_mode_{mode}"
            cur_X = X[X[cur_mode] == 1]
            cur_Y = y[X[cur_mode] == 1]
            for train_index, test_index in kf.split(cur_X):
                print(mode)
                X_train, X_test = cur_X.iloc[train_index], cur_X.iloc[test_index]
                y_train, y_test = cur_Y.iloc[train_index], cur_Y.iloc[test_index]

                run = '{0}_fold_{1}_{2}'.format(model_name, fold, args.by)

                model = pickle.load(open(f'{save_path}/{model_name}_fold{fold}.pkl', 'rb'))
                print("Calculating SHAP for {0}, run {1}".format(model_name, run))
                if model_name == 'KNeighbors':
                    continue
                else:
                    explainer = shap.TreeExplainer(model, X_train)

                shap_values = explainer.shap_values(X_test)

                # test group shap value:
                group_shap_values = {}
                run_res = {}
                print("SHAP for {}".format(model_name))
                for group_name, features in feature_groups.items():
                    idx = [X_test.columns.get_loc(f) for f in features]
                    group_value = np.sum(shap_values[:, idx], axis=1)
                    value_abs_mean = np.mean(np.abs(group_value))
                    run_res[group_name] = value_abs_mean
                    print("{0} : {1}".format(group_name, value_abs_mean))
                    group_shap_values[group_name] = group_value

                group_shap_df = pd.DataFrame(group_shap_values)
                run_res["run"] = run
                shap_result.append(run_res)
                fold += 1

        result_df = pd.DataFrame(shap_result)
        result_df.to_csv(
            os.path.join('./', "feature_importance_{0}_{1}.csv".format(args.by, mode)),
            index=False)




