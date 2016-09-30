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



base_dir = "/home/rawkintrevo/gits/zeppelin-mahout-script/scripts/mahout"

import argparse
from subprocess import call


parser = argparse.ArgumentParser()

parser.add_argument("--skip_download", help="do not download Apache Mahout")
parser.add_argument("--path_to_interpreter_json", help="path to 'interpreter.json'")

args = parser.parse_args()

print call(["pwd"])

