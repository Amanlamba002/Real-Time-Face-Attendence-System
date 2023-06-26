import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


cred = credentials.Certificate("serviceAccountKey.json") # setup the credential key
firebase_admin.initialize_app(cred,{
    'databaseURL':"write your own data base url"
})   # setup the realtime database 


ref=db.reference("Student")
data={
    '1900840100001':{
        'Name':"Akash Parashar",
        "Course":"B.tech",
        'Major':"CSE",
        'year':"4","standing":"G"
        ,'Session':"2019-2023",
        'Total-Attendance':0
        ,'Last-Attendance':'2023-05-09 00:54:20'

    },
    '1900840100002':{
        'Name':"Aman Raj Bharti",
        "Course":"B.tech",
        'Major':"CSE",
        'year':"4",
        "standing":"G",
        'Session':"2019-2023",
        'Total-Attendance':0
        ,'Last-Attendance':'2023-05-09 00:54:20'}
}


for key,value in data.items():
    ref.child(key).set(value)

 
