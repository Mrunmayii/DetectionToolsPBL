import cv2 as cv, time, pandas
import numpy as np
from datetime import datetime
import threading
import pyttsx3

def motionDetection():
    status_list=[None,None]
    times=[]
    df=pandas.DataFrame(columns=["Start","End"])
    alarm_sound = pyttsx3.init()
    voices = alarm_sound.getProperty('voices')
    alarm_sound.setProperty('voice', voices[0].id)
    alarm_sound.setProperty('rate', 150)    
    def voice_alarm(alarm_sound):
       alarm_sound.say("Motion Detected")
       alarm_sound.runAndWait()
    
    cap = cv.VideoCapture(0)
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    status=0
    while cap.isOpened():
        diff = cv.absdiff(frame1, frame2)
        diff_gray = cv.cvtColor(diff, cv.COLOR_BGR2GRAY)
        blur = cv.GaussianBlur(diff_gray, (5, 5), 0)
        _, thresh = cv.threshold(blur, 20, 255, cv.THRESH_BINARY)
        dilated = cv.dilate(thresh, None, iterations=3)
        contours, _ = cv.findContours(
            dilated, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y, w, h) = cv.boundingRect(contour)
            if cv.contourArea(contour) < 1000:
                continue
            status=1
            cv.rectangle(frame1, (x, y), (x+w, y+h), (0, 0, 200), 2)
            cv.putText(frame1, 'Movement Detected', (10, 20), cv.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0), 3)
        status_list.append(status)
            #status_list=status_list[-2:]
            
        if status_list[-1]>=1 and status_list[-2]==0:
            times.append(datetime.now())
            alarm = threading.Thread(target=voice_alarm, args=(alarm_sound,))
            alarm.start()
            '''if status_list[-1]==0 and status_list[-2]==1:
                times.append(datetime.now())
                alarm = threading.Thread(target=voice_alarm, args=(alarm_sound,))
                alarm.start()'''
        # cv.drawContours(frame1, contours, -1, (0, 255, 0), 2)

        cv.imshow("Video", frame1)
        frame1 = frame2
        ret, frame2 = cap.read()

        if cv.waitKey(10) == 27:
            if status==1:
                times.append(datetime.now())
            break
        
    for i in range(0,len(times),2):
        df=df.append({"Start":times[i],"End":times[i+1]},ignore_index=True)
        
    df.to_csv("Times.csv")
    alarm_sound.stop()  
    cap.release()
    cv.destroyAllWindows()

motionDetection()
    


