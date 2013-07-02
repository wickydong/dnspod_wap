#!/usr/bin/python
# -*-coding:utf-8-*-
import json
import requests
from flask import Flask,render_template,request

app = Flask(__name__)

#登录页

@app.route("/")
def index():
    return render_template("index.html")
#用户输入帐号密码登录，显示帐号下域名列表
@app.route("/user",methods=["POST"])
def dnspod_login():
    user_mail = request.form["user_mail"]
    user_passwd = request.form["user_passwd"]
    login_data = {"login_email": user_mail,"login_password": user_passwd,"format": "json"}
    login_request = requests.post("https://dnsapi.cn/User.Detail",data=login_data)
    user_message = json.loads(login_request.text)
    print user_message
    #return render_template("login.html")
    return ""

#添加域名并返回添加成功与否

@app.route("/add_domain")
def Add_Domain():
    add_domain_data = {"login_email": user_mail,"login_password": user_passwd,"domain":add_domain,"format":"json"} 
    add_domain_request = requests.post("https://dnsapi.cn/Domain.Create",data=add_domain_data)
    add_domain_result = json.loads(add_admin_request.text)
    if add_domain_result[status[code]] == 1:
        add_domain_status = "ok"
    elif add_domain_request[status[code]] == 7 or add_domain_request[status[code]] == 11 or add_domain_request[status[code]] == 12:
        add_domain_status = "exists"
    else:
        add_domain_status = "fail"
    return render_template("add_domain.html", add_domain_status=add_domain_status)
    
if __name__ == "__main__":
   app.run(host="0.0.0.0",port=1234,debug=True)    
