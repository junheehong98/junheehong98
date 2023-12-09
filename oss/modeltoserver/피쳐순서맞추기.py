# 필요한 라이브러리 불러오기
import pandas as pd

# 학습 데이터셋 로드
file_path_train = './modified_data7.csv'
train_data = pd.read_csv(file_path_train, encoding='cp1252')

# 예측 데이터셋 로드
file_path_predict = './tottenham_matches.csv'
predict_data = pd.read_csv(file_path_predict, encoding='cp1252')

# 학습 데이터셋과 예측 데이터셋의 특성 이름 비교
train_features = train_data.columns.tolist()
predict_features = predict_data.columns.tolist()

# 학습 데이터셋에만 존재하는 특성과 예측 데이터셋에만 존재하는 특성 확인
unique_to_train = set(train_features) - set(predict_features)
unique_to_predict = set(predict_features) - set(train_features)

print(unique_to_train, unique_to_predict)