import cv2
import face_recognition
import pickle # to dumb the file
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage


cred = credentials.Certificate("serviceAccountKey.json") # setup the credential key
# firebase_admin.initialize_app(cred,{
#     'databaseURL':"https://realtimeattendance-87ec7-default-rtdb.firebaseio.com/",
#     'storageBucket':"gs://realtimeattendance-87ec7.appspot.com"
# })  
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://realtimeattendance-87ec7-default-rtdb.firebaseio.com/",
    'storageBucket':"realtimeattendance-87ec7.appspot.com"
}) 

# importing the face images
##########

filepath="images"
imagepathlist=os.listdir(filepath)# image path
# this gives roll.png
imagelist=[]
# we also extract their roll number as well as
studentroll=[]
# add path into the mode list 
for path in imagepathlist:
    imagelist.append(cv2.imread(os.path.join(filepath,path)))
    studentroll.append(os.path.splitext(path)[0])
    # studentroll.append()# extract the student roll number from the roll.png

    # to upload images to the database
    filename=f"{filepath}/{path}"
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)


# print(studentroll)
# print(len(imagelist))

# now we encode the images

def findencoding(imglist):
    encodelist=[]
    for img in imagelist:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB) # open cv uses the bgr [blue,green,red] not rgb so we converted it
        
        # find the encoding
        encode=face_recognition.face_encodings(img)[0]
        encodelist.append(encode)
    return encodelist

print("Encoding start.......")
encodinglistknown=findencoding(imagelist)
encodelistknownWithroll=[encodinglistknown,studentroll]
# print(encodinglistknown)
print("Encoding complete")

####### now we save in a pickle file
file=open("Encodefile.p","wb")
pickle.dump(encodelistknownWithroll,file)
file.close()
print("file saved .....")
