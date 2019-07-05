import os
from flask_restful import Resource,reqparse
from flask import jsonify
import asyncio,aiohttp
from . import Couchdb,db,untils


parser = reqparse.RequestParser(trim=True)
parser.add_argument("id")
parser.add_argument("channel")

async def postCommand(url,data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data=data) as resp:
            return resp.status

class UpEnv(Resource):
    def post(self):
        args = parser.parse_args()
        id = args["id"]
        doc = db.QueryById(Couchdb, id)

        ipList = []

        for order in doc["orders"]:
            if not order["orderIp"] in ipList:
                ipList.append(order["orderIp"])

        for org in doc["orgs"]:
            for peer in org["peers"]:
                if not peer["peerIp"] in ipList:
                    ipList.append(peer["peerIp"])

        #生成启动命令
        # docker ps - a - -filter name = 'mysql'
        command = "docker stop $(docker ps -q  --filter name='%s');"% doc["domain"]
        command += "docker rm $(docker ps -q  --filter name='%s');"% doc["domain"]

        commandMap = {}

        for ip in ipList:
            yamlList = []
            for order in doc["orders"]:
                if order["orderIp"].lstrip().rstrip() == ip.lstrip().rstrip():
                    yamlname = "order_%s.yaml"%order["orderId"]
                    if not yamlname in yamlList:
                        yamlList.append(yamlname)

            for org in doc["orgs"]:
                for peer in org["peers"]:
                    if peer["peerIp"].lstrip().rstrip() == ip.lstrip().rstrip():
                        yamlname = "%s_%s.yaml" % (peer["peerId"],org["orgId"])

                        if not yamlname in yamlList:
                            yamlList.append(yamlname)
                        if "joinCouch" in peer :
                            couchyaml = "couch_%s_%s.yaml"%(peer["peerId"],org["orgId"])
                            if not couchyaml in yamlList:
                                yamlList.append(couchyaml)
                # certification yaml 启动
                yamlca = "ca_%s.yaml"%org["orgId"]
                if not yamlca in yamlList:
                    yamlList.append(yamlca)

            #生成ip对应的yamlmap
            commandMap[ip.lstrip().rstrip()] = yamlList

        #分发到各个服务上生成docker
        tasks = []
        for ip in ipList:
            # docker-compose %s up - d
            fline = ""
            print(commandMap)
            for yfile in commandMap[ip]:
                fline += " -f %s "%yfile

            dockerstr = "%s docker-compose %s up -d;"%(command,fline)
            print(dockerstr)
            url = "http://%s/upenv"%ip
            tasks.append(postCommand(url,data=dockerstr))

        #启动docker环境
        loop = asyncio.get_event_loop()

        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        return jsonify({"success":True})


class Channel(Resource):
    def post(self):
        # commandLine += "../configtxgen -profile ProjectOrgsChannel -outputCreateChannelTx ./%s.tx -channelID %s;" % (
        # channelid, channelid)
        args = parser.parse_args()
        id = args["id"]
        channelid = args["channel"]
        doc = db.QueryById(Couchdb, id)

        chanlist = []
        channel = {}
        # 判断channel是否存在
        if "channel" in doc:
            for chan in doc["channel"]:
                if chan["channelid"] == channelid :
                    channel = chan
                else:
                    chanlist.append(chan)
        # 赋值到channel中
        channel["channelid"] = channelid
        channel["status"] = "generate"

        curPath = os.path.abspath(os.curdir)
        toPath = os.path.join(curPath, "certification", doc["_id"])
        commandline = "cd % s; export FABRIC_CFG_PATH =$PWD; ../configtxgen -profile ProjectOrgsChannel -outputCreateChannelTx ./%s.tx -channelID %s;"%(toPath,channelid,channelid)
        os.system(commandline)

        #save doc
        chanlist.append(channel)
        doc["channel"] = chanlist
        db.save(doc)

        #return
        return jsonify({"success":True})

