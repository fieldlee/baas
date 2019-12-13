#!/usr/bin/python
#coding:utf-8

import os
import aiohttp
from flask_restful import Resource,reqparse
from flask import jsonify
import asyncio
from . import Couchdb,db,untils,SyncPort


parser = reqparse.RequestParser(trim=True)
parser.add_argument("id")

async def aiohttp_post(url,path,filename):
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field(name='file',value=open(path,'rb'),filename=filename,content_type='image/jpeg')
        # files = {'file':open(path,'rb')}
        async with session.post(url,data=data) as resp:
            print(await resp.text())



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
        # 生成cliyaml
        untils.GenerateCli(doc)
        #生成
        untils.Tar(doc)

        #wait to send file 各个服务器

        tasks = []
        ipList = []
        for order in doc['orders']:
            if not order["orderIp"] in ipList:
                ipList.append(order["orderIp"])

        for org in doc['orgs']:
            for peer in org['peers']:
                if not peer['peerIp'] in ipList:
                    ipList.append(peer['peerIp'])

        # 生成tasks list
        print(ipList)
        for ip in ipList:
            tmpurl = 'http://%s:%s/upcert'%(ip,str(SyncPort))
            curPath = os.path.abspath(os.curdir)
            certpath = os.path.join(curPath, "certification", '%s.tar'%doc["_id"])
            filename = '%s.tar'%doc["_id"]
            tasks.append(aiohttp_post(tmpurl,path=certpath,filename=filename))

        # send tar文件到各个服务器
        loop = asyncio.new_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)

        return jsonify({"success":True})

