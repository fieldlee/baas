import os
from flask_restful import Resource,reqparse
from flask import jsonify
import asyncio
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

        untils.CreateDir("%s/%s/%s"%(path,"certification",id))

        untils.GenerateConfigtx(doc)

        untils.GenerateCrypto(doc)

        # 生成certificate
        untils.GenerateCert(doc)

        # 生成order yaml
        untils.GenerateOrder(doc)
        # 生成peer yaml
        untils.GeneratePeer(doc)
        # 生成couch yaml
        untils.GenerateCouch(doc)
        # 生成cayaml
        untils.GenerateCa(doc)

        #生成
        untils.Tar(doc)
        #send tar文件到各个服务器
        loop = asyncio.get_event_loop()
        #wait to send file 各个服务器

        tasks = []
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

        return jsonify({"success":True})

