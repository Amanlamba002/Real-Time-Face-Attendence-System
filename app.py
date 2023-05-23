
import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime


cred = credentials.Certificate("serviceAccountKey.json") # setup the credential key
# firebase_admin.initialize_app(cred,{
#     'databaseURL':"https://realtimeattendance-87ec7-default-rtdb.firebaseio.com/",
#     'storageBucket':"gs://realtimeattendance-87ec7.appspot.com"
# })  
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://realtimeattendance-87ec7-default-rtdb.firebaseio.com/",
    'storageBucket':"realtimeattendance-87ec7.appspot.com"
}) 

 
bucket=storage.bucket()
# start web cam
cap = cv2.VideoCapture(1)

# check if camera was opened successfully
if not cap.isOpened():
    print("Could not open camera")
    exit()

# set camera resolution
cap.set(3, 640) #to set the width
cap.set(4, 480) # to set the height 

# load the background image
imgBackground=cv2.imread("Resources/background.png")
##########
# importing the mode images into a list
foldermodepath="Resources/Modes"
modespaths=os.listdir(foldermodepath)# modepath 
# this modepaths give 1.png,2.png,3.png,4.png
modelist=[]
# add path into the mode list 
for path in modespaths:
    modelist.append(cv2.imread(os.path.join(foldermodepath,path)))


# resize the background image to match the size of the captured image
# imgBackground = cv2.resize(imgBackground, (1280,720))

# load the encoding file
print("loading encoding file ....")
file=open("Encodefile.p",'rb')
encodelistknownWithroll=pickle.load(file)
file.close()
encodinglistknown,studentroll=encodelistknownWithroll
# print(studentroll)
print("encoded file loaded")

modeType=0
counter=0
roll=-1
imgstudent=[]
while True:
    # read a new frame from the camera
    success, img = cap.read()
    
    imgSm=cv2.resize(img,(0,0),None,0.25,0.25)
    imgSm=cv2.cvtColor(imgSm,cv2.COLOR_BGR2RGB)

    FaceCurrFrame= face_recognition.face_locations(imgSm)
    encodeCurrframe=face_recognition.face_encodings(imgSm,FaceCurrFrame)



    imgBackground[162:162+480,55:55+640]=img
    imgBackground[44:44+633,808:808+414]=modelist[modeType]

    if FaceCurrFrame:
        for encodeFace,faceloc in zip(encodeCurrframe,FaceCurrFrame):
            matecs=face_recognition.compare_faces(encodinglistknown,encodeFace)
            faceDist=face_recognition.face_distance(encodinglistknown,encodeFace) # find the distance 
            
            # minimum the distance find the correct result

            matchesindex=np.argmin(faceDist)

            # print("Match Index",matchesindex)

            if matecs[matchesindex]:
                # when known face detected
                # print("Student of roll number : ", studentroll[matchesindex]," is present")
                y1,x2,y2,x1=faceloc
                y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
                bbox=55+x1,162+y1,x2-x1,y2-y1


                cvzone.cornerRect(imgBackground,bbox,rt=0)# rt bole to recrangle thickness
                roll=studentroll[matchesindex]
                # print(roll)
                if counter==0:
                    cvzone.putTextRect(imgBackground,'Loading',(275,400))
                    cv2.imshow("Background", imgBackground)
                    cv2.waitKey(1)
                    counter=1
                    modeType=1
        if counter!=0:

            if counter==1:
                studentInfo=db.reference(f'Student/{roll}').get()
                print(studentInfo)
                # get the image from the storage database
                blob=bucket.get_blob(f'images/{roll}.png')
                array=np.frombuffer(blob.download_as_string(),np.uint8)
                imgstudent=cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                # update data of attendance
                datetimeObject = datetime.strptime(studentInfo["Last-Attendance"],"%Y-%m-%d %H:%M:%S")
                secondelapsed=(datetime.now()-datetimeObject).total_seconds()
                print(secondelapsed)
                if secondelapsed>30:
                    ref=db.reference(f'Student/{roll}')
                    studentInfo['Total-Attendance']+=1
                    ref.child("Total-Attendance").set(studentInfo['Total-Attendance'])
                    ref.child("Last-Attendance").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType=3
                    counter=0
            
            if modeType!=3:
    #if mode type == 3 means attendance marked then the all image are reapply
                if 10<counter<20:
                    modeType=2
                imgBackground[44:44+633,808:808+414]=modelist[modeType]
        
                
                if counter<=10:

                    cv2.putText(imgBackground,str(studentInfo['Total-Attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(100,100,100),1) 
                    
                    
                    (w,h),_=cv2.getTextSize(studentInfo['Name'],cv2.FONT_HERSHEY_COMPLEX,1,1) # font sizw 1 thikness 1
                    offset=(414-w)//2 # it might be a float so we use //               # COZ of the image size are 414*633 png
                    cv2.putText(imgBackground,str(studentInfo['Name']),(808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1) 

                    cv2.putText(imgBackground,str(studentInfo['Major']),(1006,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(100,100,100),1)
                    
                    cv2.putText(imgBackground,str(roll),(1006,493),cv2.FONT_HERSHEY_COMPLEX,0.5,(100,100,100),1)
                    
                    cv2.putText(imgBackground,str(studentInfo['standing']),(918,625),cv2.FONT_HERSHEY_COMPLEX,0.5,(100,100,100),1)
                    
                    cv2.putText(imgBackground,str(studentInfo['year']),(1025,625),cv2.FONT_HERSHEY_COMPLEX,0.5,(100,100,100),1)

                    cv2.putText(imgBackground,str(studentInfo['Session']),(1125,625),cv2.FONT_HERSHEY_COMPLEX,0.5,(100,100,100),1)
                    
                    '''above function get total attendace of student, (861,125) 'are the location of it
                    fonttype ,next font size (255,255,255) are the white colour ,1 thikness'''
                    
                    imgBackground[175:175+216,909:909+216]=imgstudent

            

        ## resetting all the modes
            counter=counter+1
            if counter>20:
                counter = 0
                modeType = 0
                studentInfo = []
                imgstudent = []
                imgBackground[44:44+633,808:808+414]=modelist[modeType]


        

                


            # print("matecs",matecs)
            # print("facedistance",faceDist)
    
        # check if frame was successfully captured
        if not success:
            print("Error: Could not capture frame")
            break

        # resize the image to ensure valid dimensions
        img = cv2.resize(img, (640, 480))

        # blend the background image and the video frame using the addWeighted function
        # img = cv2.addWeighted(img, 0.5, imgBackground, 0.5, 0)

        # display the video frame in a window
        # cv2.imshow("Face Attendance", img)  # we don't need this so we hide it from the display 

        # display the background image in a separate window
    else:
        modeType=0
        counter=0
    cv2.imshow("Background", imgBackground)

    # wait for key press
    cv2.waitKey(1)
       

# release the camera and close the windows
cap.release()
cv2.destroyAllWindows()





