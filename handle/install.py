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
        command="jq --version > /dev/null 2>&1" \
                "if [ $? -ne 0 ]; then" \
                "echo \"Please Install jq https://stedolan.github.io/jq/ to execute this script\"" \
                "exit 1" \
                "fi"
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
            loginShell += '%s_Token = $(curl - s - X POST http://localhost:4000/login -H "content-type:application/x-www-form-urlencoded"' \
                          ' -d username=%s&password=password&orgname=%s'%(org['orgId'],org['orgId'],org['orgId'])
            loginShell += '%s_TOKEN=$(echo $%s_TOKEN | jq ".token" | sed "s/\"//g")' \
                          ''%(org['orgId'],org['orgId'])


        channelTx = os.path.join('/var','certification',id,'%s.tx'%channelid)
        createChannel = "curl - s - X POST  http://localhost:4000/channels" \
                        "-H \"authorization: Bearer $%s_TOKEN\"" \
                        "-H \"content-type: application/json\"" \
                        "-d {\"channelName\":\"%s\",\"channelConfigPath\":\"%s\"}" \
                        ""%(defaultToken,channelid,channelTx)
        joinShell = ""

        installShell = ""
        for org in doc['orgs']:
            peerstr = ""
            for peer in org['peers']:
                if peerstr == "":
                    peerstr += peer['ContainerId']
                else:
                    peerstr += ",%s"%peer['ContainerId']

            joinShell += "curl -s -X POST http://localhost:4000/channels/peers" \
                         "-H \"authorization: Bearer $%s_TOKEN\"" \
                         "-H \"content-type: application/json\"" \
                         "-d '{\"peers\": [%s],\"channelName\":\"%s\"}'" \
                         ""%(org["orgId"],peerstr,channelid)


        for org in doc['orgs']:
            peerstr = ""
            for peer in org['peers']:
                if peerstr == "":
                    peerstr += peer['ContainerId']
                else:
                    peerstr += ",%s"%peer['ContainerId']

            installShell += "curl -s -X POST http://localhost:4000/chaincodes" \
                            "-H \"authorization: Bearer $%s_TOKEN\"" \
                            "-H \"content-type: application/json\"" \
                            "-d {\"peers\": [%s],\"channelName\": \"%s\",\"chaincodeName\": \"%s\"," \
                            "\"chaincodePath\": \"%s\",\"chaincodeVersion\": \"%s\"}" \
                            ""%(org["orgId"],peerstr,channelid,ccname,ccpath,ccversion)


        instantiateChainCode = "curl -s -X POST http://localhost:4000/channels/chaincodes" \
                               "-H \"authorization: Bearer $%s_TOKEN\"" \
                               "-H \"content-type: application/json\"" \
                               "-d {\"channelName\": \"%s\",\"chaincodeName\": \"%s\",\"chaincodeVersion\": \"%s\"," \
                               "\"args\": []}" \
                               ""%(defaultToken,channelid,ccname,ccversion)

        upgradeChainCode = "curl -s -X PUT http://localhost:4000/channels/chaincodes" \
                               "-H \"authorization: Bearer $%s_TOKEN\"" \
                               "-H \"content-type: application/json\"" \
                               "-d {\"channelName\": \"%s\",\"chaincodeName\": \"%s\",\"chaincodeVersion\": \"%s\"," \
                               "\"args\": []}" \
                           "" % (defaultToken, channelid, ccname, ccversion)
        install = ""
        upgrade = ""
        if type == "install":
            install = "%s %s %s %s %s "%(loginShell,createChannel,joinShell,installShell,instantiateChainCode)
            return install
        else:
            upgrade = "%s %s %s %s %s "%(loginShell,installShell,upgradeChainCode)
            return  upgrade
