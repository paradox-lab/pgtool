import requests
import os
import time
import json
import base64
from pgtool.ProgramTool.setting import themepath

def access_token():
    """"
       获取access_token
    """
    appid = 'wx41a3b499425417a7'
    secret = 'e56e7b2b447c15127e9f5e7084f76565'
    url ='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential'
    response = requests.get(url,params={'appid':appid,'secret':secret})
    result = response.json()
    return result["access_token"]

def init():
	datal=[]
	for dirname in os.listdir(themepath):
		for model_name in os.listdir(os.path.join(themepath,dirname)):
			path=os.path.join(themepath,dirname,model_name)

			for file in os.listdir(path):
				filename,filetype=os.path.splitext(file)
				modifiedTime=time.localtime(os.stat(os.path.join(path,file)).st_mtime)
				strmodifiedTime=time.strftime('%Y%m%d%H:%M:%S', modifiedTime)
				try:
					with open(os.path.join(path,file),'rb') as f:
						txt=f.read()
						txt = str(base64.b64encode(txt))[2:-1]
						# txt = txt.replace('\n', '\\n').replace('\"', '\\"')
				except UnicodeDecodeError:
					with open(os.path.join(path,file),'rb',encoding='utf8') as f:
						txt=f.read()
						txt=str(base64.b64encode(txt))
						# txt=txt.replace('\n','\\n').replace('\"','\\"')
				data = (dirname, model_name, filename, filetype,txt,strmodifiedTime)
				datal.append(dict(zip(('langtype','modelname','filename','filetype','txt','rowversion'),data)))

	data={'data':datal}
	data=json.dumps(data)
	ACCESS_TOKEN=access_token()

	env='wxproject-hsqfa'
	query='db.collection("model").add(' \
		  "{})".format(data)
	url='https://api.weixin.qq.com/tcb/databaseadd?access_token='+ACCESS_TOKEN
	params={'env':env,
			'query':query
			}

	r = requests.post(url, data = json.dumps(params))
	return r.text

def delete():
	ACCESS_TOKEN = access_token()
	env = 'wxproject-hsqfa'
	url='https://api.weixin.qq.com/tcb/databasedelete?access_token='+ACCESS_TOKEN
	query="""db.collection("model").where({langtype:'前端'}).remove()"""
	params={'env':env,
			'query':query
			}
	r = requests.post(url, data=json.dumps(params))
	return r.text



