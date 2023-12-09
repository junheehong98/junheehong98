from flask import Flask, request, jsonify
import pickle
import os
import numpy as np
from sklearn.metrics import mean_squared_error



app = Flask(__name__)

# 모델 불러오기 및 예측 수행
model_names = ['tree_reg', 'voting_regressor', 'gbrt', 'sgd_reg', 'rnd_for', 'svm_reg']

# 각 모델을 불러와 저장할 딕셔너리
loaded_models = {}

# 모델 불러오기
for model_name in model_names:
    with open(f'{model_name}.pkl', 'rb') as file:
        loaded_models[model_name] = pickle.load(file)

@app.route('/predict', methods=['POST'])
def predict():
    # JSON 요청을 파싱
    data = request.get_json(force=True)
    features = data['features']
    actual_labels = data.get('labels')  # 실제 레이블 (옵션)

    # 모든 모델에 대해 예측 수행 및 RMSE 계산
    predictions = {}
    for model_name, model in loaded_models.items():
        prediction = model.predict([features])
        predictions[model_name] = {'prediction': prediction.tolist()}

        # 실제 레이블이 제공된 경우 RMSE 계산
        if actual_labels is not None:
            from sklearn.metrics import mean_squared_error
            rmse = np.sqrt(mean_squared_error([actual_labels], [prediction]))
            predictions[model_name]['rmse'] = rmse

    # 모든 예측 결과와 RMSE를 JSON으로 반환
    return jsonify(predictions)


if __name__ == '__main__':
    app.run(debug=True)