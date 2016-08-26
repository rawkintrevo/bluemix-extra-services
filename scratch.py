import paramiko  # v 2.0.2

from data.services.zeppelin import startZeppelin, installZeppelin, downloadTerpProps, uploadTerpProps, updateSparkWithStandardSettings
#from data.services.kafka import *
from data.services.mahout import installMahout, updateSparkTerpWithMahoutDeps
from data.webapp import deploy_app

APP_PREFIX="no-gradle-1"
#BLUEMIX_GIT_DIR="/home/rawkintrevo/gits/blue-mix/bi-git2"
SERVER = "bi-hadoop-prod-4162.bi.services.us-south.bluemix.net"
USERNAME = "guest"
PASSWORD = "password1234"

ZEPPELIN_DIR="/home/rawkintrevo/gits/blue-mix/bi-git2/examples/Zeppelin"
NIFI_DIR= "/home/rawkintrevo/gits/blue-mix/bi-git2/examples/NiFi"
NIFI_DIR= "/home/rawkintrevo/gits/blue-mix/bi-git2/examples/Kafka"

## These could be inferred from config files
ZEPPELIN_BI_PORT= 8081
NIFI_BI_PORT=8084

connection_conf = {
    "gateway"   : "https://" + SERVER + ":8443/gateway/default",
    "username"  : USERNAME,
    "password"  : PASSWORD,
    "ambariUrl" : "https://" + SERVER +  ":9443/api",
    "ambariUsername" : USERNAME,
    "ambariPassword" : PASSWORD,
    "known_hosts":"allowAnyHosts"
}


#######################################################################################################################
# Configure for new Cluster
#######################################################################################################################

print "establishing ssh"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())
ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

## For Gradle
# with open(BLUEMIX_GIT_DIR + "/connection.properties", 'wb') as f:
#     for k,v in connection_conf.iteritems():
#         f.write(k + ":" + v + "\n")
# call(["./gradlew", "DownloadCertificate"], cwd=BLUEMIX_GIT_DIR)
# call(["./gradlew", "DownloadLibs"], cwd=BLUEMIX_GIT_DIR)

print "installing mahout"
installMahout(ssh)
print "installing zeppelin"
installZeppelin(ssh)

downloadTerpProps(ssh)
updateSparkWithStandardSettings()
updateSparkTerpWithMahoutDeps()
uploadTerpProps(ssh)

#
#
# ## Setup and Run Zeppelin

#call(["./gradlew", "Install"], cwd=NIFI_DIR)


## Create Webapp front ends
#clone_rawkintrevos_webapp_template()

#updateConfigs(ssh)
startZeppelin(ssh)
deploy_app(8081, APP_PREFIX+"-zeppelin", SERVER, USERNAME, PASSWORD)

# startNiFi(ssh)
# deploy_app(NIFI_BI_PORT, APP_PREFIX+"-nifi", SERVER, USERNAME, PASSWORD)

#installKafka(ssh); startKafka(ssh)

from data.services.flink import FlinkServiceOnBI

APP_PREFIX="no-gradle-1"
#BLUEMIX_GIT_DIR="/home/rawkintrevo/gits/blue-mix/bi-git2"
SERVER = "bi-hadoop-prod-4172.bi.services.us-south.bluemix.net"
USERNAME = "guest"
PASSWORD = "password1234"


flink = FlinkServiceOnBI(SERVER, USERNAME, PASSWORD)

flink.install()
flink.updateConfig()
flink.start()
flink.deployApp("flinktester1")

