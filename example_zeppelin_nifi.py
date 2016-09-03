

from data.services.zeppelin import ZeppelinServiceOnBI
from data.services.nifi import NiFiServiceOnBI

from data.webapp import clone_rawkintrevos_webapp_template, deploy_app

APP_PREFIX="my-app"

SERVER = "" # eg ""bi-hadoop-prod-4162.bi.services.us-south.bluemix.net"
USERNAME = "" # eg "user1"
PASSWORD = "" # eg "password1"

## For Notebook storage:
## https://zeppelin.apache.org/docs/0.5.5-incubating/storage/storage.html

S3_USERNAME = 'user'
S3_BUCKET = "bucekt"
AWS_ACCESS_KEY_ID="xxx"
AWS_SECRET_ACCESS_KEY="yyy"

clone_rawkintrevos_webapp_template()

zeppelin = ZeppelinServiceOnBI(SERVER, USERNAME, PASSWORD)
zeppelin.install()
zeppelin.start()
from time import sleep
sleep(5)
zeppelin.setS3auth(S3_USERNAME, S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
zeppelin.updateConifg()
zeppelin.deployApp(APP_PREFIX)
zeppelin.start()

n = NiFiServiceOnBI(SERVER, USERNAME, PASSWORD)
n.install()
n.uploadConfig()
n.start()
n.deployApp("tester-00001")


print "your app will be deployed to http://%s-zeppelin.mybluemix.net/" % APP_PREFIX
print "your app will be deployed to http://%s-nifi.mybluemix.net/" % APP_PREFIX



