from flask import Flask, request, jsonify
import pickle
import os

import pickle

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDRegressor, LinearRegression
from sklearn.model_selection import RandomizedSearchCV, cross_val_score
from scipy.stats import uniform, randint
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.svm import LinearSVR, SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor


data = pd.read_csv('modified_data7.csv', encoding='cp1252')

# 필요없는 피처 날리기
data = data.drop("subbedOutTime", axis=1)
data = data.drop("position", axis=1)
data = data.drop("fantasyScore", axis=1)

# 포지션만 있고 세부 포지션 널값처리
# 'positionStringShort'의 널값이 있는 행 찾기
null_positions = data[data['positionStringShort'].isna()]

# 각 널값에 대해 처리
for index, row in null_positions.iterrows():
    # 현재 널값이 있는 행의 'name' 가져오기
    name = row['name']
    # 해당 'name'을 가진 모든 행에서 'positionStringShort'의 최빈값 찾기
    most_frequent_position = data[data['name'] == name]['positionStringShort'].mode()[0]
    # 널값 채우기
    data.at[index, 'positionStringShort'] = most_frequent_position

data = data.drop("name", axis=1)
# rating 널값 제거, 개수가 매우적어 없는거만 제거
data = data.dropna(subset=["rating"])

# x , y 나누기
data_x = data.drop("rating", axis=1)
data_y = data["rating"]

# 학습, 테스트 데이터 나누기
x_train, x_test, y_train, y_test = train_test_split(data_x, data_y, test_size=0.2)

# 'positionStringShort'와 'positionRow' 열 선택
x_train_cat = x_train[['positionStringShort', 'positionRow']].values
# OneHotEncoder 객체 생성
cat_encoder = OneHotEncoder()
# 원-핫 인코딩 적용
x_train_cat_1hot = cat_encoder.fit_transform(x_train_cat)
# positionStringShort, positionRow은 카테고리컬
x_train_num = x_train.drop(["positionStringShort", "positionRow"], axis=1)

# 불리언 타입이 아닌 수치형 데이터만 선택
numeric_features = x_train_num.select_dtypes(include=['int64', 'float64'])
# StandardScaler 객체 생성
scaler = StandardScaler()
# 수치형 데이터에 표준화 적용
numeric_features_scaled = scaler.fit_transform(numeric_features)
# 스케일링된 데이터를 데이터프레임으로 변환 (원본 데이터프레임의 인덱스 사용)
numeric_features_scaled_df = pd.DataFrame(numeric_features_scaled, columns=numeric_features.columns,
                                          index=x_train_num.index)
# 데이터를 소수점 셋째 자리에서 반올림
numeric_features_scaled_df = numeric_features_scaled_df.round(3)
# 스케일링된 수치형 데이터프레임을 원본 데이터프레임과 병합
data_num_scaled = x_train_num.copy()
data_num_scaled[numeric_features.columns] = numeric_features_scaled_df

# 원-핫 인코딩된 데이터를 데이터프레임으로 변환
x_train_cat_1hot_df = pd.DataFrame(x_train_cat_1hot.toarray(), columns=cat_encoder.get_feature_names_out(),
                                   index=x_train.index)

# 불리언 타입의 데이터만 선택
bool_features = x_train_num.select_dtypes(include=['bool'])


# 스케일링된 수치형 데이터, 불리언 타입의 데이터, 원-핫 인코딩된 데이터 병합
x_train_prepared = pd.concat([data_num_scaled, bool_features, x_train_cat_1hot_df], axis=1)

x_test, y_test

# x_test, y_test


# 'positionStringShort'와 'positionRow' 열 선택
x_test_cat = x_test[['positionStringShort', 'positionRow']].values
# OneHotEncoder 객체 생성
cat_encoder2 = OneHotEncoder()
# 원-핫 인코딩 적용
x_test_cat_1hot = cat_encoder2.fit_transform(x_test_cat)

# positionStringShort, positionRow은 카테고리컬
x_test_num = x_test.drop(["positionStringShort", "positionRow"], axis=1)

# 불리언 타입이 아닌 수치형 데이터만 선택
numeric_features2 = x_test_num.select_dtypes(include=['int64', 'float64'])
# StandardScaler 객체 생성
scaler2 = StandardScaler()
# 수치형 데이터에 표준화 적용
numeric_features_scaled2 = scaler.transform(numeric_features2)
# 스케일링된 데이터를 데이터프레임으로 변환 (원본 데이터프레임의 인덱스 사용)
numeric_features_scaled_df2 = pd.DataFrame(numeric_features_scaled2, columns=numeric_features2.columns,
                                          index=x_test_num.index)
# 데이터를 소수점 셋째 자리에서 반올림
numeric_features_scaled_df2 = numeric_features_scaled_df2.round(3)
# 스케일링된 수치형 데이터프레임을 원본 데이터프레임과 병합
data_num_scaled2 = x_test_num.copy()
data_num_scaled2[numeric_features2.columns] = numeric_features_scaled_df2

# 원-핫 인코딩된 데이터를 데이터프레임으로 변환
x_test_cat_1hot_df = pd.DataFrame(x_test_cat_1hot.toarray(), columns=cat_encoder2.get_feature_names_out(),
                                   index=x_test.index)

# 불리언 타입의 데이터만 선택
bool_features2 = x_test_num.select_dtypes(include=['bool'])


# 스케일링된 수치형 데이터, 불리언 타입의 데이터, 원-핫 인코딩된 데이터 병합
x_test_prepared = pd.concat([data_num_scaled2, bool_features2, x_test_cat_1hot_df], axis=1)
# 'positionStringShort'와 'positionRow' 열 선택
x_test_cat = x_test[['positionStringShort', 'positionRow']].values
# OneHotEncoder 객체 생성
cat_encoder2 = OneHotEncoder()
# 원-핫 인코딩 적용
x_test_cat_1hot = cat_encoder2.fit_transform(x_test_cat)

# positionStringShort, positionRow은 카테고리컬
x_test_num = x_test.drop(["positionStringShort", "positionRow"], axis=1)

# 불리언 타입이 아닌 수치형 데이터만 선택
numeric_features2 = x_test_num.select_dtypes(include=['int64', 'float64'])
# StandardScaler 객체 생성
scaler2 = StandardScaler()
# 수치형 데이터에 표준화 적용
numeric_features_scaled2 = scaler.transform(numeric_features2)
# 스케일링된 데이터를 데이터프레임으로 변환 (원본 데이터프레임의 인덱스 사용)
numeric_features_scaled_df2 = pd.DataFrame(numeric_features_scaled2, columns=numeric_features2.columns,
                                          index=x_test_num.index)
# 데이터를 소수점 셋째 자리에서 반올림
numeric_features_scaled_df2 = numeric_features_scaled_df2.round(3)
# 스케일링된 수치형 데이터프레임을 원본 데이터프레임과 병합
data_num_scaled2 = x_test_num.copy()
data_num_scaled2[numeric_features2.columns] = numeric_features_scaled_df2

# 원-핫 인코딩된 데이터를 데이터프레임으로 변환
x_test_cat_1hot_df = pd.DataFrame(x_test_cat_1hot.toarray(), columns=cat_encoder2.get_feature_names_out(),
                                   index=x_test.index)

# 불리언 타입의 데이터만 선택
bool_features2 = x_test_num.select_dtypes(include=['bool'])


# 스케일링된 수치형 데이터, 불리언 타입의 데이터, 원-핫 인코딩된 데이터 병합
x_test_prepared = pd.concat([data_num_scaled2, bool_features2, x_test_cat_1hot_df], axis=1)



# 모델 불러오기 및 예측 수행
model_names = ['tree_reg', 'voting_regressor', 'gbrt', 'sgd_reg', 'rnd_for', 'svm_reg']
predictions = {}


for model_name in model_names:
    with open(f'{model_name}.pkl', 'rb') as file:
        model = pickle.load(file)
        predictions[model_name] = model.predict(x_test_prepared)

# 각 모델의 RMSE 계산
for model_name, prediction in predictions.items():
    rmse = np.sqrt(mean_squared_error(y_test, prediction))
    print(f"Model: {model_name}, RMSE: {rmse}")