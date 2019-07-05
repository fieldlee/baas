from flask import Flask
from flask_restful import Api
from handle import format,generate,upenv


baasApp = Flask(__name__)
api = Api(baasApp)


api.add_resource(format.Format,'/save')
api.add_resource(generate.Generate,'/generate')
api.add_resource(upenv.UpEnv,'/up')
api.add_resource(upenv.Channel,'/channel')
api.add_resource(upenv.ApiGene,'/api')

if __name__ == "__main__":
    baasApp.run(debug=True,port=8080)