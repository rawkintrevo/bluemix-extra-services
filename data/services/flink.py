# /**
#  * Licensed to the Apache Software Foundation (ASF) under one
#  * or more contributor license agreements.  See the NOTICE file
#  * distributed with this work for additional information
#  * regarding copyright ownership.  The ASF licenses this file
#  * to you under the Apache License, Version 2.0 (the
#  * "License"); you may not use this file except in compliance
#  * with the License.  You may obtain a copy of the License at
#  *
#  *     http://www.apache.org/licenses/LICENSE-2.0
#  *
#  * Unless required by applicable law or agreed to in writing, software
#  * distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.
#  */

from selenium import webdriver
from time import sleep

from data.services.common import AbstractServiceOnBI

class FlinkServiceOnBI(AbstractServiceOnBI):
    service_name = 'flink'
    service_port = 8083
    binaryLocation = "http://mirrors.koehn.com/apache/flink/flink-1.1.2/flink-1.1.2-bin-hadoop2-scala_2.10.tgz"

    config_files = {
        "yarn-session.sh": "bin/yarn-session.sh",
        "flink-conf.yaml": "conf/flink-conf.yaml",
        "taskmanager.sh" : "bin/taskmanager.sh"
    }

    def startYarn(self, containers=1, otherArgs=""):
        """
        :param containers:
        :param otherArgs:  see https://ci.apache.org/projects/flink/flink-docs-master/setup/yarn_setup.html#start-flink-session
        :return:
        """
        stdin, stdout, stderr = self.ssh.exec_command(
            "%s/bin/yarn-session.sh -n %i %s" % (self.dirName, containers, otherArgs))
        self.stdout = stdout


    def startLocal(self):
        stdin, stdout, stderr = self.ssh.exec_command(
            "%s/bin/start-local.sh" % self.dirName)

    def stopLocal(self):
        stdin, stdout, stderr = self.ssh.exec_command(
            "%s/bin/stop-local.sh" % self.dirName)

    def yarnGetUrlOfWebUI(self, app_prefix):
        self.start()
        while True:
            line = self.stdout.readline()
            print line
            if "JobManager Web Interface:" in line:
                jmwi_line = line
                break
            if "Flink JobManager is now running on" in line:
                jmro_line = line

        jobMgrAddr = jmro_line.split(" ")[-1].split(":")[0]

        self.deployApp(app_prefix)

        # Wait until App is deployed
        sleep(1000)  # have to sleep until app is up

        # Wait until App is deployed
        sleep(1000)  # have to sleep until app is up

        ## Now we go get the actual port, this is all bc Flink thought it would be cute to use Java Script in the job manager UI
        #  SMH
        url = "http://" + app_prefix + "-flink.mybluemix.net" + jmwi_line.split("8088")[1].replace("\n", "") + "#/submit"

        driver = webdriver.Firefox()
        driver.get(url) #"http://flinktester1-flink.mybluemix.net/proxy/application_1472068101977_0008/#/submit")
        sleep(5)
        htmlSource = driver.page_source

        for line in htmlSource.split("\n"):
            if "Yarn's AM proxy doesn't allow file uploads. You can visit" in line:
                break

        jobMgrPort = int(line.split("a href=")[1].split("#")[0].split(':')[2][:-1])
        return jobMgrPort, jobMgrAddr
