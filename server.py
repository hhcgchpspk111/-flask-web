from flask import Flask,render_template,redirect,url_for,request,abort,session
from gevent import pywsgi
import pymysql
from Config import config#网址配置文件
from AppConfig import appConfig#程序配置文件
import json
import os

app = Flask(__name__)#设置flask设置
app.config.from_object(appConfig)

db = pymysql.connect(host=config.host,database=config.database,user=config.user,password=config.password)#连接数据库
db.ping(reconnect=True)#检查重新连接(长时间开启pymysql会断连)
cursor=db.cursor()#创建游标

def ipRecord(ip):
    try:
        cursor.execute("CREATE TABLE ips(ip varchar(255));")#创造数据库ip表
    except:
        pass
    cursor.execute("SELECT * FROM ips;")
    ipsNow = cursor.fetchall()#获取所有记录在数据库的ip
    if (str(ip) in str(ipsNow))==True:#若已经记录ip则跳过
        pass
    else:
        cursor.execute("INSERT INTO ips VALUES('%s');"%(ip))#插入ip
        db.commit()#提交ip信息
        with open("ips.log","a+",encoding="utf-8") as f:
            f.write(ip+"\n")
        #(双重保险,数据库记录ip同时用文本文件记录ip数据)
    ##记录ip值
    
def checkUsername(username,mark):
    selectUser="SELECT * FROM users;"
    cursor.execute(selectUser)
    results = cursor.fetchall()
    resultU = []#创建列表
    for row in results:
        _username=row[0]
        resultU.append(str(_username))
    if (username in resultU) and mark==1:#如何是更新用户
        pass
    elif (username not in resultU) and mark==0:#如果是添加用户
        pass
    else:#非法操作
        abort(400)
    ##检查用户名是否已存在

@app.route("/target")
def target():
    cursor.execute("SELECT * FROM users WHERE username='%s'"%(request.args.get('user')))#获取截取的url参数用户数据
    users = cursor.fetchall()
    for e in users:
        username=e[0]
        sex=e[1]
        mail=e[2]
        introduction=e[3]
        img=e[4]
    return render_template('target.html',username=username,sex=sex,mail=mail,introduction=introduction,img=img)#传递用户信息
    ##对象页面

@app.route("/clientIp")
def clientIp():
    cursor.execute("SELECT * FROM ips;")#查询所有ip
    ips = cursor.fetchall()
    ipsL = []
    for ip in ips:
        ipsL.append(ip[0])#添加ip列表
    return render_template("clientIp.html",ips=ipsL)
    ##获取访问ip
    
@app.route("/ipDrop",methods=["POST"])
def ipDrop():
    try:
        cursor.execute("DROP TABLE ips;")
        db.commit()
        return redirect(url_for("blank"))
    except Exception:
        abort(400)
    ##删除ip表

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["adminname"]==config.adminname and request.form["adminpassword"]==config.adminpassword:#检测是否管理员与密码正确
            session["adminname"]=request.form["adminname"]
            session["adminpassword"]=request.form["adminpassword"]
            #设置session会话信息
            return redirect(url_for("users"))
        else:
            abort(401)#错误信息返回无权限页面
    else:
        return render_template("login.html")
    ##登入页面
    
@app.route("/logout")
def logout():
    session.pop("adminname",None)
    session.pop("adminpassword",None)
    return redirect(url_for("login"))
    ##注销用户记录
    
@app.route("/createUser")#创建用户
def createUser():
    try:
        createUser="CREATE TABLE users(username varchar(255),sex varchar(255),mail varchar(255),introduction varchar(255),img varchar(255));"
        #创建用户表
        insertAdmin="INSERT INTO users(username,sex,mail,introduction,img) VALUES('name?','sex?','mail?','introduction?','img?');"
        insertUser="INSERT INTO users(username,sex,mail,introduction,img) VALUES('admin','man','qq@qq.com','programing','/static/img/admin.jpg');"
        #添加管理员和基本用户信息
        cursor.execute(createUser)
        cursor.execute(insertAdmin)
        cursor.execute(insertUser)
        #执行sql语句
        db.commit()#提交数据
        return "Successful create basic user"
    except:
       return 'Already create basic user'
    ##创建基本用户(测试数据库存在)

@app.route("/users")
def users():
    if "adminpassword" in session:
        selectUser="SELECT * FROM users"#获取用户信息
        cursor.execute(selectUser)#执行sql语句
        results = cursor.fetchall()#获取用户记录列表
        resultL = []#创建列表
        
        for row in results:
            username=row[0]
            sex = row[1]
            mail=row[2]
            introduction=row[3]
            img = row[4]
            resultL.append(str(username))
            resultL.append(str(sex))
            resultL.append(str(mail))
            resultL.append(str(introduction))
            resultL.append(str(img))
            resultL.append(str("*"))
            #添加列表内容
        return render_template("dbpage.html",result=json.dumps(resultL))#打开数据库控制面板模板
    else:
        abort(401)

@app.route("/addUser",methods=["POST"])
def adduser():
    try:
        username = request.form["username"]
        sex = request.form["sex"]
        mail = request.form['mail']
        introduction = request.form['introduction']
        img =request.form['img']
        #获取增加用户信息
        checkUsername(username,0)#检查用户名是否存在
        insertNew = "INSERT INTO users(username,sex,mail,introduction,img) VALUES('%s','%s','%s','%s','%s');"%(username,sex,mail,introduction,img)
        cursor.execute(insertNew)#添加新用户
        db.commit()#提交数据
        return redirect(url_for("users"))
    except Exception:
        abort(400)
    ##添加用户
    
@app.route('/delUser',methods=["POST"])
def delUser():
    try:
        username=request.form["username"]#获取删除用户信息
        delUser = "DELETE FROM users WHERE username='%s';"%(username)
        cursor.execute(delUser)#删除用户
        db.commit()
        return redirect(url_for("users"))
    except Exception:
        abort(400)
    ##删除用户
@app.route("/updateUser",methods=["POST"])
def updateUser():
    try:
        username=request.form["username"]
        sex = request.form['sex']
        mail = request.form['mail']
        introduction = request.form['introduction']
        img = request.form['img']
        #获取更新用户信息
        checkUsername(username,1)#检查用户名是否存在
        updateUser = "UPDATE users SET sex='%s',mail='%s',introduction='%s',img='%s' WHERE username='%s'"%(sex,mail,introduction,img,username)
        cursor.execute(updateUser)#更新用户
        db.commit()
        return redirect(url_for("users"))
    except Exception:
        abort(400)
    ##更新用户
@app.route("/dropUser",methods=["POST"])
def dropUser():
    try:
        cursor.execute("DROP TABLE users")
        db.commit()
        #删除用户表
        return redirect(url_for("blank"))
    except Exception:
        abort(400)
    ##删除用户表

@app.route("/upload")
def upload():
    return render_template("upload.html")
    
@app.route("/uploadFile",methods=["GET","POST"])
def uploadFile():
    if request.method == "POST":
        file=request.files["uploadFile"]#提取文件
        file.save(os.path.join("./static/upload",file.filename))#保存上传文件
    return render_template("success.html")
    ##文件上传保存
    
@app.route("/")#首页
def index():
    ipRecord(request.headers.get('X-Forwarded-For',request.remote_addr))#获取远程用户ip
    cursor.execute('SELECT username FROM users')
    users = cursor.fetchall()
    usersL=[]
    for row in users:
        usersL.append(row[0])
        #获取全用户名
    return render_template('index.html',users=usersL)
    ##首页

@app.route('/blank')
def blank():
    return ""
    ##空白页

@app.errorhandler(404)#404错误页面
def notFound(error):
    return render_template("404refresh.html")
    

if __name__ == "__main__":
    server = pywsgi.WSGIServer(('0.0.0.0',8080),app)
    server.serve_forever()
