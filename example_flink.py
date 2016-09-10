
from data.services.flink import FlinkServiceOnBI
from data.webapp import clone_rawkintrevos_webapp_template

APP_PREFIX="flinktester12"

SERVER = "" # ""bi-hadoop-prod-xxxx.bi.services.us-south.bluemix.net"
USERNAME = ""  #"user"
PASSWORD = "" # "password"

clone_rawkintrevos_webapp_template()

flink = FlinkServiceOnBI(SERVER, USERNAME, PASSWORD)

flink.install()
flink.updateConfig()
flink.getUrlOfWebUI()



## Finally redeploy the "REAL" app. (Pointed at real job manager)
flink.deployApp(prefix=APP_PREFIX, remotePort=jobMgrPort, remoteAddr=jobMgrAddr)

