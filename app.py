from flask import Flask
from flask import request
import MySQLdb
import json
import moodle_api
from urllib.parse import unquote

moodle_api.URL = "https://asulearn.appstate.edu/"
#moodle_api.KEY = "72b2eecff7aa722a812268a906d228e1"
moodle_api.KEY='173b03e93d507cab8cba5a142fb8ca65'

db=MySQLdb.connect(host='127.0.0.1', #CHANGE BACK to db for docker
                    user='reedrw',
                    passwd='calvin',
                    db='moodle')
app=Flask(__name__)
@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/users')
def get_users():
    cur=db.cursor()
    cur.execute('select * from testable')
    output=[]
    print(type(output))
    
    for row in cur.fetchall():
        #output=output+str(row[0])+", "+row[1]+", "+row[2]+", "+str(row[3])+"\n"
        output.append({"field1":row[0],
        "field2":row[1],
        "field3":row[2],
        "field4":str(row[3])
        })
        

    return json.dumps(output)

@app.route('/addstds')
def addstudents():
    cur=db.cursor()
    courseid=request.args.get('course')
    students=moodle_api.call("core_enrol_get_enrolled_users",courseid=courseid)
    print ('total students=%s'%(len(students)))
    for student in students:
        print(student['id'],student['email'],student['fullname'])
        for groupnames in student['groups']:
            if groupnames['name'].find('REL')!=-1:
                cur.execute("""insert into students (course, id, email, fullname, coursegroup) VALUES (%s,%s,%s,%s,%s)""", (courseid, student['id'],student['email'],student['fullname'],groupnames['name']))
    db.commit()
    cur.close()
    return "True"

@app.route('/findstd')
def findstudent():
    cur=db.cursor()
    cur.execute("select count(*) from students;")
    tot=cur.fetchall()[0]
    tot=int(tot[0])
    print('total students=%s'% tot)
    print('tot type=%s' % type(tot))
    if tot==0:
        print('no students need sync')
        return "need_sync"
    else:
        email=request.args.get('email')
        print('email=%s'% email)
        id=request.args.get('id')
        print('id=%s' % id)
        if not id:
            cur.execute("select id from students where email='"+email+"';")
        else:
            cur.execute("select email from students where id="+str(id)+";")

        stdreq=cur.fetchall()
        if not stdreq:
            return "Not_Found"
        print(stdreq)
        print(stdreq[0][0])
        return str(stdreq[0][0])

@app.route('/findstdfull')
def findstdfull():
    cur=db.cursor()
    cur.execute("select count(*) from students;")
    tot=cur.fetchall()[0]
    tot=int(tot[0])
    print('total students=%s'% tot)
    print('tot type=%s' % type(tot))
    if tot==0:
        print('no students need sync')
        return "need_sync"
    else:
        email=request.args.get('email')
        print('email=%s'% email)
        id=request.args.get('id')
        print('id=%s' % id)
        if not id:
            cur.execute("select * from students where email='"+email+"';")
        else:
            cur.execute("select * from students where id="+str(id)+";")
        row_headers=[x[0] for x in cur.description] # this extracts headers
        stdreq=cur.fetchall()
        print(stdreq)
        if not stdreq:
            return "Not_Found"
        json_data=[]
        for result in stdreq:
            json_data.append(dict(zip(row_headers,result)))
        print(json_data)
        return json.dumps(json_data)

@app.route('/sqlrequest')
def sqlrequest():
    sql=unquote(request.args.get('request'))
    #print(sql)
    cur=db.cursor()
    if sql.find(';')==-1:
        sql=sql+";"
    print(sql)
    cur.execute(sql)
    results=cur.fetchall()
    print (results)
    #remove none first from tuple
    """ res=[tuple(xi for xi in x if xi is not None)for x in results]
    print (res)
    list1=[''.join(str(i)) for i in res]
    output=",".join(list1)
    print(output)
    print(type(output))"""
    row_headers=[x[0] for x in cur.description] # this extracts headers 
    json_data=[]
    for result in results:
        json_data.append(dict(zip(row_headers,result)))
    print(json_data)
    return json.dumps(json_data)

if '__name__':
    app.run(debug=True,host='0.0.0.0')