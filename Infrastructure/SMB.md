## Server Message Block

* MS06-025 - RCE vulnerability.
* MS08-067 / CVE-2008-4250 - RCE vulnerability exploited by the Conficker worm.
* MS17-010 / CVE-2017-0144 - RCE vulnerability allegedly leaked from the NSA.


### Recon

```
nmap -p 139,445 target.com
nmap --script smb-vuln* -p 139,445 [ip]
```

### Enumerate Host
```
# nxc smb [ip]
crackmapexec smb [ip]
```

### List Shares
```
crackmapexec smb [host/ip] --shares
crackmapexec smb [host/ip] -u [user] -p [pass] --shares
crackmapexec smb [host/ip] -u guest -p '' --shares
crackmapexec -N -L //[ip]

smbclient -N -L //[IP]

```

### User Enumeration 
```
crackmapexec smb [ip] -u guest -p '' --rid-brute
```

### Enumerate Files
```
smbclient //[ip]/[share name] -U [username] [password] #With creds
smbclient //[ip]/[share name] -N  #Null authentication


crackmapexec smb 10.10.11.222 -u [username] -p '' -M spider_plus #spider_plus module will run through all the shares and collect data about all the files
```

