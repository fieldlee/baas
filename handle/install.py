#!/usr/bin/python
#coding:utf-8

import os
from flask_restful import Resource,reqparse
from . import Couchdb,db


parser = reqparse.RequestParser(trim=True)
parser.add_argument("id")
parser.add_argument("channel")
parser.add_argument("ccname")
parser.add_argument("ccversion")
parser.add_argument("ccpath")
parser.add_argument("type")

class Install(Resource):
    def post(self):
        command="#!/bin/bash \n" \
                "jq --version > /dev/null 2>&1\n" \
                "if [ $? -ne 0 ]; then\n" \
                "   echo \"Please Install jq https://stedolan.github.io/jq/ to execute this script\"\n" \
                "   exit 1\n" \
                "fi\n"
        #command 打印
        print(command)
        args = parser.parse_args()
        id = args["id"]
        channelid = args["channel"]
        ccname = args["ccname"]
        ccversion = args["ccversion"]
        ccpath = args["ccpath"]
        type = args["type"]

        doc = db.QueryById(Couchdb, id)

        loginShell = ""
        defaultToken = ""
        for org in doc['orgs']:
            if defaultToken == "":
                defaultToken = org['orgId']
            loginShell += '%s_Token=$(curl - s - X POST http://localhost:4000/login  -H "content-type:application/x-www-form-urlencoded"' \
                          ' -d username=%s&password=password&orgname=%s)\n'%(org['orgId'],org['orgId'],org['orgId'])
            loginShell += '%s_TOKEN=$(echo $%s_TOKEN | jq ".token" | sed "s/\\"//g")' \
                          '\n'%(org['orgId'],org['orgId'])
            #打印login
            print(loginShell)

        channelTx = os.path.join('/var','certification',id,'%s.tx'%channelid)
        createChannel = "curl - s - X POST  http://localhost:4000/channels" \
                        " -H \"authorization: Bearer $%s_TOKEN\"" \
                        " -H \"content-type: application/json\"" \
                        " -d '{\"channelName\":\"%s\",\"channelConfigPath\":\"%s\"}'" \
                        "\n"%(defaultToken,channelid,channelTx)
        print(createChannel)

        joinShell = ""

        installShell = ""
        for org in doc['orgs']:
            peerstr = ""
            for peer in org['peers']:
                if peerstr == "":
                    peerstr += "\"%s\""%peer['ContainerId']
                else:
                    peerstr += ",\"%s\""%peer['ContainerId']

            joinShell += "curl -s -X POST http://localhost:4000/channels/peers" \
                         " -H \"authorization: Bearer $%s_TOKEN\"" \
                         " -H \"content-type: application/json\"" \
                         " -d '{\"peers\": [%s],\"channelName\":\"%s\"}'" \
                         "\n"%(org["orgId"],peerstr,channelid)
            print(joinShell)


        for org in doc['orgs']:
            peerstr = ""
            for peer in org['peers']:
                if peerstr == "":
                    peerstr += "\"%s\""%peer['ContainerId']
                else:
                    peerstr += ",\"%s\""%peer['ContainerId']

            installShell += "curl -s -X POST http://localhost:4000/chaincodes" \
                            " -H \"authorization: Bearer $%s_TOKEN\"" \
                            " -H \"content-type: application/json\"" \
                            " -d '{\"peers\": [%s],\"channelName\": \"%s\",\"chaincodeName\": \"%s\"," \
                            "\"chaincodePath\": \"%s\",\"chaincodeVersion\": \"%s\"}'" \
                            "\n"%(org["orgId"],peerstr,channelid,ccname,ccpath,ccversion)
            print(installShell)


        instantiateChainCode = "curl -s -X POST http://localhost:4000/channels/chaincodes" \
                               " -H \"authorization: Bearer $%s_TOKEN\"" \
                               " -H \"content-type: application/json\"" \
                               " -d '{\"channelName\": \"%s\",\"chaincodeName\": \"%s\",\"chaincodeVersion\": \"%s\"," \
                               "\"args\": []}'" \
                               "\n"%(defaultToken,channelid,ccname,ccversion)
        print(instantiateChainCode)

        upgradeChainCode = "curl -s -X PUT http://localhost:4000/channels/chaincodes" \
                               " -H \"authorization: Bearer $%s_TOKEN\"" \
                               " -H \"content-type: application/json\"" \
                               " -d '{\"channelName\": \"%s\",\"chaincodeName\": \"%s\",\"chaincodeVersion\": \"%s\"," \
                               "\"args\": []}'" \
                           "\n" % (defaultToken, channelid, ccname, ccversion)
        install = ""
        upgrade = ""

        curPath = os.path.abspath(os.curdir)
        shellPath = os.path.join(curPath, "certification",id,'install.sh')
        updatePath = os.path.join(curPath, "certification", id, 'update.sh')
        if type == "install":
            install = "%s %s %s %s %s %s "%(command,loginShell,createChannel,joinShell,installShell,instantiateChainCode)
            with open(shellPath,'w') as file:
                file.write(install)
            return install
        else:
            upgrade = "%s %s %s %s "%(command,loginShell,installShell,upgradeChainCode)
            with open(updatePath,'w') as file:
                file.write(upgrade)
            return  upgrade
