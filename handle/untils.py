
import os

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
    toPath = os.path.join(curPath, "certification", docid)
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

    newline = line
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
    newline = newline.replace("-ProjectDIR-", toPath)
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

def GenerateConfigtx(doc):
    curPath = os.path.abspath(os.curdir)
    yamlDemo = os.path.join(curPath,"yaml","configtx_solo.yaml")
    toPath = os.path.join(curPath,"certification",doc["_id"])
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
