import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import datetime
import math

def one_hot_enc(feature_name, unique_vals):
    return tf.feature_column.indicator_column(tf.feature_column.categorical_column_with_vocabulary_list(feature_name, unique_vals))


def get_timestamp(date):
    if "-" in date:
        return datetime.datetime.strptime(date + "-01", "%Y-%m-%d").timestamp()
    else:
        return datetime.datetime.strptime(date + "01", "%Y%m%d").timestamp()


def f1_score(prec, rec):
    return (2 * prec * rec)/(prec + rec)


def load_prep_data(file_name):


    type_dict = {'loan_amnt': np.float64,
                 'state': 'str',
                 # 'annual_inc': np.int,
                 'int_rate': np.float64,
                 'delinquent': np.int,
                 'disbursal_date': 'str',
                 'credit_score': np.float64
                 }

    df = pd.read_csv(file_name, header=0, delimiter=",", dtype=type_dict)
    print("df:")
    print(df.head(n=5))

    # drop records that contain NaN
    df.dropna(inplace=True)
    print("df after dropna:")
    print(df.head(n=5))

    # get the training and testing out of the data
    df = df.sample(frac=1, replace=False)

    # create new column representing converted dates into timestamps
    new_col = df["disbursal_date"].apply(get_timestamp)
    print("new_col info:")
    print(new_col)
    df.insert(df.shape[1], "disbursal_timestamp", new_col, False)

    # remove old disbursal_date column
    df.pop('disbursal_date')

    print("df after removing disbursal date:")
    print(df.head(n=5))

    # separate into train and test
    num_rows = df.shape[0]
    train_num_rows = math.floor(num_rows * 0.5)
    df_train_X = df.iloc[:train_num_rows, :]
    df_test_X = df.iloc[train_num_rows:, :]

    # separate into two dataframes each, i.e. X, y
    df_train_y = df_train_X.pop('delinquent')
    df_test_y = df_test_X.pop('delinquent')

    # list of categorical (as opposed to continuous) feature (column) names
    # CATEGORICAL_FEATURES = ['state']
    CONTINUOUS_FEATURES = ['loan_amnt', 'annual_inc', 'int_rate', 'disbursal_timestamp', 'credit_score']
    feature_cols = []
    state_unique_vals = df['state'].unique()
    feature_cols.append(one_hot_enc('state', state_unique_vals))

    for cont_feat in CONTINUOUS_FEATURES:
        feature_cols.append(tf.feature_column.numeric_column(cont_feat, dtype=tf.float32))

    # todo: remove this once done testing
    ##########
    # example = dict(df_train_X.head(1))
    # class_fc = tf.feature_column.indicator_column(tf.feature_column.categorical_column_with_vocabulary_list('state', ('PA', 'WV', 'OH')))
    # print('Feature value: "{}"'.format(example['state'].iloc[0]))
    # print('One-hot encoded: ', tf.keras.layers.DenseFeatures([class_fc])(example).numpy())
    # print("feature_cols:")
    # print(feature_cols)
    # exit()
    ##########

    return df_train_X, df_train_y, df_test_X, df_test_y, feature_cols