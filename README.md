# backup-config.py

**This script is no longer maintained here, please check the one in our [Gitlab repo](https://gitlab.com/ip-fabric/integrations/scripts/ipf-export-device-config)**

Python3 script to collect available configuration files in IP Fabric and store them in a (Git) folfer

## How to install

Install ipfabric Python module and dependencies. Make sure the version of the `ipfabric` SDK matches your version of IP Fabric.

```shell
pip install -U ipfabric==6.0.10 python-dotenv typer loguru
```

or

```shell
pip install -r requirements.txt
```

## How to use

```shell
python3 backup_config.py [OPTIONS]
```

Available Options:

* --folder     -f       TEXT  Select the backup folder. [default: /path/of/script/backup]
* --no-git     -ng            Disable GIT option for the Backup folder.
* --sanitized  -s             Sanitized configuration by removing some data.
* --help                      Show this message and exit.

### Environment file

In the file `.env`, you will need to set the variables:

* `IPF_URL = "https://ipfabric-server/"` enter the URL of IP Fabric
* `IPF_TOKEN = "abcd1234"` enter the API token
* `IPF_SNAPSHOT` leave blank if you want to use the latest snapshot, otherwise add the `id` of the snapshot, i.e. `66365ad3-e568-403a-91a3-de1775b4f600`
* `IPF_VERIFY = "True"` use False if you are using a self-signed certificate
* `INVENTORY_FILTER` use if you want to filter the list of devices from the inventory to take into account to collect the backup config. This has to be a valid JSON as a string.

### Check the GIT Backup Folder

Inside the backup folder, you can run the following git commands to see:

* #### git log - list of commit

```shell
git log --graph --pretty='\''%Cred%h%Creset -%C(auto)%d%Creset %s %Cgreen(%ad) %C(bold blue)<%an>%Creset'\
```

* #### git log --stat - summary of changes for each commit

```shell
git log --graph --pretty='\''%Cred%h%Creset -%C(auto)%d%Creset %s %Cgreen(%ar) %C(bold blue)<%an>%Creset'\'' --stat
```

* #### git diff - see the diff between the previous and the latest commit

```shell
git diff HEAD^ HEAD
gd HEAD^ <file_to_compare_between_prev_and_last_commit>.txt
```

## Help

```shell
python3 backup_config.py --help
```

## License

MIT

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job.)
