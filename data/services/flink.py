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

from data.services.common import AbstractServiceOnBI

class FlinkServiceOnBI(AbstractServiceOnBI):
    service_name = 'flink'
    service_port = 8088
    binaryLocation = "http://mirrors.koehn.com/apache/flink/flink-1.1.1/flink-1.1.1-bin-hadoop2-scala_2.10.tgz"

    config_files = {
        "yarn-session.sh": "bin/yarn-session.sh"
    }

    def start(self, containers=1, otherArgs=""):
        """
        :param containers:
        :param otherArgs:  see https://ci.apache.org/projects/flink/flink-docs-master/setup/yarn_setup.html#start-flink-session
        :return:
        """
        stdin, stdout, stderr = self.ssh.exec_command(
            "%s/bin/yarn-session.sh -n %i %s" % (self.dirName, containers, otherArgs))
        self.stdout = stdout
