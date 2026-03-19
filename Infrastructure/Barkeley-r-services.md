# Berkeley r-services (rlogin / rsh / rexec)

Berkeley r-services are legacy remote access services that rely on **host-based trust** instead of strong authentication. When misconfigured, they can allow **passwordless remote command execution or shell access**.  
Common ports:
- **rlogin**: TCP/513
- **rsh**: TCP/514
- **rexec**: TCP/512

These services often trust users/hosts via `.rhosts`, `/etc/hosts.equiv`, or weak service configuration.

## Detection
### nmap
```
nmap -p 512,513,514 -sV <IP>
nmap -p 512,513,514 --script rlogin,rsh,rexec <IP>
```

## rlogin (TCP/513)

### Basic Usage
```
rlogin <IP>
```

### Specify username
```
rlogin -l root <IP>
rlogin -l user <IP>
```

## rsh (TCP/512)

### Execute remote command
```
rsh <IP> id
rsh <IP> whoami
rsh <IP> uname -a
```

### Specify user
```
rsh -l root <IP> id
rsh -l user <IP> /bin/sh
```

### Attempt shell
```
rsh <IP> /bin/sh
```

## rexec (TCP/512)

Unlike `rlogin`/`rsh`, rexec requires credentials, but credentials are transmitted in cleartext.

### Basic Usage
```
rexec <IP> -l root -p password id
```

### Interactive Shell
```
rexec <IP> -l user -p password /bin/sh
```

## Trust Relationship Abuse

### Files indicating trust
- `/etc/hosts.equiv`
- `~/.rhosts`

If writable or misconfigured, these allow passwordless access from trusted hosts/users.

#### Example `.rhosts` entry
```
trustedhost root
+
```

- `+` trusts all hosts/users — catastrophic

