## Requirements

Python
- paramiko `sudo apt-get install python-paramiko`
- scp `sudo apt-get install python-scp`

BlueMix / Cloud Foundry
- [IBM Docs](https://console.ng.bluemix.net/docs/cli/index.html#cli)
- `cf login -a https://api.ng.bluemix.net`
-- or `cf login` and then `https://api.ng.bluemix.net` when it asks you for an API enpoint

Amazon S3 Creds (for Zeppelin Notebook Storage)
- My Account -> Security and Credentials -> Continue -> Access Keys -> Create New Access Keys
- save rootkey.csv to ./data/resources/aws`
- Setup s3 as bucketName/userName/notebook
- Review this first: https://zeppelin.apache.org/docs/0.5.5-incubating/storage/storage.html

