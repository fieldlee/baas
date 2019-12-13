#!/usr/bin/python
#coding:utf-8

import os
from flask import jsonify
from flask_restful import Resource,reqparse
from . import Couchdb,db,untils


parser = reqparse.RequestParser(trim=True)
parser.add_argument("id")
parser.add_argument("channel")
parser.add_argument("org",type=dict,action='append')

class Add(Resource):
    def post(self):
        args = parser.parse_args()
        id = args["id"]
        channel = args["channel"]
        org = args["org"]

        orgId = ""

        tmpIP = ""
        ipNUm = 0
        for torg in org:
            for peer in torg['peers']:
                tmpIP = peer["peerIp"]

        doc = db.QueryById(Couchdb, id)

        for tOrg in doc['orgs']:
            for peer in tOrg['peers']:
                if tmpIP == peer["peerIp"]:
                    ipNUm += 1

        for torg in org:
            tmpOrg = {}
            tmpOrg["orgName"] = torg["orgId"]
            tmpOrg["orgId"] = torg["orgId"]
            tmpOrg["peerNumber"] = len(torg["peers"])
            orgId = torg["orgId"]
            j = 0
            peerList = []
            for peer in torg["peers"]:
                tmpPeer = {}

                if j == 0:
                    tmpOrg["anchorIp"] = peer["peerIp"]
                    tmpOrg["anchorPort"] = 7051 + 1000 * ipNUm
                    tmpOrg["caIp"] = peer["peerIp"]
                    tmpOrg["caPort"] = 7054 + 1000 * ipNUm
                    tmpOrg["caUser"] = "admin"
                    tmpOrg["caPwd"] = "adminpw"
                    tmpOrg["ContainerId"] = ("ca.%s.%s" % (tmpOrg["orgId"], doc["domain"]))

                tmpPeer["peerIp"] = peer["peerIp"]
                tmpPeer["peerId"] = "peer%s" % j
                tmpPeer["postPort"] = 7051 + 1000 * ipNUm
                tmpPeer["eventPort"] = 7053 + 1000 * ipNUm
                tmpPeer["ContainerId"] = ("%s.%s.%s" % (tmpPeer["peerId"], tmpOrg["orgId"], doc["domain"]))
                if "joinCouch" in peer:
                    if peer["joinCouch"] == True:
                        tmpPeer["joinCouch"] = True
                        tmpPeer["couchUsername"] = "couchadmin"
                        tmpPeer["couchPassword"] = "adminpwd"
                        tmpPeer["couchPort"] = 6984 + 1000 * ipNUm
                        tmpPeer["CouchContainerId"] = ("couch.%s" % tmpPeer["ContainerId"])
                peerList.append(tmpPeer)
                ipNUm += 1
                j += 1
            tmpOrg["peers"] = peerList


            doc['orgs'].append(tmpOrg)

        try:
            Couchdb.save(doc)
        except:
            return jsonify({"success":False})
        #生成crypto yaml 文件和 configtx 文件
        untils.GenerateAddCrypto(doc,orgId)
        untils.GenerateAddConfigtx(doc,orgId)
        #生成peer 和 couch yaml
        untils.GeneratePeer(doc,orgId)
        untils.GenerateCouch(doc,orgId)

        #生成add org
        untils.GenerateCli(doc)
        untils.GenerateCli(doc,orgId)

        #生成cli 处理sh 文件
        untils.GenerateCliAndAddCli(doc,channel=channel,orgid=orgId)
        #生成证书文件
        #cryptogen generate --config=./org3-crypto.yaml
        curPath = os.path.abspath(os.curdir)
        toPath = os.path.join(curPath, "certification", doc["_id"],orgId)
        comandLine = "cd %s ;"%toPath
        comandLine += "../cryptogen generate --config=./crypto_%s.yaml ;"%orgId
        comandLine += "export FABRIC_CFG_PATH=$PWD; ../../configtxgen  -printOrg %s > ./%s.json"%(orgId,orgId)

        os.system(comandLine)
        return jsonify({"success":True})