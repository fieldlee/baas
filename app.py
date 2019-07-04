from flask import Flask,request,jsonify
from flask_restful import reqparse,Api,Resource,reqparse
from handle import format,generate


baasApp = Flask(__name__)
api = Api(baasApp)


api.add_resource(format.Format,'/save')
api.add_resource(generate.Generate,'/generate')

if __name__ == "__main__":
    baasApp.run(debug=True,port=8080)