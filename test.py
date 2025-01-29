import cv2 
import numpy as np 
import face_recognition 
import os 
import mysql.connector
import time 
from datetime import datetime 
from PIL import ImageEnhance 
import os

#This method takes a list of images and returns the face encodings using face_recognition library
def findEncodings(images): 
    encodeList = [] 
    for img in images:
        #  Converts the color format of the image from BGR to RGB. The face_recognition 
        # library expects images in RGB format.
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # The face_recognition library is used to extract face encodings from the converted image. 
        # The [0] index indicates that it is using the first (and presumably only) face in the image.
        encode = face_recognition.face_encodings(img)[0] 
        encodeList.append(encode)
    return encodeList 
 
# This method marks attendance for a given name by either inserting a 
# new record or updating the timestamp in the database.
def markAttendance(name,mydb):
    nameList = [] 
    mycursor = mydb.cursor() 
    mycursor.execute("SELECT * FROM class_a") 
    myresult = mycursor.fetchall() 
    for x in myresult: 
        nameList.append(x[0]) 
    if name not in nameList:
        sql = "INSERT INTO class_a (id,timestampvalue ) VALUES (%s, %s)" 
        timestamp = int(time.time()) 
        dt_stamp = datetime.fromtimestamp(timestamp) 
        val = (name, dt_stamp) 
        mycursor.execute(sql, val) 
        mydb.commit()
    else:
        timestamp = int(time.time()) 
        dt_stamp = datetime.fromtimestamp(timestamp)
        sql = "UPDATE class_a SET timestampvalue= %s  WHERE id=%s" 
        val = (dt_stamp, name)
        mycursor.execute(sql,val) 
        mydb.commit()
         
 
#This function connects to a MySQL database and returns the connection object.
def establishing_connection(): 
    mydb = mysql.connector.connect( 
        host="localhost", 
        user="root", 
        password="root", 
        database='cvproject' 
    ) 
 
    print(mydb) 
    return mydb

#This method Reads images from a specified directory, sends them for encoding, 
# and establishes a database connection.  
def encodeImages(): 
    path = 'C:/Users/ruthv/OneDrive/Desktop/CV/Project/ImagesAttendance' 
    images = [] 
    classNames = [] 
    myList = os.listdir(path) 
    print(myList) 
    mydb = establishing_connection(); 
 
    for cl in myList: 
        curImg = cv2.imread(f'{path}/{cl}') 
        images.append(curImg) 
        classNames.append(os.path.splitext(cl)[0]) 
    print(classNames) 
    encodeListKnown = findEncodings(images) 
    print('Encoding Complete') 
    return encodeListKnown,classNames,mydb 
 
 # This method is usd to capture video from the webcam, detects faces, 
 # recognize them, and mark attendance accordingly.  
def attendance_maker(encodeListKnown,classNames,mydb): 
    start_time = int(time.time()) 
    print("Start Time", start_time, sep='\t') 
    cap = cv2.VideoCapture(0) 
    img_path = r'testimg.jpg' 
    while True: 
        success, img = cap.read() 
        imgS = cv2.resize(img, (0, 0), None, 0.5, 0.5) 
        imgS = cv2.cvtColor(imgS, cv2.COLOR_RGB2BGR) 
        facesCurFrame = face_recognition.face_locations(imgS) 
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)        
        for encodeFace, faceLoc in zip (encodesCurFrame, facesCurFrame): 
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace) 
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace) 
            # print(faceDis) 
            matchIndex = np.argmin(faceDis) 
            if faceDis[matchIndex] < 0.55: 
                name = classNames[matchIndex].upper() 
                y1, x2, y2, x1 = faceLoc 
                y1, x2, y2, x1 = y1 * 2, x2 * 2, y2 * 2, x1 * 2 
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2) 
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED) 
                cv2.putText(img, name, (x1 + 6, y2 - 6),  
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2) 
                cv2.imshow('Webcam', img) 
                key = cv2.waitKey(0) 
                markAttendance(name,mydb)
                return

            else: 
                name = 'Unknown Person' 
                y1, x2, y2, x1 = faceLoc 
                y1, x2, y2, x1 = y1 * 2, x2 * 2, y2 * 2, x1 * 2 
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2) 
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED) 
                cv2.putText(img, name, (x1 + 6, y2 - 6),  
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2) 
                cv2.imshow('Webcam', img) 
                key = cv2.waitKey(0) 
                # if ((((int(time.time()))-start_time)>=10)):
            
                cap.release(); 
                cv2.destroyAllWindows()
                return


# The program flow starts here
from time import sleep 
if __name__=="__main__":

    encodeListKnown,classNames,mydb = encodeImages() 
    while True:
        input_value = input("Enter o to start, q to quit\n")
        if(input_value=="o"):
            attendance_maker(encodeListKnown,classNames,mydb)
        if(input_value == "q"):
            break