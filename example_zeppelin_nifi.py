
import paramiko

from data.services.zeppelin import startZeppelin, installZeppelin, \
    downloadTerpProps, \
    uploadTerpProps, \
    updateSparkWithStandardSettings

from data.webapp import clone_rawkintrevos_webapp_template, deploy_app

APP_PREFIX="no-gradle-1"

BLUEMIX_GIT_DIR="/home/rawkintrevo/gits/blue-mix/bi-git2"
SERVER = "bi-hadoop-prod-4162.bi.services.us-south.bluemix.net"
USERNAME = "guest"
PASSWORD = "password1234"

print "establishing ssh"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())
ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

print "installing zeppelin"
installZeppelin(ssh)

downloadTerpProps(ssh)
updateSparkWithStandardSettings()
uploadTerpProps(ssh)
startZeppelin(ssh)


clone_rawkintrevos_webapp_template()
deploy_app(8081, APP_PREFIX+"-zeppelin", SERVER, USERNAME, PASSWORD)
