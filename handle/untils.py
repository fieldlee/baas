
import os
import json

def CreateDir(path):
    if not os.path.exists(path):
        os.mkdir(path,mode=0o777)

def CreateFile(path):
    if not os.path.exists(path):
        os.mknod(path,mode=0o777)

def ReplaceYaml(line,doc):
    newline = line

    # replace list
    #-OrderIDForReplace-
    #-ProjectDIR-
    #-DomainForReplace-

    orderid = doc["orderid"]
    ordername = doc["ordername"]
    domain = doc["domain"]
    curPath = os.path.abspath(os.curdir)
    toPath = os.path.join(curPath, "certification", doc["_id"])

    if "##List-Start" in line:
        listline = ""
        print(line)
        for org in doc["orgs"]:
            newline = line
            newline = newline.replace("-OrgIDForReplace-",org["orgId"])
            newline = newline.replace("-AnchorIpForReplace-", org["anchorIp"])
            newline = newline.replace("-AnchorPortForReplace-", str(org["anchorPort"]))
            newline = newline.replace("-ProjectDIR-", toPath)
            newline = newline.replace("-DomainForReplace-", domain)
            listline += newline

        return listline
    #-OrderIDForReplace-.-DomainForReplace-:-OrderPortForReplace-
    if "##OrderList-Start" in line:
        orderline = ""
        for order in doc["orders"]:
            newline = line
            newline = newline.replace("-OrderIDForReplace-", order["orderId"])
            newline = newline.replace("-OrderPortForReplace-", str(order["orderPort"]))
            newline = newline.replace("-ProjectDIR-", toPath)
            newline = newline.replace("-DomainForReplace-", domain)
            orderline += newline
        return orderline

    newline = newline.replace("-OrderNameForReplace-", ordername)
    newline = newline.replace("-OrderIDForReplace-",orderid)
    newline = newline.replace("-ProjectDIR-",toPath)
    newline = newline.replace("-DomainForReplace-", domain)

    return newline

def ReplaceOrderYaml(line,order,domain,docid):
    newline = line

    curPath = os.path.abspath(os.curdir)
    toPath = os.path.join('/var', "certification", docid)
    # -OrderIDForReplace-
    # -OrderPortForReplace-
    newline = newline.replace("-ContainerIdForReplace-", order["containerId"])
    newline = newline.replace("-ProjectDIR-", toPath)
    newline = newline.replace("-DomainForReplace-", domain)
    newline = newline.replace("-OrderIDForReplace-", order["orderId"])
    newline = newline.replace("-OrderPortForReplace-", str(order["orderPort"]))
    return newline

def ReplacePeerYaml(line,peer,org,doc):

    domain = doc["domain"]
    curPath = os.path.abspath(os.curdir)
    toPath = os.path.join(curPath, "certification", doc["_id"])
    projectPath = os.path.join('/var', "certification", doc["_id"])
    newline = line
    #
    newline = newline.replace("-NetWorkForReplace-",doc["_id"])
    #-ContainerIdForReplace-
    newline = newline.replace("-ContainerIdForReplace-", peer["ContainerId"])
    #-OrgIDForReplace-
    newline = newline.replace("-OrgIDForReplace-", org["orgId"])
    # -PeerPortForReplace-
    newline = newline.replace("-PeerPortForReplace-", str(peer["postPort"]))
    # -PeerEventPortForReplace-
    newline = newline.replace("-PeerEventPortForReplace-", str(peer["eventPort"]))
    if "joinCouch" in peer :
        #-CouchUserForReplace-
        newline = newline.replace("-CouchUserForReplace-", peer["couchUsername"])
        #-CouchPasswordForReplace-
        newline = newline.replace("-CouchPasswordForReplace-", peer["couchPassword"])
        # -CouchContainerIdForReplace-
        newline = newline.replace("-CouchContainerIdForReplace-", peer["CouchContainerId"])
    else:
        if "##COUCH_Start" in line:
            return ""

    # -OrgIDForReplace-.-DomainForReplace -
    newline = newline.replace("-OrgIDForReplace-", org["orgId"])
    newline = newline.replace("-DomainForReplace-", domain)
    #-ProjectDIR-
    newline = newline.replace("-ProjectDIR-", projectPath)
    # -PeerIDForReplace-
    newline = newline.replace("-PeerIDForReplace-", peer["peerId"])

    if "##OrderExtra_Start" in line:
        peerip = peer["peerIp"]
        orderips = []
        hasExtra = False
        for order in doc["orders"]:
            if peerip != order["orderIp"]:
                hasExtra = True

        if hasExtra == True:
            orderLIne = "    extra_hosts:\n"
            for order in doc["orders"]:
                if peerip != order["orderIp"]:
                    tmpOrderLIen = "%s:%s"%(order["containerId"],order["orderIp"])
                    orderLIne += "      - %s\n"%tmpOrderLIen
            return orderLIne
        else:
            return ""


    if "##DependOn_Start" in line:
        hasDepend = False
        if "joinCouch" in peer:
            hasDepend = True

        dependLIne = "    depends_on:\n"
        peerip = peer["peerIp"]
        for order in doc["orders"]:
            if peerip == order["orderIp"]:
                dependLIne += "      - %s\n" % order["containerId"]

        if "joinCouch" in peer:
            dependLIne += "      - %s\n" % peer["CouchContainerId"]
        return dependLIne

    return newline

def ReplaceCouch(line,peer,org,doc):
    newline = line
    curPath = os.path.abspath(os.curdir)
    toPath = os.path.join(curPath, "certification", doc["_id"])
    # -ContainerIdForReplace-
    # -CouchUserForReplace-
    # -CouchPasswordForReplace-
    # -CouchPortForReplace-
    newline = newline.replace("-ContainerIdForReplace-", peer["CouchContainerId"])
    newline = newline.replace("-CouchUserForReplace-", peer["couchUsername"])
    newline = newline.replace("-CouchPasswordForReplace-", peer["couchPassword"])
    newline = newline.replace("-CouchPortForReplace-", str(peer["couchPort"]))
    return newline

def ReplaceCa(line,org,doc):
    newline = line
    curPath = os.path.abspath(os.curdir)
    toPath = os.path.join(curPath, "certification", doc["_id"])
    projectPath = os.path.join('/var', "certification", doc["_id"])
    # -ContainerIdForReplace-
    # -OrgCAIDForReplace-
    # -OrgIDForReplace-
    # -DomainForReplace-
    # -CAPEMFILENAMEForReplace-
    # -OrgCAPortForReplace-
    # -CAPATHForReplace-
    newline = newline.replace("-ContainerIdForReplace-", org["ContainerId"])
    newline = newline.replace("-OrgCAIDForReplace-", "ca")
    newline = newline.replace("-OrgCAPortForReplace-", str(org["caPort"]))
    newline = newline.replace("-OrgIDForReplace-", org["orgId"])
    newline = newline.replace("-DomainForReplace-", doc["domain"])

    caCertFilePath = os.path.join(toPath,"crypto-config","peerOrganizations","%s.%s"%(org["orgId"],doc["domain"]),"ca")

    files = os.listdir(caCertFilePath)

    caSkPath = ""
    for file in files:
        if "_sk" in file:
            caSkPath = file

    caCertFilePath = caCertFilePath.replace(curPath,'/var')
    newline = newline.replace("-CAPATHForReplace-", caCertFilePath)
    newline = newline.replace("-CAPEMFILENAMEForReplace-", caSkPath)


    return newline

def GenerateConfigtx(doc):
    curPath = os.path.abspath(os.curdir)
    yamlDemo = os.path.join(curPath,"yaml","configtx_solo.yaml")
    toPath = os.path.join(curPath,"certification",doc["_id"])
    projectPath = os.path.join('/var', "certification", doc["_id"])
    toYamlPath = os.path.join(toPath,"configtx.yaml")
    if doc["consensus"] == "raft":
        yamlDemo = os.path.join(curPath, "yaml", "configtx_raft.yaml")

    file = open(yamlDemo, 'r')
    # 创建yaml文件
    CreateFile(toYamlPath)

    hasWait = False
    forRplLine = ""
    with open(toYamlPath,'w') as tofile:
        try:
            while True:
                text_line = file.readline()
                if text_line:
                    # 如果是list 一直等待end to replace
                    if ("##List-Start" in text_line) or ("##OrderList-Start" in text_line):
                        hasWait = True
                    # 如果不是list 直接调用replace
                    if not hasWait:
                        tofile.write(ReplaceYaml(text_line,doc))
                        continue

                    if hasWait == True:
                        forRplLine += text_line

                    if ("##List-End" in text_line) or ("##OrderList-End" in text_line):
                        hasWait = False

                    if not hasWait :
                        tofile.write(ReplaceYaml(forRplLine,doc))
                        forRplLine=""

                else:
                    break
        finally:
            file.close()

def GenerateCrypto(doc):
    curPath = os.path.abspath(os.curdir)
    yamlDemo = os.path.join(curPath, "yaml", "cryptogen.yaml")
    toPath = os.path.join(curPath, "certification", doc["_id"])
    toYamlPath = os.path.join(toPath, "cryptogen.yaml")

    file = open(yamlDemo, 'r')
    # 创建yaml文件
    CreateFile(toYamlPath)

    hasWait = False
    forRplLine = ""
    with open(toYamlPath, 'w') as tofile:
        try:
            while True:
                text_line = file.readline()
                if text_line:
                    # 如果是list 一直等待end to replace
                    if ("##List-Start" in text_line) or ("##OrderList-Start" in text_line):
                        hasWait = True
                    # 如果不是list 直接调用replace
                    if not hasWait:
                        tofile.write(ReplaceYaml(text_line, doc))
                        continue

                    if hasWait == True:
                        forRplLine += text_line

                    if ("##List-End" in text_line) or ("##OrderList-End" in text_line):
                        hasWait = False

                    if not hasWait:
                        tofile.write(ReplaceYaml(forRplLine, doc))
                        forRplLine = ""

                else:
                    break
        finally:
            file.close()

def GenerateOrder(doc):
    curPath = os.path.abspath(os.curdir)
    yamlDemo = os.path.join(curPath, "yaml", "order_demo.yaml")
    toPath = os.path.join(curPath, "certification", doc["_id"])

    # 生成order yaml文件
    for order in doc["orders"]:
        toYamlPath = os.path.join(toPath, "order_%s.yaml"%order["orderId"])
        # 创建yaml文件
        CreateFile(toYamlPath)

        file = open(yamlDemo, 'r')

        with open(toYamlPath, 'w') as tofile:
            try:
                while True:
                    text_line = file.readline()
                    if text_line:
                        tofile.write(ReplaceOrderYaml(text_line, order,doc["domain"],doc["_id"]))
                    else:
                        break
            finally:
                file.close()

def GeneratePeer(doc):
    curPath = os.path.abspath(os.curdir)
    yamlDemo = os.path.join(curPath, "yaml", "peer_demo.yaml")
    toPath = os.path.join(curPath, "certification", doc["_id"])
    # peer yaml文件
    hasWait = False
    forRplLine = ""
    for org in doc["orgs"]:
        for peer in org["peers"]:

            toYamlPath = os.path.join(toPath, "%s_%s.yaml" % (peer["peerId"],org["orgId"]))
            # 创建yaml文件
            CreateFile(toYamlPath)

            file = open(yamlDemo, 'r')

            with open(toYamlPath, 'w') as tofile:
                try:
                    while True:
                        text_line = file.readline()
                        if text_line:
                            # 如果是list 一直等待end to replace
                            if ("##COUCH_Start" in text_line) or ("##OrderExtra_Start" in text_line) or ("##DependOn_Start" in text_line):
                                hasWait = True
                            # 如果不是list 直接调用replace
                            if not hasWait:
                                tofile.write(ReplacePeerYaml(text_line, peer,org,doc))
                                continue

                            if hasWait == True:
                                forRplLine += text_line

                            if ("##COUCH_End" in text_line) or ("##OrderExtra_End" in text_line) or ("##DependOn_End" in text_line):
                                hasWait = False

                            if not hasWait:
                                tofile.write(ReplacePeerYaml(forRplLine, peer,org,doc))
                                forRplLine = ""

                        else:
                            break
                finally:
                    file.close()

def GenerateCouch(doc):
    curPath = os.path.abspath(os.curdir)
    yamlDemo = os.path.join(curPath, "yaml", "couch_demo.yaml")
    toPath = os.path.join(curPath, "certification", doc["_id"])

    # 生成order yaml文件
    for org in doc["orgs"]:
        for peer in org["peers"]:
            if "joinCouch" in peer :
                toYamlPath = os.path.join(toPath, "couch_%s_%s.yaml" % (peer["peerId"],org["orgId"]))
                # 创建yaml文件
                CreateFile(toYamlPath)

                file = open(yamlDemo, 'r')

                with open(toYamlPath, 'w') as tofile:
                    try:
                        while True:
                            text_line = file.readline()
                            if text_line:
                                tofile.write(ReplaceCouch(text_line, peer, org, doc))
                            else:
                                break
                    finally:
                        file.close()

def GenerateCa(doc):
    curPath = os.path.abspath(os.curdir)
    yamlDemo = os.path.join(curPath, "yaml", "ca_demo.yaml")
    toPath = os.path.join(curPath, "certification", doc["_id"])

    # 生成order yaml文件
    for org in doc["orgs"]:
        toYamlPath = os.path.join(toPath, "ca_%s.yaml" % (org["orgId"]))
        # 创建yaml文件
        CreateFile(toYamlPath)
        file = open(yamlDemo, 'r')
        with open(toYamlPath, 'w') as tofile:
            try:
                while True:
                    text_line = file.readline()
                    if text_line:
                        tofile.write(ReplaceCa(text_line, org, doc))
                    else:
                        break
            finally:
                file.close()

def GenerateCert(doc):

    curPath = os.path.abspath(os.curdir)
    toPath = os.path.join(curPath, "certification", doc["_id"])
    configPath = os.path.join(curPath, "certification", doc["_id"],"crypto-config")
    #创建目录
    CreateDir(configPath)
    #crypto-config
    #export FABRIC_CFG_PATH=$PWD
    #../cryptogen generate --config=./cryptogen.yaml
    #../configtxgen -profile ProjectOrgsOrdererGenesis -outputBlock ./genesis.block
    #../configtxgen -profile SampleMultiNodeEtcdRaft -outputBlock ./genesis.block
    #; ../configtxgen -profile ProjectOrgsChannel -outputCreateChannelTx ./.tx", " -channelID
    commandLine = "cd %s; export FABRIC_CFG_PATH=$PWD;../cryptogen generate --config=./cryptogen.yaml;"%toPath
    if doc["consensus"] == "raft":
        commandLine += "../configtxgen -profile SampleMultiNodeEtcdRaft -outputBlock ./genesis.block;"
    elif doc["consensus"] == "solo":
        commandLine += "../configtxgen -profile ProjectOrgsOrdererGenesis -outputBlock ./genesis.block;"
    else:
        commandLine += "../configtxgen -profile ProjectOrgsOrdererGenesis -outputBlock ./genesis.block;"

    # commandLine += "../configtxgen -profile ProjectOrgsChannel -outputCreateChannelTx ./%s.tx -channelID %s;"%(channelid,channelid)
    # print(commandLine)
    os.system(commandLine)

def Tar(doc):
    curPath = os.path.abspath(os.curdir)
    rootPath = os.path.join(curPath, "certification")
    gizShell = "cd %s; tar -cvf %s.tar ./%s ;"%(rootPath,doc["_id"],doc["_id"])
    os.system(gizShell)

def GenerateApiJson(doc):
    print(doc["_id"])
    ProPath = os.path.join("/var","certification",doc["_id"])

    Json = {}
    Json["host"]="localhost"
    Json["port"] = "4000"
    Json["curOrgId"] = ""
    Json["orderId"] = doc["orderid"]
    Json["consensus"] = doc["consensus"]
    Json["caUser"] = "admin"
    Json["caSecret"] = "adminpw"
    Json["CC_SRC_PATH"] = os.path.join(ProPath,"cc")
    Json["caUser"] = "admin"
    Json["eventWaitTime"] = "100000"
    Json["expireTime"] = "360000"
    Json["jwt_expiretime"] = "360000"
    Json["keyValueStore"] = "/var/fabric-client-kvs"

    # network-config
    tmpConfig = {}
    for org in doc["orgs"]:

        tmpLIne = "{\"client\":{\"credentialStore\":{\"cryptoStore\":{\"path\":\"/var/fabric-client-kvs_%s\"}," \
                  "\"path\":\"/var/fabric-client-kvs_%s\"}," \
                  "\"organization\":\"%s\"},\"version\":\"1.0\"}"%(org["orgId"],org["orgId"],org["orgId"])
        tmpConfig[org["orgId"]] = json.loads(tmpLIne)

    Json["network-config"] = tmpConfig




    tmpProfile = {}

    # channel
    tmpChan = {}
    chanmap = {}
    for chan in doc["channel"]:
        tmpOrderList = []
        for order in doc["orders"]:
            tmpOrderList.append(order["containerId"])

        tmpChan["orderers"] = tmpOrderList


        tmpPeerMap = {}
        for org in doc["orgs"]:
            for peer in org["peers"]:
                if "peer0" in peer["peerId"]:
                    tmpPeerMap[peer["ContainerId"]] = {"chaincodeQuery": True,"endorsingPeer":True,"eventSource":True,"ledgerQuery":True}
                else:
                    tmpPeerMap[peer["ContainerId"]] = {"chaincodeQuery": True, "endorsingPeer": False,"eventSource": False, "ledgerQuery": True}
        tmpChan["peers"] = tmpPeerMap
        chanmap[chan["channelid"]] = tmpChan

    # channels 赋值
    tmpProfile["channels"] = chanmap

    # certificateAuthorities
    tmpCert = {}
    for org in doc["orgs"]:
        tmpLIne = "{\"caName\":\"%s\",\"httpOptions\":{\"verify\":false},\"registrar\":[" \
                  "{\"enrollId\":\"%s\",\"enrollSecret\":\"%s\"}],\"tlsCACerts\":" \
                  "{\"path\":\"/var/certification/%s/crypto-config/peerOrganizations/%s.%s/ca/ca.%s.%s-cert.pem\"}," \
                  "\"url\":\"https://%s:%s\"}"%(org["ContainerId"],org["caUser"],org["caPwd"],doc["_id"],org["orgId"],doc["domain"],org["orgId"],doc["domain"],org["caIp"],str(org["caPort"]))

        tmpCert[org["ContainerId"]] = json.loads(tmpLIne)

    tmpProfile["certificateAuthorities"] = tmpCert
    #orders

    tmpOrder = {}
    for order in doc["orders"]:
        tmpLIne = "{\"grpcOptions\":{\"ssl-target-name-override\":\"%s\"}," \
                  "\"tlsCACerts\":{\"path\":\"/var/certification/%s/crypto-config/ordererOrganizations/%s/orderers/%s/tls/ca.crt\"}," \
                  "\"url\":\"grpcs://%s:%s\"}"%(order["containerId"],doc["_id"],doc["domain"],order["containerId"],order["orderIp"],str(order["orderPort"]))

        tmpOrder[order["containerId"]] = json.loads(tmpLIne)

    tmpProfile["orderers"] = tmpOrder
    #peers
    tmpPeers = {}
    for org in doc["orgs"]:
        for peer in org["peers"]:
            tmpLIne = "{\"eventUrl\":\"grpcs://%s:%s\",\"grpcOptions\":{\"ssl-target-name-override\":" \
                      "\"%s\"},\"tlsCACerts\":{\"path\":\"/var/certification/%s/crypto-config/peerOrganizations/%s.%s/peers/%s/tls/ca.crt\"}," \
                      "\"url\":\"grpcs://%s:%s\"}"%(peer["peerIp"],str(peer["eventPort"]),peer["ContainerId"],doc["_id"],org["orgId"],doc["domain"],peer["ContainerId"],peer["peerIp"],str(peer["postPort"]))
            tmpPeers[peer["ContainerId"]] = json.loads(tmpLIne)

    tmpProfile["peers"] = tmpPeers

    #orgnzation
    tmpOrgs = {}
    curPath = os.path.abspath(os.curdir)
    toPath = os.path.join(curPath, "certification", doc["_id"])
    for org in doc["orgs"]:

        caCertFilePath = os.path.join(toPath, "crypto-config", "peerOrganizations","%s.%s" % (org["orgId"], doc["domain"]), "users","Admin@%s.%s"%(org["orgId"],doc["domain"]),"msp","keystore")

        files = os.listdir(caCertFilePath)

        caSkfile = ""
        for file in files:
            if "_sk" in file:
                caSkfile = file

        comLIne = "%s.%s"%(org["orgId"],doc["domain"])
        peer0 = "peer0.%s"%comLIne
        peer1 = "peer1.%s"%comLIne
        tmpLIne = "{\"adminPrivateKey\":{\"path\":\"/var/certification/%s/crypto-config/peerOrganizations/%s/users/Admin@%s/msp/keystore/%s\"}," \
                  "\"certificateAuthorities\":" \
                  "[\"%s\"],\"mspid\":\"%s\",\"peers\":[\"%s\",\"%s\"]," \
                  "\"signedCert\":" \
                  "{\"path\":\"/var/certification/%s/crypto-config/peerOrganizations/%s/users/Admin@%s/msp/signcerts/Admin@%s-cert.pem\"}}"%(doc["_id"],comLIne,comLIne,caSkfile,org["ContainerId"],org["orgId"],peer0,peer1,doc["_id"],comLIne,comLIne,comLIne)

        tmpOrgs[org["orgId"]] = json.loads(tmpLIne)

    tmpProfile["organizations"] = tmpOrgs
    tmpProfile["version"] = "1.0"
    Json["connect_profile"] = tmpProfile

    curPath = os.path.abspath(os.curdir)
    toPath = os.path.join(curPath, "certification", doc["_id"])
    # 保持json config文件
    jsonFile = os.path.join(toPath,"config.json")
    with open(jsonFile,'w') as jFile:
        jFile.write(json.dumps(Json))


def RemoveFloder(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))

        for name in dirs:
            os.rmdir(os.path.join(root, name))

        os.rmdir(root)

