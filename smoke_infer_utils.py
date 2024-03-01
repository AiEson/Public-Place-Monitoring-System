from ultralytics import YOLO
import cv2
tt = YOLO(model='./weights/smoke.pt',verbose=False)

def get_is_smoke_img(img, conf=0.8):
    frame = img.copy()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    prediction = tt.predict(frame)
    if len(prediction) > 0:
        return prediction[0].probs.data.numpy().tolist()[1] > conf
    
    return False


if __name__ == "__main__":
    video_path = "./Videos/smoke.mp4"
    cap = cv2.VideoCapture(video_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        smokeing = get_is_smoke_img(frame)
        print(smokeing)
        cv2.imshow("frame", cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()