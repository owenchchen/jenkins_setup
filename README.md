jenkins\_setup
=============

This repository contains the code (config, src and script files) to setup and run a
cob-Jenkins CI server.


SETUP:
======
Description how to set up the Jenkins master and its slaves. This manual is made and tested for Ubuntu 12.04. Especially for older versions there might occure some problems.

Master:
-------

###Install Jenkins CI:

###Set up Jenkins configurations
All configurations should be stored in a common folder in the
`$HOME`-folder called `jenkins-config':
```mkdir ~/jenkins-config```

####SSH configurations
A `.ssh`-folder is needed which contains a ssh-key to access the GitHub-repositories. Either you generate a new key with `ssh-keygen` or you just copy the `~/.ssh` of the master. You have to add this key to your GitHub user (http://github.com/settings/ssh). This user should have read-access to all repositories you want to build.
It is very important that 'github.com' belongs to *known hosts*. Therefore the `.ssh`-folder should contain a `known\_hosts` file. If 'github.com' is already known can be checked by entering:
```ssh-keygen -H -f <known_host_PATH> -F github.com```
If it is not known TODO

Slaves:
-------

###Sudo commands without password on slave
To be able to run sudo commands without the need to enter the password each time, enter
```sudo visudo```
and add
```<JENKINS-USER>    ALL=(ALL) NOPASSWD: ALL```
at the end. Exit with `CTRL-X`. After re-login you won't need a password anymore.

###SSH access without password to master (and the otherway around)
The slave has to be able the access the master via SSH without a password (and the otherway around). Enter the following command on each slave, login to the master and run the command again.
```
ssh-copy-id <master> (on slave)
ssh <master> (on slave)
ssh-copy-id <slave> (on master)
```
Go back with twice `CTRL-D`.

###`Pbuilder`
`Pbuilder` is recommended! If not present, install it:
```bash
apt-get install pbuilder debootstrap devscripts
```

####Performance improvement
For the configurations a file called `~/.pbuilderrc` in the slaves $HOME-folder is
needed (`/etc/pbuilder/pbuilderrc` is an alternative).

#####Don't use pbuilders aptcache
The aptcach of pbuilder is very useful but when the cache is getting
bigger gradually it takes quite a while to open a chroot from the
tarball. If you don't want to use it (for instance if you use an
external apt-cacher), add the following to
`~/.pbuilderrc`:
```conf
\# don't use aptcache
APTCACHE=""
```

#####Use ccache for build
To use ccache inside the pbuilder add the following to `~/.pbuilderrc`:
```conf
\# ccache
sudo mkdir -p /var/cache/pbuilder/ccache
sudo chmod a+w /var/cache/pbuilder/ccache
export CCACHE_DIR="/var/cache/pbuilder/ccache"
export PATH="/usr/lib/ccache:${PATH}"
EXTRAPACKAGES=ccache
BINDMOUNTS="${CCACHE_DIR}"
```


#####Use multi-core zipping
To speedup the zipping and unzipping of the chroot tarballs, install `pigz`:
```bash
apt-get install pigz debootstrap devscripts
```

And add the following to .pbuilderrc:
```conf
\# pigz; multicore zipping
COMPRESSPROG=pigz
```

#####Mount memory to run the pbuilder chroots in it
Installations and builds inside the chroot need quite a lot write accesses. If you don't have a SSD installed, you can use the memory for this. Therefore you have to create a filesystem in your RAM, using `tmpfs` by adding the following to the slaves `/etc/fstab`:
```fstab
\# pbuilder
tmpfs   /var/cache/pbuilder/build   tmpfs   defaults,size=32000M    0   0
```
*The size depends on the size of the chroot you will work with (at least 3G, more is better). It can be larger then the RAM size. If the chroot size exceeds the RAM size it will use the SWAP as well.*

Additionally you have to add the following to `~/pbuilderrc`:
```
\# tmpfs
APTCACHEHARDLINK=no
```

Finally you have to mount `tmpfs` by entering:
```
mount -a
```

___


Generate pipeline manually (deprecated):
===============================

1. Checkout this repository:
----------------------------

Clone this repository to your desired location
```bash
git clone git://github.com/ipa320/jenkins_setup.git <path to clone in>
```


2. Set up slave config file:
----------------------------

Create a folder in your HOME-folder called: jenkins-config
```bash
mkdir ~/jenkins-config
```

Create a so called slave_config.yaml file with the following entries:
```yaml
master: name_of_jenkins_master
master_uri: "http://url_of_jenkins_master:8080"
tarball_host: name_of_server_storing_the_chroot_tarballs
tarball_folderpath: folder_the_tarballs_are_stored
jenkins_login: user_name_with_right_to_create_jobs
jenkins_pw: user_password
```

3. Add repository to PYTHONPATH:
--------------------------------

```bash
export PYTHONPATH=$PYTHONPATH:<repository_path>/src
```

4. Set up pipeline configuration:
---------------------------------

Checkout the repository [jenkins_config](https://github.com/ipa320/jenkins_config "ipa320/jenkins_config")
```bash
git clone git@github.com:config/jenkins_config.git
```

Repository structure:
```bash
jenkins_config
|-jenkins_master_name1
| |- user_name1
| |  |-pipeline_config.yaml
| |- user_name2
| |  |-pipeline_config.yaml
|-jenkins_master_name2
| |- user_name3
| |  |-pipeline_config.yaml
```

You have to create a folder according to your Jenkins masters name (if
not existent yet). Inside create a folder with your user name. Within this
folder set up a pipeline_config.yaml file with your configurations. You
can use the \<jenkins_config_repository_location\>/jenkins-test-server/test-user
as an example.

When your done push it to GitHub.

5. Create pipeline:
-------------------

Execute the
\<jenkins_setup_repository_location\>/scripts/generate_buildpipeline.py
script to create all your pipeline jobs on the Jenkins CI Server.

```bash
./generate_buildpipeline.py <user_name>
```
