from time import sleep

from data.services.zeppelin import ZeppelinServiceOnBI
from data.services.mahout import MahoutServiceOnBI



APP_PREFIX="" # anything you want- but must be unique

## Last Init: 9/29/2016 @ 8:56 AM
SERVER = "" # eg ""bi-hadoop-prod-4162.bi.services.us-south.bluemix.net"
USERNAME = "" # eg "user1"
PASSWORD = "" # eg "password1"

## For Notebook storage:
## https://zeppelin.apache.org/docs/0.5.5-incubating/storage/storage.html

#S3_USERNAME = 'rawkintrevo'
#S3_BUCKET = "rawkintrevos-notebooks"

m = MahoutServiceOnBI(SERVER, USERNAME, PASSWORD)
m.install()
m.uploadConfig()

z = ZeppelinServiceOnBI(SERVER, USERNAME, PASSWORD)
z.install()
z.setS3auth(S3_USERNAME, S3_BUCKET) ## Must do this prior to z.start

z.start()
sleep(5)
z.downloadConfig({"interpreter.json"  : "conf/interpreter.json"})
z.updateConfig()

## Add your own dependencies if you want them always there...
#z._addTerpDep("spark", "com.databricks:spark-csv_2.10:1.4.0")

new_terp_name = "sparkMahout"
z.createTerp( "spark", new_terp_name)
z.addMahoutConfig(new_terp_name)

z._updateTerpProp("flink", "host", "localhost")
new_terp_name = "flinkMahout"
z.createTerp("flink", new_terp_name)
z.addMahoutConfig(new_terp_name)

z._writeTerpJson()
z.uploadConfig()
z.setupR()
z.start()
z.setupR()

### Only need to uncomment/run this once ever. 
# from data.webapp import clone_rawkintrevos_webapp_template
# clone_rawkintrevos_webapp_template()

z.deployApp(APP_PREFIX)
