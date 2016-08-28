

from data.services.zeppelin import ZeppelinServiceOnBI
from data.services.mahout import MahoutServiceOnBI

from data.webapp import clone_rawkintrevos_webapp_template, deploy_app

APP_PREFIX="my-app"

SERVER = "" # eg ""bi-hadoop-prod-4162.bi.services.us-south.bluemix.net"
USERNAME = "" # eg "user1"
PASSWORD = "" # eg "password1"

## For Notebook storage:
## https://zeppelin.apache.org/docs/0.5.5-incubating/storage/storage.html

S3_USERNAME = 'user'
S3_BUCKET = "bucekt"

aws_keys = open("data/resources/rootkey.csv").readlines()
AWS_ACCESS_KEY_ID= aws_keys[0].split("=")[1].replace("\n", "").replace("\r", "")
AWS_SECRET_ACCESS_KEY=aws_keys[1].split("=")[1].replace("\n", "").replace("\r", "")

clone_rawkintrevos_webapp_template()

mahout = MahoutServiceOnBI(SERVER, USERNAME, PASSWORD)
mahout.install()

zeppelin = ZeppelinServiceOnBI(SERVER, USERNAME, PASSWORD)
zeppelin.install()
zeppelin.setS3auth(S3_USERNAME, S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
zeppelin.updateConifg()

mahout.updateSparkTerpWithMahoutDeps()
zeppelin._uploadTerpJson()

zeppelin.start()
zeppelin.deployApp(APP_PREFIX)
