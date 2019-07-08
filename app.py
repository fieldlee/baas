from flask import Flask
from flask_restful import Api
from handle import format,generate,upenv,clone,install


baasApp = Flask(__name__)
api = Api(baasApp)

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

if __name__ == "__main__":
    baasApp.run(debug=True,port=8080)