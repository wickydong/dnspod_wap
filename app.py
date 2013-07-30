#!/usr/bin/python
# -*-coding:utf-8-*-
import json
import requests
from flask import Flask,render_template,request,session,url_for,redirect,session,make_response

app = Flask(__name__)

#登录页


@app.route("/")
def index():
    return render_template("index.html", is_dtoken=False)

#获取用户帐号以及密码并储存，重定向到域名列表路由

@app.route("/login",methods=["POST"])
def login_d():
    user_mail = request.form["user_mail"]
    user_passwd = request.form["user_passwd"]
    user_d = request.form.get('user_d')

    login_data = {"login_email": user_mail,"login_password": user_passwd,"login_code": user_d,"format": "json"}
    login_request = requests.post("https://dnsapi.cn/User.Detail",data=login_data)
    print login_request.cookies
    user_message = json.loads(login_request.text)
    user_status = user_message["status"]
    user_code = user_status["code"]
    if int(user_code) == 1:
        session["user_mail"] = user_mail
        session["user_passwd"] = user_passwd
        for i in login_request.cookies:
            if i.name[0] == 't':
                session['cookies'] = {i.name: i.value}
        return redirect(url_for('domainlist', state=' '))
    elif int(user_code) == 50:
        return render_template("index.html", is_dtoken=True, user_mail=user_mail, user_passwd=user_passwd)
    else:
        return render_template("index.html", is_dtoken=False, user_mail=user_mail, user_passwd=user_passwd)


#进入域名列表

@app.route("/domainlist/<state>")
def domainlist(domainfree=None,domainvip=None,state=None):
    login_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"format": "json","error_on_empty": "no"}
    login_request = requests.post("https://dnsapi.cn/Domain.List",data=login_data, cookies=session['cookies'])
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
    return render_template("domainlist.html",domainfree=domainfree,domainvip=domainvip,state=state)

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
        return redirect(url_for("domainlist",state="del domain is successful"))
    elif code == -15 or code == 7:
        state = "domain is already ban or lock"
        return redirect(url_for("domainlist",state=state))

#禁用域名

@app.route("/disabled/<domain>")
def disabled(domain):
    return render_template("disabled.html",domain=domain)

#确认禁用

@app.route("/disabled_domain/<domain>")
def disabled_domain(domain):
    disabled_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain": domain,"status": "disable","format": "json"}
    disabled_request = requests.post("https://dnsapi.cn/Domain.Status",data=disabled_data)
    disabled_result = json.loads(disabled_request.text)
    status = disabled_result["status"]
    code = int(status["code"])
    if code == 1:
        return redirect(url_for("domainlist",state="disable domain is successful"))
    else:
        state = "domain is not disabled"
        return redirect(url_for("domainlist",state=state))



#退出登录
@app.route("/login_out")
def login_out():
    session.pop("user_mail",None)
    return redirect(url_for("index"))


if __name__ == "__main__":   
    app.secret_key = 'fuckmjj'
    app.run(host="0.0.0.0",port=1234,debug=True)    
