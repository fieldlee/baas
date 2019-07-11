from flask_restful import Resource,reqparse
from flask import json,  jsonify
from . import Couchdb as db


parser = reqparse.RequestParser(trim=True)
parser.add_argument("domain")
parser.add_argument("orders",action='append',location=['json','args'],type=dict)
parser.add_argument("orgs",type=dict,action='append')


class Format(Resource):
    # method_decorators = [auth.login_required]
    def post(self):
        args = parser.parse_args()
        domain = args["domain"]

        orders = args["orders"]
        orgs = args["orgs"]

        apiIP = ""

        orderList = []
        i = 0
        tmpip = ""
        ipNum = 0
        for order in orders:
            if tmpip == "":
                tmpip = order["orderIp"]
                apiIP = order["orderIp"]
            tmpOrder = {}
            tmpOrder["orderName"] = "order%s"%i
            tmpOrder["orderId"] = "order%s"%i
            tmpOrder["orderIp"] = order["orderIp"]
            tmpOrder["orderPort"] = 7050 + ipNum * 1000
            tmpOrder["containerId"] = ("%s.%s"%(tmpOrder["orderId"],domain))
            orderList.append(tmpOrder)
            #计算ip重复的数量
            if tmpip == order["orderIp"]:
                ipNum += 1
            else:
                ipNum = 0
            i += 1

        # 计算共识方法
        consensus = "solo"
        if i > 1:
            consensus = "raft"

        orgList = []
        tmpOrgip = ""
        ipOrgNum = 0
        for org in orgs:
            tmpOrg = {}
            tmpOrg["orgName"] = org["orgId"]
            tmpOrg["orgId"]   = org["orgId"]
            tmpOrg["peerNumber"] = len(org["peers"])

            j = 0
            peerList = []
            for peer in org["peers"]:
                tmpPeer = {}

                if tmpOrgip == "":
                    tmpOrgip = peer["peerIp"]

                if j == 0 :
                    tmpOrg["anchorIp"] = peer["peerIp"]
                    tmpOrg["anchorPort"] = 7051 + 1000 *ipOrgNum
                    tmpOrg["caIp"] = peer["peerIp"]
                    tmpOrg["caPort"] = 7054 + 1000 *ipOrgNum
                    tmpOrg["caUser"] = "admin"
                    tmpOrg["caPwd"] = "adminpw"
                    tmpOrg["ContainerId"] = ("ca.%s.%s"%(tmpOrg["orgId"],domain))

                tmpPeer["peerIp"] = peer["peerIp"]
                tmpPeer["peerId"] = "peer%s"%j
                tmpPeer["postPort"] = 7051 + 1000 *ipOrgNum
                tmpPeer["eventPort"] = 7053 + 1000 *ipOrgNum
                tmpPeer["ContainerId"] = ("%s.%s.%s" % (tmpPeer["peerId"], tmpOrg["orgId"], domain))
                if "joinCouch" in peer:
                    if peer["joinCouch"] == True :
                        tmpPeer["joinCouch"] = True
                        tmpPeer["couchUsername"] = "couchadmin"
                        tmpPeer["couchPassword"] = "adminpwd"
                        tmpPeer["couchPort"] = 6984 + 1000*ipOrgNum
                        tmpPeer["CouchContainerId"] = ("couch.%s"%tmpPeer["ContainerId"])
                peerList.append(tmpPeer)
                #计算ipOrgNUm
                if tmpOrgip == peer["peerIp"]:
                    ipOrgNum += 1
                else:
                    ipOrgNum = 0

                j += 1
            tmpOrg["peers"] = peerList
            orgList.append(tmpOrg)

        try:
            db.save({"domain":domain,"consensus":consensus,"apiip":apiIP,"ordername":"order","orderid":"order","orders":orderList,"orgs":orgList})
        except:
            return jsonify({"success":False})

        return jsonify({"success":True})