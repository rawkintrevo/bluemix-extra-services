
from time import sleep

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

clone_rawkintrevos_webapp_template()

m = MahoutServiceOnBI(SERVER, USERNAME, PASSWORD)
m.install()

z = ZeppelinServiceOnBI(SERVER, USERNAME, PASSWORD)
z.install()
z.start()
sleep(5)
z.downloadConfig({"interpreter.json"  : "conf/interpreter.json"})
z.updateConfig()
## Add your own dependencies if you want them always there...
#z._addTerpDep("spark", "com.databricks:spark-csv_2.10:1.4.0")
new_terp_name = "mahoutSpark"
z.createTerp(new_terp_name, "spark")
z.addMahoutConfig(new_terp_name)

z.setS3auth(S3_USERNAME, S3_BUCKET)
z._writeTerpJson()
z.uploadConfig()
z.start()
z.deployApp(APP_PREFIX)

print "your app will be deployed to http://%s-zeppelin.mybluemix.net/" % APP_PREFIX
