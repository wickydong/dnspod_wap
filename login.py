#!/usr/bin/python
# -*-coding:utf-8-*-
import json
import requests
from flask import Flask,render_template,request,current_app,session,url_for,redirect

app = Flask(__name__)

#登录页


@app.route("/")
def index():
    return render_template("index.html")

#获取用户帐号以及密码并储存，重定向到域名列表路由

@app.route("/login", methods=["POST"])
def login():
    app.user_mail = request.form["user_mail"]
    app.user_passwd = request.form["user_passwd"]
    login_data = {"login_email": app.user_mail,"login_password": app.user_passwd,"format": "json"}
    login_request = requests.post("https://dnsapi.cn/User.Detail",data=login_data)
    print login_request.text
    user_message = json.loads(login_request.text)
    return redirect(url_for('domainlist'))

#进入域名列表

@app.route("/domainlist")
def domainlist(domainfree=None,domainvip=None):
    login_data = {"login_email": current_app.user_mail,"login_password": current_app.user_passwd,"format": "json"}
    login_request = requests.post("https://dnsapi.cn/Domain.List",data=login_data)
    domainlist = json.loads(login_request.text)
    domaininfo = domainlist["info"]
    domainnum = domaininfo["all_total"]
    vip_total = domaininfo["vip_total"]
    print domainnum,vip_total
    domainlists = domainlist["domains"]
    for domainmessage in domainlists:
        domainname = domainmessage["name"]
        domaingrade = domainmessage["grade"]
        if domaingrade == "D_Free" or domaingrade == "DP_Free":
            domainfree = domainname
            print domainfree,"is free"
        else:
            domainvip = domainname
            print domainvip,"is vip"
    return render_template("domainlist.html",domainfree=domainfree,domainvip=domainvip)

#从域名列表进入添加域名页面

@app.route("/add_domain",methods=["GET"])
def add_domain():
    return render_template("adddomain.html")

#添加域名并返回添加成功与否

@app.route("/add_domains",methods=["POST","GET"])
def Add_Domains(add_domain_status=None):
    add_domain = request.form["add_domain"]
    add_domain_data = {"login_email": current_app.user_mail,"login_password": current_app.user_passwd,"domain":add_domain,"format":"json"} 
    add_domain_request = requests.post("https://dnsapi.cn/Domain.Create",data=add_domain_data)
    add_domain_result = json.loads(add_domain_request.text)
    status = add_domain_result['status']
    code = int(status['code'])
    print code
    if code == 1:
        add_domain_status = "success"
    elif code == 7 or code == 11 or code == 12:
        add_domain_status = "exists"
    else:
        add_domain_status = "fail"
    return render_template("adddomain.html", add_domain_status=add_domain_status)
    
if __name__ == "__main__":
   app.run(host="0.0.0.0",port=1234,debug=True)    
