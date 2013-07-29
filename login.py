#!/usr/bin/python
# -*-coding:utf-8-*-
import json
import requests
from flask import Flask,render_template,request,session,url_for,redirect,session

app = Flask(__name__)

#登录页


@app.route("/")
def index():
    return render_template("index.html")

#获取用户帐号以及密码并储存，重定向到域名列表路由

@app.route("/login", methods=["POST"])
def login():
    user_mail = request.form["user_mail"]
    user_passwd = request.form["user_passwd"]
    login_data = {"login_email": user_mail,"login_password": user_passwd,"format": "json"}
    login_request = requests.post("https://dnsapi.cn/User.Detail",data=login_data)
    user_message = json.loads(login_request.text)
    user_status = user_message["status"]
    user_code = user_status["code"]
    if int(user_code) == 1:
        session["user_mail"] = user_mail
        session["user_passwd"] = user_passwd
        print session["user_mail"]
        return redirect(url_for('domainlist'))
    elif int(user_code) == 50:
        return render_template("index_d.html")
    else:
        return render_template("index.html")
#D令牌登录
@app.route("/login_d",methods=["POST"])
def login_d():
    user_mail = request.form["user_mail"]
    user_passwd = request.form["user_passwd"]
    user_d = request.form["user_d"]
    
    login_data = {"login_email": user_mail,"login_password": user_passwd,"login_code": user_d,"format": "json"}
    login_request = requests.post("https://dnsapi.cn/User.Detail",data=login_data)
    
    user_message = json.loads(login_request.text)
    user_status = user_message["status"]
    user_code = user_status["code"]
    print user_code
    if int(user_code) == 1:
        d_cookies = make_response(user_message)
        d_cookies.set_cookies()
        session["user_mail"] = user_mail
        session["user_passwd"] = user_passwd
        print session["user_mail"]
        return redirect(url_for('domainlist'))
    else:
        return render_template("index_d.html")


#进入域名列表

@app.route("/domainlist/<status>")
def domainlist(domainfree=None,domainvip=None,status=None):
    login_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"format": "json"}
    login_request = requests.post("https://dnsapi.cn/Domain.List",data=login_data)
    domainlist = json.loads(login_request.text)
    domaininfo = domainlist["info"]
    domainnum = domaininfo["all_total"]
    vip_total = domaininfo["vip_total"]
    print domainnum,vip_total
    domainlists = domainlist["domains"]
    domainfree = []
    domainvip = []
    for domainmessage in domainlists:
        domainname = domainmessage["name"]
        domaingrade = domainmessage["grade"]
        if domaingrade == "D_Free" or domaingrade == "DP_Free":
            domainfree.append(domainname)
            print domainname,"is free"
        else:
            domainvip.append(domainname)
            print domainvip,"is vip"
    return render_template("domainlist.html",domainfree=domainfree,domainvip=domainvip,status=status)

#从域名列表进入添加域名页面

@app.route("/add_domain",methods=["GET"])
def add_domain():
    return render_template("adddomain.html")

#添加域名并返回添加成功与否

@app.route("/add_domains",methods=["POST","GET"])
def Add_Domains(add_domain_status=None):
    add_domain = request.form["add_domain"]
    add_domain_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain":add_domain,"format":"json"} 
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

#删除域名
@app.route("/rm/<domain>",methods=["GET"])
def rm(domain):
    return render_template("rm.html",domain=domain)
#@app.route("/rm_domain",method)

#确认删除

@app.route("/rm_domain/<domain>",methods=["GET"])
def rm_domain(domain):
    
    rm_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain": domain,"format": "json"}
    rm_request = requests.post("https://dnsapi.cn/Domain.Remove",data=rm_data)
    rm_result = json.loads(rm_request.text)
    status = rm_result["status"]
    code = int(status["code"])
    if code == 1:
        return redirect(url_for("domainlist"))
    elif code == -15 or code == 7:
        status = "domain is already ban or lock"
        return redirect(url_for("domainlist",status=status))

#退出登录
@app.route("/login_out")
def login_out():
    session.pop("user_mail",None)
    return redirect(url_for("index"))


if __name__ == "__main__":   
    app.secret_key = 'fuckmjj'
    app.run(host="0.0.0.0",port=1234,debug=True)    
