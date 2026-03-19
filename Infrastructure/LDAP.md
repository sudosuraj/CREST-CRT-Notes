# LDAP / Active Directory LDAP (TCP/389, TCP/636)

DAP (Lightweight Directory Access Protocol) is used to query directory services, most commonly **Microsoft Active Directory**. Misconfigurations can allow **unauthenticated or low-privilege enumeration** of users, groups, computers, and domain structure.  
Default ports:
- **389/TCP** – LDAP (cleartext or StartTLS)
- **636/TCP** – LDAPS (SSL/TLS)

## Detection

### nmap
```
nmap -p 389,636,3268 -sV <IP>
nmap -p 389 --script ldap-rootdse <IP> # pulls naming contexts and domain info
nmap -p 389 --script ldap-search <IP> # search directory entries
```

## Banner Grabbing
```
nc -vn target.com 389
```

## Connect/Validate Bind

### Anonymous Bind
```
ldapsearch -x -H ldap://<IP> -s base
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" "(objectClass=*)"
```

### Null Bind
```
ldapsearch -x -H ldap://<IP> -D "" -w "" -b "DC=example,DC=local"
```

### Verify Creds (quick)
```
ldapwhoami -x -H ldap://<IP> -D "user@example.local" -w 'password'
```


## RootDSE (Base DN Discovery)

```
ldapsearch -x -H ldap://<IP> -s base \
  "(objectClass=*)" namingContexts defaultNamingContext rootDomainNamingContext \
  schemaNamingContext configurationNamingContext supportedControl supportedSASLMechanisms
```

## Enumeration

### Basic Bind
```
ldapsearch -x -H ldap://target.com -D "cn=admin,dc=example,dc=com" -w password \
  -b "dc=example,dc=com"
```

### Enumerate Users

#### No Authentication
```
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" \
  "(objectClass=user)" sAMAccountName userPrincipalName memberOf
```
#### Authenticated
```
ldapsearch -x -H ldap://<IP> -D "user@example.local" -w password -b "DC=example,DC=local" \
  "(objectClass=user)" sAMAccountName userPrincipalName memberOf
```

### Enumerate Domain Groups
#### No Authentication
```
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" \
  "(objectClass=group)" cn member
```

#### Authenticated
```
ldapsearch -x -H ldap://<IP> -D "user@example.local" -w password -b "DC=example,DC=local" \
  "(objectClass=group)" cn member
```

### Enumerate Computers

#### No Authentication
```
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" \
  "(objectClass=computer)" name dNSHostName operatingSystem
```
#### Authenticated
```
ldapsearch -x -H ldap://<IP> -D "user@example.local" -w password -b "DC=example,DC=local" \
  "(objectClass=computer)" name dNSHostName operatingSystem
```

## Targeted Queries

### Find Privileged Users

#### No Authentication
```
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" \
  "(memberOf=CN=Domain Admins,CN=Users,DC=example,DC=local)" sAMAccountName
```

#### Authenticated
```
ldapsearch -x -H ldap://<IP> -D "user@example.local" -w password -b "DC=example,DC=local" \
  "(memberOf=CN=Domain Admins,CN=Users,DC=example,DC=local)" sAMAccountName
```

### Users with SPNs (Kerberoastable)
#### No Authentication
```
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" \
  "(servicePrincipalName=*)" sAMAccountName servicePrincipalName
```
#### Authenticated
```
ldapsearch -x -H ldap://<IP> -D "user@example.local" -w password -b "DC=example,DC=local" \
  "(servicePrincipalName=*)" sAMAccountName servicePrincipalName
```

### ASREPRoast Candidates (DONT_REQ_PREAUTH)

#### No Authentication
```
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" \
  "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))" \
  sAMAccountName userPrincipalName
```

#### Authenticated
```
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" -D "user@example.local" -w password \
  "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))" \
  sAMAccountName userPrincipalName
```

### Passord Policy

#### No Authentication 
```
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" \
  "(objectClass=domainDNS)" minPwdLength lockoutThreshold
```
#### Authenticated
```
ldapsearch -x -H ldap://<IP> -D "user@example.local" -w password -b "DC=example,DC=local" \
  "(objectClass=domainDNS)" minPwdLength lockoutThreshold
```

### Sensitive attribute hunting

#### Descriptions
```
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" "(description=*)" description sAMAccountName
```
#### Emails and Phones
```
ldapsearch -x -H ldap://<IP> -b "DC=example,DC=local" "(mail=*)" mail sAMAccountName
```

## Dumping

### Full User Dump (all attributes)
```
ldapsearch -x -H ldap://<IP> -D "user@example.local" -w 'password' \
  -b "DC=example,DC=local" "(objectClass=user)" "*" "+" > all_users.ldif

grep -i "description:" all_users.ldif | grep -i "pass\|pwd"
```

### ldapdomaindump
```
ldapdomaindump -u "example.local\\user" -p 'password' <IP>
```

## CrackMapExec

### Base Check
```
crackmapexec ldap <DC_IP> -d <domain> -u <user> -p <pass>
```

### MAQ (Machine Account Quota)

- Identifies how many computers a user can create 

```
crackmapexec ldap <DC_IP> -d <domain> -u <user> -p <pass> -M maq
```

### Enumerate subnets
```
crackmapexec ldap <DC_IP> -d <domain> -u <user> -p <pass> -M subnets
```

### Users with descriptions (often sensitive)
```
crackmapexec ldap <DC_IP> -d <domain> -u <user> -p <pass> -M get-desc-users
```

## LDAPS (SSL/TLS)
- If 389 is restricted but 636 is open:
```
ldapsearch -x -H ldaps://<IP> -b "DC=example,DC=local"
ldapsearch -x -H ldaps://target.com:636 -D "cn=admin,dc=example,dc=com" -w password -b "dc=example,dc=com"
```

## ldapwhoami

### Test authentication
```
ldapwhoami -x -H ldap://target.com -D "cn=admin,dc=example,dc=com" -w password
```

### Anonymous Bind
```
ldapwhoami -x -H ldap://target.com
```

## ldapadd/ldapmodify

### Add new entry
```
ldapadd -x -H ldap://target.com -D "cn=admin,dc=example,dc=com" -w password -f new_entry.ldif
```
### Modify entry
```
ldapmodify -x -H ldap://target.com -D "cn=admin,dc=example,dc=com" -w password -f modify.ldif
```

### Delete entry
```
ldapdelete -x -H ldap://target.com -D "cn=admin,dc=example,dc=com" -w password "cn=user,ou=users,dc=example,dc=com"
```

## Brute Force

### Hydra
```
hydra -L users.txt -P passwords.txt <IP> ldap2 -s 389
```

### nmap
```
nmap -p 389 --script ldap-brute --script-args ldap.base='"DC=example,DC=local"' <IP>
```

### Metasploit
```
use auxiliary/scanner/ldap/ldap_login
set RHOSTS target.com
set USERNAME admin
set PASS_FILE passwords.txt
run
```