#!/usr/bin/python
# -*-coding:utf-8-*-
import json
import requests
from flask import Flask,render_template,request,session,url_for,redirect,session,make_response
g_record_line = {}

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
        session['cookies'] = ''
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
        domainid = domainmessage["id"]
        domainstatus = domainmessage["status"]
        t = {"domainname":domainname,"domainid": domainid,"status": domainstatus}
        if domaingrade == "D_Free" or domaingrade == "DP_Free":
            domainfree.append(t)
            print domainname,"is free"
        else:
            domainvip.append(t)
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
    add_domain_request = requests.post("https://dnsapi.cn/Domain.Create",data=add_domain_data,cookies=session['cookies'])
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

#编辑域名

@app.route("/editdomain")
def editdomain():
    domain = request.args.get("domain")
    domainid = request.args.get("domain_id")
    rm_state = request.args.get("rm_state")
    print domain,domainid
    editdomain_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain_id": domainid,"format":"json","error_on_empty": "no"}
    editdomain_request = requests.post("https://dnsapi.cn/Record.List",data=editdomain_data,cookies=session['cookies'])
    editdomain_result = json.loads(editdomain_request.text)
    records = editdomain_result["records"]
    print records
    return render_template("editdomain.html",records=records,domain=domain,domainid=domainid,rm_state=rm_state)


#进入修改域名记录(后续)

@app.route("/edit_record")
def edit_record():
    domain = request.args.get("domain")
    record_id = request.args.get("record_id")
    domainid = request.args.get("domain_id")
    recordinfo_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain_id": domainid,"format":"json","record_id": record_id}
    recordinfo_request = requests.post("https://dnsapi.cn/Record.Info",data=recordinfo_data,cookies=session['cookies'])
    recordinfo_result = json.loads(recordinfo_request.text)
    domain_grade = recordinfo_result["domain"]["domain_grade"]
    sub_domain = recordinfo_result["record"]["sub_domain"]
    record_value = recordinfo_result["record"]["value"]
    record_type = recordinfo_result["record"]["record_type"]
    ttl = recordinfo_result["record"]["ttl"]
    mx = recordinfo_result["record"]["mx"]


    rl_key = 'rl_' + session['user_mail'] + '_' + domain
    if rl_key in g_record_line:
	recordline = g_record_line[rl_key]
    else:
    	recordline_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain_id": domainid,"format": "json","domain_grade": domain_grade}
    	recordline_request = requests.post("https://dnsapi.cn/Record.Line",data=recordline_data,cookies=session["cookies"])
    	recordline_result = json.loads(recordline_request.text)
    	recordline = recordline_result["lines"]
	g_record_line[rl_key] = recordline
    return render_template("edit_record.html",domain=domain,recordline=recordline,sub_domain=sub_domain,record_value=record_value,record_type=record_type,ttl=ttl,mx=mx,domain_id=domainid,record_id=record_id)

@app.route("/editrecord",methods=["POST","GET"])
def editrecord():
    #recordline = request.args.get("recordline")
    domain = request.args.get("domain")
    domain_id = request.args.get("domain_id")
    record_id = request.args.get("record_id")
    print domain_id,record_id
    sub_domain = request.form["sub_domain"]
    record_type = request.form["record_type"]
    recordline = request.form["recordline"]
    record_value = request.form["record_value"]
    mx = request.form["mx"]
    ttl = request.form["ttl"]
    modify_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain_id": domain_id,"format":"json","record_id": record_id,"sub_domain": sub_domain,"record_type": record_type,"record_line": recordline,"value": record_value,"mx": mx,"ttl": ttl}
    recordmodify_request = requests.post("https://dnsapi.cn/Record.Modify",data=modify_data,cookies=session["cookies"])
    recordmodify_result = json.loads(recordmodify_request.text)
    recordmodify_code = recordmodify_result["status"]["code"]
    print recordmodify_code
    if int(recordmodify_code) == 1:
        modify_status = "successful"
    else:
        modify_status = "wrong"
    rl_key = 'rl_' + session['user_mail'] + '_' + domain
    return render_template("edit_record.html",domain=domain,recordline=g_record_line[rl_key],sub_domain=sub_domain,record_value=record_value,record_type=record_type,ttl=ttl,mx=mx,domain_id=domain_id,record_id=record_id,modify_status=modify_status)
    #return recordmodify_code
    
#禁用记录（后续）

@app.route("/record_status/")
def record_status():
    return render_template("record_status.html")

#删除记录
@app.route("/rm_record")
def rm_record():
    domain = request.args.get("domain")
    record_id = request.args.get("record_id")
    domain_id = request.args.get("domain_id")
    print domain,record_id,domain_id
    return render_template("rm_record.html",record_id=record_id,domain_id=domain_id,domain=domain)
#确认删除记录
@app.route("/rm_record_sure")
def rm_record_sure():
    domain = request.args.get("domain")
    record_id = request.args.get("record_id")
    domain_id = request.args.get("domain_id")
    rm_record_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain_id": domain_id,"format":"json","record_id": record_id}
    rm_record_request = requests.post("https://dnsapi.cn/Record.Remove",data=rm_record_data,cookies=session["cookies"])
    rm_record_result = json.loads(rm_record_request.text)
    rm_code = rm_record_result["status"]["code"]
    print rm_code,domain,domain_id
    if int(rm_code) == 1:
        rm_state = "success"
        return redirect(url_for("editdomain",domain=domain,domain_id=domain_id,rm_state=rm_state))
    else:
        rm_state = "wrong"
        return redirect(url_for("editdomain",domain=domain,domain_id=domain_id,rm_state=rm_state))


#删除域名

@app.route("/rm/<domain>",methods=["GET"])
def rm(domain):
    return render_template("rm.html",domain=domain)


#确认删除

@app.route("/rm_domain/<domain>",methods=["GET"])
def rm_domain(domain):
    D_code = request.args.get("D_code",None)
    rm_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain": domain,"format": "json","login_code": D_code}
    rm_request = requests.post("https://dnsapi.cn/Domain.Remove",data=rm_data,cookies=session['cookies'])
    rm_result = json.loads(rm_request.text)
    status = rm_result["status"]
    code = int(status["code"])
    print code
    if code == 1:
        return redirect(url_for("domainlist",state="del domain is successful"))
    elif code == -15 or code == 7 or code == 8:
        state = "domain was ban,lock or vip"
        return redirect(url_for("domainlist",state=state))
   #需要加入D令牌判断 code == 50 
    elif code == 50:
        return render_template("D_code.html",domain=domain)
#禁用域名

@app.route("/disabled/<domain>")
def disabled(domain):
    return render_template("disabled.html",domain=domain)

#确认禁用

@app.route("/disabled_domain/<domain>")
def disabled_domain(domain):
    disabled_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain": domain,"status": "disable","format": "json"}
    disabled_request = requests.post("https://dnsapi.cn/Domain.Status",data=disabled_data,cookies=session['cookies'])
    disabled_result = json.loads(disabled_request.text)
    status = disabled_result["status"]
    code = int(status["code"])
    if code == 1:
        return redirect(url_for("domainlist",state="disable domain is successful"))
    else:
        state = "domain is not disabled"
        return redirect(url_for("domainlist",state=state))
   #需要加上D令牌报错判断 code == 50
#启用域名
@app.route("/enable/<domain>")
def enable(domain):
    enable_data = {"login_email": session["user_mail"],"login_password": session["user_passwd"],"domain": domain,"status": "enable","format": "json"}
    enable_request = requests.post("https://dnsapi.cn/Domain.Status",data=enable_data,cookies=session['cookies'])
    enable_result = json.loads(enable_request.text)
    status = enable_result["status"]
    code = int(status["code"])
    if code == 1:
        return redirect(url_for("domainlist",state="enable domain is successful"))
    else:
        state = "domain is not enabled"
        return redirect(url_for("domainlist",state=state))

#退出登录
@app.route("/login_out")
def login_out():
    session.pop("user_mail",None)
    session.pop("user_passwd", None)
    session.pop("cookies", None)
    return redirect(url_for("index"))


if __name__ == "__main__":   
    app.secret_key = 'fuckmjj'
    app.run(host="0.0.0.0",port=1234,debug=True)    
