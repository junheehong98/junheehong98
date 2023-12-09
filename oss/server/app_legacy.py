from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_squared_error

app = Flask(__name__)

# 날짜와 match_id 매핑
match_ids = {
    "2023-08-13": 4193457,
    "2023-08-20": 4193477,
    "2023-08-26": 4193480,
    "2023-09-02": 4193493,
    "2023-09-16": 4193507,
    "2023-09-24": 4193510,
    "2023-10-01": 4193527,
    "2023-10-07": 4193536,
    "2023-10-24": 4193549,
    "2023-10-28": 4193555,
    "2023-11-07": 4193569,
    "2023-11-11": 4193579,
    "2023-11-26": 4193660
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    date = request.json['date']
    match_id = match_ids.get(date)
    if match_id:
        prediction_results = run_prediction(match_id)
        return jsonify(prediction_results)
    else:
        return jsonify({"error": "No match found for selected date"})

def run_prediction(match_id):
    # 데이터 처리 및 예측 수행
    file_path = './tottenham_matches.csv'
    data = pd.read_csv(file_path)
    data = data_processing(data, match_id)
    predictions = perform_prediction(data)
    return format_predictions(predictions, data)

def data_processing(data, match_id):
    # 해당 match_id에 대한 데이터 필터링
    data = data[data['matchId'] == match_id]

    # 불필요한 피쳐 제거
    data = data.drop(["matchId", "subbedOutTime", "position", "fantasyScore", "subbedInTime"], axis=1)

    # 피쳐 이름 변경
    rename_columns = {
        'accurate_passes': 'accurate_passes_rate(%)',
        # 나머지 컬럼 이름 변경
    }
    data = data.rename(columns=rename_columns)

    # 포지션 널값 처리
    null_positions = data[data['positionStringShort'].isna()]
    for index, row in null_positions.iterrows():
        name = row['name']
        most_frequent_position = data[data['name'] == name]['positionStringShort'].mode()[0]
        data.at[index, 'positionStringShort'] = most_frequent_position

    # 데이터 나누기
    player_names = data['name'].tolist()
    positions = data['positionStringShort'].tolist()
    data = data.drop(["name", "positionStringShort", "positionRow"], axis=1)

    # rating 널값 제거
    data = data.dropna(subset=["rating"])
    data_x = data.drop("rating", axis=1)
    data_y = data["rating"]

    # 데이터 스케일링 및 인코딩
    train_feature_order = ['isCaptain', 'minutesPlayed', 'isGoalkeeper', 'goal', 'assist', 'yellowCard', 'redCard',
                           'total_shots', 'accurate_passes_rate(%)',
                           'chances_created', 'expected_goals(xG)', 'expected_goals_on_target(xGOT)',
                           'expected_assists(xA)', 'xG+xA', 'shot_accuracy(%)', 'blocked_shots',
                           'touches', 'touches_in_opposition_box', 'passes_into_final_third', 'long_balls_accuracy(%)',
                           'dispossessed', 'xG_Non_penalty', 'tackles_won_rate(%)',
                           'clearances', 'headed_clearance', 'defensive_actions', 'recoveries', 'dribbled_past',
                           'duels_won', 'duels_lost', 'ground_duels_won_rate(%)',
                           'aerial_duels_won_rate(%)', 'was_fouled', 'fouls_commited', 'dribble_success_rate(%)',
                           'penalties_won', 'big_chances_missed',
                           'crosses_success_rate(%)', 'x0_AM', 'x0_CB', 'x0_CM', 'x0_DM', 'x0_GK', 'x0_LB', 'x0_LM',
                           'x0_LW', 'x0_RB',
                           'x0_RM', 'x0_RW', 'x0_ST', 'x1_0', 'x1_1', 'x1_2', 'x1_3', 'x1_4', 'x1_5']

    # 'positionStringShort'와 'positionRow' 열 선택
    data_x_cat = data_x[['positionStringShort', 'positionRow']].values
    # OneHotEncoder 객체 생성
    cat_encoder = OneHotEncoder()
    # 원-핫 인코딩 적용
    data_x_cat_1hot = cat_encoder.fit_transform(data_x_cat)

    data_x_cat_1hot_df = pd.DataFrame(data_x_cat_1hot.toarray(), columns=cat_encoder.get_feature_names_out())

    # 누락된 범주형 특성 추가
    missing_cat_features = ['x0_AM', 'x0_CB', 'x0_CM', 'x0_DM', 'x0_GK', 'x0_LB', 'x0_LM', 'x0_LW', 'x0_RB', 'x0_RM',
                            'x0_RW', 'x0_ST', 'x1_0',
                            'x1_1', 'x1_2', 'x1_3', 'x1_4', 'x1_5']

    for feature in missing_cat_features:

        if feature not in data_x_cat_1hot_df.columns:
            data_x_cat_1hot_df[feature] = 0  # 누락된 특성에 0 값 추가

    # positionStringShort, positionRow은 카테고리컬
    data_x_num = data_x.drop(["positionStringShort", "positionRow"], axis=1)

    # 불리언 타입이 아닌 수치형 데이터만 선택
    numeric_features = data_x_num.select_dtypes(include=['int64', 'float64'])
    # StandardScaler 객체 생성
    scaler = StandardScaler()
    # 수치형 데이터에 표준화 적용
    numeric_features_scaled = scaler.fit_transform(numeric_features)
    # 스케일링된 데이터를 데이터프레임으로 변환 (원본 데이터프레임의 인덱스 사용)
    numeric_features_scaled_df = pd.DataFrame(numeric_features_scaled, columns=numeric_features.columns,
                                              index=data_x_num.index)
    # 데이터를 소수점 셋째 자리에서 반올림
    numeric_features_scaled_df = numeric_features_scaled_df.round(3)
    # 스케일링된 수치형 데이터프레임을 원본 데이터프레임과 병합
    data_num_scaled = data_x_num.copy()
    data_num_scaled[numeric_features.columns] = numeric_features_scaled_df
    #
    # # 원-핫 인코딩된 데이터를 데이터프레임으로 변환
    # data_x_cat_1hot_df = pd.DataFrame(data_x_cat_1hot.toarray(), columns=cat_encoder.get_feature_names_out(),
    #                                    index=data_x.index)

    # 불리언 타입의 데이터만 선택
    bool_features = data_x_num.select_dtypes(include=['bool'])

    # 인덱스 재설정
    # 데이터가 11개인데 병합하면 자꾸 22개가 되어 추가했다
    data_num_scaled.reset_index(drop=True, inplace=True)
    bool_features.reset_index(drop=True, inplace=True)
    data_x_cat_1hot_df.reset_index(drop=True, inplace=True)

    # 스케일링된 수치형 데이터, 불리언 타입의 데이터, 원-핫 인코딩된 데이터 병합
    data_x_prepared = pd.concat([data_num_scaled, bool_features, data_x_cat_1hot_df], axis=1)

    # Make sure the prediction data has the same feature order
    data_x_prepared = data_x_prepared[train_feature_order]

    return data_x_prepared, data_y, player_names, positions

def perform_prediction(data):
    # 예측 모델 로드 및 예측 수행
    # 예시:
    # model = pickle.load(open('model.pkl', 'rb'))
    # predictions = model.predict(data_x)
    # return predictions
    # 모델 로드 및 예측 수행 로직 (위 코드 참조)
    # ...
    # 모델 불러오기 및 예측 수행
    model_names = ['tree_reg', 'voting_regressor', 'gbrt', 'sgd_reg', 'rnd_for', 'svm_reg']
    predictions = {}
    best_model = None
    lowest_rmse = float('inf')
    model_rmses = {}  # 모델별 RMSE 저장

    for model_name in model_names:
        with open(f'./{model_name}.pkl', 'rb') as file:
            model = pickle.load(file)
            model_predictions = model.predict(data_x)
            predictions[model_name] = model_predictions

            # 각 모델의 RMSE 계산
            rmse = np.sqrt(mean_squared_error(data_y, model_predictions))
            model_rmses[model_name] = rmse  # RMSE 저장
            if rmse < lowest_rmse:
                lowest_rmse = rmse
                best_model = model_name

    best_predictions = predictions[best_model]
    return best_predictions, model_rmses  # 예측 결과와 RMSE 반환

def format_predictions(predictions, data):
    results = {}
    for position in data['positionStringShort'].unique():
        results[position] = []
        position_data = data[data['positionStringShort'] == position]
        for idx, row in position_data.iterrows():
            result = {
                "name": row['name'],
                "actual": row['rating'],
                "predicted": predictions[idx]
            }
            results[position].append(result)
    return results

if __name__ == '__main__':
    app.run(debug=True)
