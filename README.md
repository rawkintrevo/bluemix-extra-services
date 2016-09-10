## Requirements

### On your local machine (no on the cluster)
This is also based on linux, but you can figure it out on other stuff

#### Install these

Python
- On Linux
-- paramiko `sudo apt-get install python-paramiko`
-- scp `sudo apt-get install python-scp`
- On Mac
-- pip install paramiko
-- pip install scp


BlueMix / Cloud Foundry
- [IBM Docs](https://console.ng.bluemix.net/docs/cli/index.html#cli)
- `cf login -a https://api.ng.bluemix.net`
-- or `cf login` and then `https://api.ng.bluemix.net` when it asks you for an API enpoint

Amazon S3 Creds (for Zeppelin Notebook Storage)
- My Account -> Security and Credentials -> Continue -> Access Keys -> Create New Access Keys
- save rootkey.csv to `<CLONE_DIR>`/data/resources/aws`
- Setup s3 as bucketName/userName/notebook
- Review this first: https://zeppelin.apache.org/docs/0.5.5-incubating/storage/storage.html
- ALWAYS run `z.setS3auth(S3_USERNAME, S3_BUCKET)` before adding any additional configs, e.g. `z.addMahoutConfig(new_terp_name)`. This is imporant bc `zeppelin-env.sh` is overwritten.


#### Ports Used

These are not the default ports per the projects- I've done a little traffic control so they don't conflict on a box. Everyone seems to want to use `8080`.
- Flink Stand Alone Cluster:
-- WebUI: `8083`
-- master: `6121` - Did this so Zeppelin LocalMiniCluster wouldn't get in its way
- Nifi: 8084
- Zeppelin: 8081, 8082



