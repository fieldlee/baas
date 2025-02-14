#!/usr/bin/python
#coding:utf-8

from flask import Flask
from flask_restful import Api
from flask_jsonrpc import JSONRPC
from flask_httpauth import HTTPTokenAuth
from handle import format,generate,upenv,clone,install,add


baasApp = Flask(__name__)
api = Api(baasApp)
auth = HTTPTokenAuth()
#jsonrpc = JSONRPC(baasApp, '/api', enable_web_browsable_api=False)

#根据json 生成文档
api.add_resource(format.Format,'/save')
#生成yaml文件和证书并且发送到服务器
api.add_resource(generate.Generate,'/generate')
#启动各个服务器上的对应的yaml
api.add_resource(upenv.UpEnv,'/up')
#生成channel tx文件并且发送到服务器
api.add_resource(upenv.Channel,'/channel')
#生成api config json文件 保持在服务器上并且发送
api.add_resource(upenv.ApiGene,'/api')
#clone chaincode 和 sdk
api.add_resource(clone.Clone,'/clone')
#生成chaincode shell命令
api.add_resource(install.Install,'/code')
#生成addOrg
api.add_resource(add.Add,'/addorg')
if __name__ == "__main__":
    baasApp.run(debug=True,port=8000)