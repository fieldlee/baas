import os
from flask_restful import Resource,reqparse
from flask import json,  jsonify
from . import Couchdb,db,untils


parser = reqparse.RequestParser(trim=True)
parser.add_argument("id")



class Generate(Resource):
    def post(self):
        args = parser.parse_args()
        id = args["id"]
        doc = db.QueryById(Couchdb,id)

        #create path
        path = os.path.abspath(os.curdir)
        print(path)

        untils.CreateDir("%s/%s/%s"%(path,"certification",id))

        untils.GenerateConfigtx(doc)

        untils.GenerateCrypto(doc)

        untils.GenerateOrder(doc)

        untils.GeneratePeer(doc)
