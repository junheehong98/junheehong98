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
    data_x_prepared, data_y, player_names, positions = data_processing(data, match_id)
    predictions, model_rmses = perform_prediction(data_x_prepared, data_y)
    formatted_predictions = format_predictions(predictions, data_y, player_names, positions)

    # formatted_predictions에 model_rmses를 추가하지 않고, 두 데이터를 하나의 딕셔너리로 통합하여 반환
    # 리턴할때 각각 리턴하니 프론트에서 각각 키 값으로 매핑하려 했으나
    # 못해서 여기서 여기서 키값으ㅗ 매핑하니 되었다
    return {
        "predictions": formatted_predictions,
        "model_rmses": model_rmses
    }

    return formatted_predictions
def data_processing(data, match_id):
    # 표준화 위한 훈련데이터 가져오기
    # 훈련데이터 -> 표준화 위해서 로드
    train = pd.read_csv('modified_data7.csv', encoding='cp1252')

    # 필요없는 피처 날리기
    train = train.drop("subbedOutTime", axis=1)
    train = train.drop("position", axis=1)
    train = train.drop("fantasyScore", axis=1)

    null_positions = train[train['positionStringShort'].isna()]

    # 각 널값에 대해 처리
    for index, row in null_positions.iterrows():
        # 현재 널값이 있는 행의 'name' 가져오기
        name = row['name']
        # 해당 'name'을 가진 모든 행에서 'positionStringShort'의 최빈값 찾기
        most_frequent_position = train[train['name'] == name]['positionStringShort'].mode()[0]
        # 널값 채우기
        train.at[index, 'positionStringShort'] = most_frequent_position

    train = train.drop("name", axis=1)
    # rating 널값 제거, 개수가 매우적어 없는거만 제거
    train = train.dropna(subset=["rating"])

    # x , y 나누기
    train_x = train.drop("rating", axis=1)
    train_y = data["rating"]

    # 'positionStringShort'와 'positionRow' 열 선택
    train_x_cat = train_x[['positionStringShort', 'positionRow']].values
    # OneHotEncoder 객체 생성
    cat_encoder = OneHotEncoder()
    # 원-핫 인코딩 적용
    train_x_cat_1hot = cat_encoder.fit_transform(train_x_cat)
    # positionStringShort, positionRow은 카테고리컬
    train_x_num = train_x.drop(["positionStringShort", "positionRow"], axis=1)

    # 불리언 타입이 아닌 수치형 데이터만 선택
    numeric_features = train_x_num.select_dtypes(include=['int64', 'float64'])
    # StandardScaler 객체 생성
    scaler = StandardScaler()
    # 수치형 데이터에 표준화 적용
    numeric_features_scaled = scaler.fit_transform(numeric_features)






    # 해당 match_id에 대한 데이터 필터링
    data = data[data['matchId'] == match_id]

    # 불필요한 피쳐 제거
    data = data.drop(["matchId", "subbedOutTime", "position", "fantasyScore", "subbedInTime"], axis=1)

    # 피쳐 이름 변경
    rename_columns = {
        'accurate_passes': 'accurate_passes_rate(%)',
        'shot_accuracy': 'shot_accuracy(%)',
        'accurate_long_balls': 'long_balls_accuracy(%)',
        'tackles_won': 'tackles_won_rate(%)',
        'ground_duels_won': 'ground_duels_won_rate(%)',
        'aerial_duels_won': 'aerial_duels_won_rate(%)',
        'successful_dribbles': 'dribble_success_rate(%)',
        'accurate_crosses': 'crosses_success_rate(%)'
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
    data = data.drop(["name"], axis=1)

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

    # 원-핫 인코딩 적용
    data_x_cat_1hot = cat_encoder.transform(data_x_cat)

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

    # 수치형 데이터에 표준화 적용
    numeric_features_scaled = scaler.transform(numeric_features)
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

def perform_prediction(data_x, data_y):
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
    print(model_rmses)
    print(best_predictions)

    return best_predictions, model_rmses  # 예측 결과와 RMSE 반환s

def format_predictions(predictions, data_y, player_names, positions):
    '''
    results = {}
    for name, position, actual, predicted in zip(player_names, positions, data_y, predictions):


        results[position] = ({"name": name, "actual": actual, "predicted": predicted})


    return results
    '''


    results = {}
    for name, position, actual, predicted in zip(player_names, positions, data_y, predictions):
        if position not in results:
            results[position] = []
        results[position].append({"name": name, "actual": actual, "predicted": predicted})
    return results

if __name__ == '__main__':
    app.run(debug=True)
