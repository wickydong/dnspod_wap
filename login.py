#!/usr/bin/python
# -*-coding:utf-8-*-
import json
import requests
from flask import Flask,render_template,request
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

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
@app.route("/add_domain")
def Add_Domain():
    add_domain_data = {"login_email": user_mail,"login_password": user_passwd,"domain":add_domain,"format":"json"} 
    add_domain_request = requests.post("https://dnsapi.cn/Domain.Create",data=add_domain_data)
    add_domain_result = json.loads(add_admin_request.text)
    
if __name__ == "__main__":
   app.run(host="0.0.0.0",port=1234,debug=True)    
