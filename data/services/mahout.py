import json

def installMahout(ssh):
    print "downloading mahout"
    stdin, stdout, stderr = ssh.exec_command("wget http://mirror.reverse.net/pub/apache/mahout/0.12.2/apache-mahout-distribution-0.12.2.tar.gz")
    print stdout.read()
    print "untarring mahout"
    stdin, stdout, stderr = ssh.exec_command("tar xzf apache-mahout-distribution-0.12.2.tar.gz")
    print stdout.read()



def updateSparkTerpWithMahoutDeps():
    with open("./data/resources/zeppelin/interpreter.json") as f:
        interpreter_json = json.load(f)

    for k, v in interpreter_json['interpreterSettings'].iteritems():
        if v['name'] == 'spark':
            spark_id = k
            break

    interpreter_json['interpreterSettings'][spark_id]['dependencies'] = \
        [{
             u'groupArtifactVersion': u'/home/guest/apache-mahout-distribution-0.12.2/mahout-spark_2.10-0.12.2-dependency-reduced.jar',
             u'local': False},
         {u'groupArtifactVersion': u'/home/guest/apache-mahout-distribution-0.12.2/mahout-spark-shell_2.10-0.12.2.jar',
          u'local': False},
         {u'groupArtifactVersion': u'/home/guest/apache-mahout-distribution-0.12.2/mahout-math-0.12.2.jar',
          u'local': False},
         {u'groupArtifactVersion': u'/home/guest/apache-mahout-distribution-0.12.2/mahout-math-scala_2.10-0.12.2.jar',
          u'local': False, u'exclusions': []},
         {u'groupArtifactVersion': u'/home/guest/apache-mahout-distribution-0.12.2/mahout-spark_2.10-0.12.2.jar',
          u'local': False}]

    with open("./data/resources/zeppelin/interpreter.json", 'w') as f:
        json.dump(interpreter_json, f)
