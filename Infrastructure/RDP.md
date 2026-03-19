# Remote Desktop Protocol (TCP/3389)

RDP is Microsoft’s remote desktop protocol used for graphical login to Windows systems. From a pentest perspective, RDP exposure can allow **user enumeration**, **credential validation**, and **direct interactive access** if credentials are obtained.  
Default port: **TCP/3389**.

## Detection

### nmap
```
nmap -p 3389 -sV <IP>
nmap -p 3389 --script rdp-ntlm-info <IP>
nmap -p 3389 --script rdp-enum-encryption <IP>
```

## Authentication Testing

### Crowbar (RDP brute-force/spray)
```
crowbar -b rdp -s <IP>/32 -U users.txt -C passwords.txt
```

### Hydra
```
hydra -L users.txt -P passwords.txt rdp://<IP>
```

## Manual Access (Valid Credentials)

### xfreerdp
```
xfreerdp /v:<IP> /u:user /p:password
xfreerdp /v:<IP> /u:DOMAIN\\user /p:password
xfreerdp /v:<IP> /u:user /p:password +clipboard /drive:share,/tmp
```