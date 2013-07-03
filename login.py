#!/usr/bin/python
# -*-coding:utf-8-*-
import json
import requests
from flask import Flask,render_template,request,current_app

app = Flask(__name__)

#登录页


@app.route("/")
def index():
    return render_template("index.html")

#用户输入帐号密码登录，显示帐号下域名列表
@app.route("/user",methods=["POST"])
def dnspod_login():
    app.user_mail = request.form["user_mail"]
    app.user_passwd = request.form["user_passwd"]
    login_data = {"login_email": app.user_mail,"login_password": app.user_passwd,"format": "json"}
    login_request = requests.post("https://dnsapi.cn/User.Detail",data=login_data)
    user_message = json.loads(login_request.text)
    print user_message
    return render_template("domainlist.html")

@app.route("/add_domain",methods=["GET"])
def Add_Domain():
    return render_template("adddomain.html")

#添加域名并返回添加成功与否

@app.route("/add_domains",methods=["POST"])
def Add_Domains():
    add_domain = request.form["add_domain"]
    add_domain_data = {"login_email": current_app.user_mail,"login_password": current_app.user_passwd,"domain":add_domain,"format":"json"} 
    add_domain_request = requests.post("https://dnsapi.cn/Domain.Create",data=add_domain_data)
    add_domain_result = json.loads(add_domain_request.text)
    status = add_domain_result['status']
    code = int(status['code'])
    print code
    if code == 1:
        add_domain_status = "ok"
    elif code == 7 or code == 11 or code == 12:
        add_domain_status = "exists"
    else:
        add_domain_status = "fail"
    return render_template("adddomain.html", add_domain_status=add_domain_status)
    
if __name__ == "__main__":
   app.run(host="0.0.0.0",port=1234,debug=True)    
