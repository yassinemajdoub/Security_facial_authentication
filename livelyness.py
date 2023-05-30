
import cv2
import time
import numpy as np

face_cascade = cv2.CascadeClassifier("C:\\Users\\betech.tn\\OneDrive\\Desktop\\New folder\\security project\\haarcascade_frontalface_alt2.xml")

def check_liveliness():
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("Failed to open camera.")
        exit()

    while True:
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray , scaleFactor = 1.5 , minNeighbors = 5)
        if len(faces) > 0:
            for (x,y,w,h) in faces:
                print(x,y,w,h)
                roi_gray = gray[y:y+h , x:x+w]
                roi_color = frame[y:y+h , x:x+w]
                #recognize:
                img_item = 'my_image.png'
                cv2.imwrite(img_item,roi_gray)
            result = texture_analysis(roi_color)
            print(result)
        else:
            print("No face detected")


        time.sleep(2)
        break
    video_capture.release()
    cv2.destroyAllWindows()

def texture_analysis(frame):
    lbp = cv2.ORB_create()
    keypoints, descriptors = lbp.detectAndCompute(frame, None)

    if descriptors is not None:
        descriptor_mean = np.mean(descriptors)
        descriptor_std = np.std(descriptors)
        print(descriptor_std)
        threshold = 72

        if descriptor_std > threshold:
            return "Live"
        else:
            return "Non-live"
    else:
        return "Non-live"
    
if __name__ == "__main__":
    check_liveliness()