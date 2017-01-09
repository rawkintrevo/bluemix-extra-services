from time import sleep

from data.services.zeppelin import ZeppelinServiceOnBI
from data.services.mahout import MahoutServiceOnBI



APP_PREFIX="myapp" # anything you want- but must be unique

## Last Init: 9/29/2016 @ 8:56 AM
SERVER = "" # eg ""bi-hadoop-prod-4162.bi.services.us-south.bluemix.net"
USERNAME = "" # eg "user1"
PASSWORD = "" # eg "password1"

## For Notebook storage:
## https://zeppelin.apache.org/docs/0.5.5-incubating/storage/storage.html

S3_USERNAME = 'flink-meetups'
S3_BUCKET = "rawkintrevos-notebooks"


from data.services.flink import FlinkServiceOnBI

flink = FlinkServiceOnBI(SERVER, USERNAME, PASSWORD)
flink.install()
sleep(10)
flink.uploadConfig()
flink.startLocal()
flink.deployApp(APP_PREFIX)


## For Notebook storage:
## https://zeppelin.apache.org/docs/0.5.5-incubating/storage/storage.html

#S3_USERNAME = 'rawkintrevo'
#S3_BUCKET = "rawkintrevos-notebooks"


z = ZeppelinServiceOnBI(SERVER, USERNAME, PASSWORD)
z.install()
z.setS3auth(S3_USERNAME, S3_BUCKET) ## Must do this first!
z.start()
sleep(5)
z.downloadConfig({"interpreter.json"  : "conf/interpreter.json"})
z.updateConfig()
## Add your own dependencies if you want them always there...
#z._addTerpDep("spark", "com.databricks:spark-csv_2.10:1.4.0")

new_terp_name = "sparkMahout"
z.createTerp( "spark", new_terp_name)
#z.addMahoutConfig(new_terp_name)

z._updateTerpProp("flink", "host", "localhost")
#new_terp_name = "flinkMahout"
#z.createTerp("flink", new_terp_name)
#z.addMahoutConfig(new_terp_name)
z._writeTerpJson()
z.uploadConfig()
z.setupR()
z.start()

z.deployApp(APP_PREFIX)