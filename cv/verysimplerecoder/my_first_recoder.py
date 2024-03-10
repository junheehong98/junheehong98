import cv2

# 카메라 초기화
cap = cv2.VideoCapture(0)

# 비디오 저장을 위한 설정
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

recording = False  # 녹화 상태 플래그

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if recording:
        # 녹화 모드일 때, 프레임을 파일에 쓴다.
        out.write(frame)
        # 녹화 상태를 화면에 표시 (예: 빨간색 원)
        cv2.circle(frame, (50, 50), 20, (0, 0, 255), -1)

    # 화면에 현재 카메라 영상 표시
    cv2.imshow('Video Recorder', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):  # Space 키로 녹화 상태 전환
        recording = not recording
    elif key == 27:  # ESC 키로 종료
        break

# 종료 처리
cap.release()
out.release()
cv2.destroyAllWindows()
