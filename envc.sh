#!/bin/bash
# 安装 脚本 系统环境要求 1.Ubuntu 16.06 2.Centos 7
sysVer=`cat /proc/version`
echo $sysVer
rootPath=`pwd`
function installCentos()
{
    #yum update -y
    softs=(vim telnet go docker epel-release python-pip git unzip zip jq)
    for soft in ${softs[@]} ; do
       echo "install ${soft}"
       installed=`yum list installed | grep ${soft}`
       sudo yum install -y $soft
    done
     sudo curl --silent --location https://rpm.nodesource.com/setup_9.x | bash -
     sudo yum install -y nodejs
     sudo yum install -y gcc-c++
     sudo npm install -g pm2
     sudo yum install -y epel-release
     sudo yum install -y python-pip
     sudo pip install docker-compose
     sudo yum install -y git;
     sudo yum install -y jq;
     echo "防火墙"
     sudo firewall-cmd --zone=public --add-port=1081/tcp --permanent
     sudo firewall-cmd --zone=public --add-port=1082/tcp --permanent
     sudo firewall-cmd --reload
}
function installUbuntu()
{
    #apt-get update -y
    softs=(vim telnet go docker unzip zip jq)
    for soft in ${softs[@]} ; do
        echo "install ${soft}"
        sudo apt-get install -g $soft
    done
    echo "安装node 9"
    sudo sh ./env/node.sh
    sudo apt-get install docker.io -y
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    sudo apt-get install -y nodejs
    sudo apt-get install -y python-pip
    sudo apt-get install build-essential
    sudo npm install -g pm2
    echo "安装pm2"
    sudo apt-get install -y git
    sudo apt-get install -y jq
    echo "安装docker-compose"
    sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo ufw allow 1081/tcp
    sudo ufw allow 1082/tcp
    sudo ufw reload
}
if [[ $sysVer == *"centos"* ]];then
    echo "centos"
    installCentos
elif [[ $sysVer == *"Ubuntu"* ]];then
    echo "ubuntu"
    installUbuntu
else
    echo "目前支持centos7.0及以上或者Ubuntu系统"
    exit
fi

echo "启动docker"
sudo systemctl daemon-reload
sudo systemctl start docker

configFile="/etc/hlcbaas/online.json"

if [ ! -f "/etc/hlcbaas" ];then
    echo "创建/etc/hlcbaas目录"
    sudo mkdir -p "/etc/hlcbaas"
else
    echo "已存在目录"
fi

echo "安装docker images"
# install images
sudo chmod a+x ./env/get-images.sh
sudo env/get-images.sh
sudo chmod a+x ./env/set-images-latest.sh
sudo env/set-images-latest.sh

# curl -sSL http://bit.ly/2ysbOFE | bash -s -- 1.4.1 1.4.1 0.4.15

