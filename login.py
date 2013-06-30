#!/usr/bin/python
# -*-coding:utf-8-*-

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
    return login_request.text
if __name__ == "__main__":
   app.run(host="0.0.0.0",port=1234,debug=True)    
