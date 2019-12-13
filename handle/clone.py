#!/usr/bin/python
#coding:utf-8

from flask_restful import Resource,reqparse
from flask import jsonify
import asyncio,aiohttp
from . import Couchdb,db,untils,SyncPort

parser = reqparse.RequestParser(trim=True)
parser.add_argument("id")
parser.add_argument("sdk")
parser.add_argument("cc")
parser.add_argument("ccname")

async def postClone(url,data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data=data) as resp:
            return resp.status

class Clone(Resource):
    def post(self):
        args = parser.parse_args()
        id = args["id"]
        sdkUrl = args["sdk"]
        ccUrl = args["cc"]
        ccName = args["ccname"]

        doc = db.QueryById(Couchdb, id)
        # 生成api服务
        ip = doc["apiip"]

        data = {'id':id,'sdk':sdkUrl,'cc':ccUrl,'ccname':ccName}

        cloneUrl = 'http://%s:%s/clone'%(ip,str(SyncPort))

        tasks = [postClone(cloneUrl, data)]
        # 启动docker环境
        loop = asyncio.new_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

        return jsonify({'success':True})