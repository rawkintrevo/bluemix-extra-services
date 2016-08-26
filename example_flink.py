from selenium import webdriver
import time

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
flink.start()

while True:
    line = flink.stdout.readline()
    print line
    if "JobManager Web Interface:" in line:
        jmwi_line = line
        break
    if "Flink JobManager is now running on" in line:
        jmro_line = line


jobMgrAddr = jmro_line.split(" ")[-1].split(":")[0]

flink.deployApp("flinktester1")

# Wait until App is deployed
time.sleep(1000)  # have to sleep until app is up


# Wait until App is deployed
time.sleep(1000)  # have to sleep until app is up

## Now we go get the actual port, this is all bc Flink thought it would be cute to use Java Script in the job manager UI
#  SMH
url = "http://" + APP_PREFIX + "-flink.mybluemix.net" + jmwi_line.split("8088")[1].replace("\n", "")  +"#/submit"

driver = webdriver.Firefox()
driver.get("http://flinktester1-flink.mybluemix.net/proxy/application_1472068101977_0008/#/submit")
time.sleep(5)
htmlSource = driver.page_source

for line in htmlSource.split("\n"):
    if "Yarn's AM proxy doesn't allow file uploads. You can visit" in line:
        break

jobMgrPort = int(line.split("a href=")[1].split("#")[0].split(':')[2][:-1])

## Finally redeploy the "REAL" app. (Pointed at real job manager)
flink.deployApp(prefix=APP_PREFIX, remotePort=jobMgrPort, remoteAddr=jobMgrAddr)

