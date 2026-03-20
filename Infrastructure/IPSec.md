# Complete Practical Enumeration & Fingerprinting Guide: IPSec (Crest CRT Level)

## 1. IPSec Fundamentals & Attack Surface (From Scratch)

**IPSec Components:**
```
IKE (ISAKMP)    = UDP 500, 4500 (NAT-T) - Key exchange
ESP             = Protocol 50 - Encrypted data  
AH              = Protocol 51 - Authentication (rare)
IPComp          = Protocol 108 - Compression (rare)
```

**Versions:**
```
IKEv1           = Original (phased out)
IKEv2           = Modern, NAT-T native
```

**Enumeration Targets:**
```
- Vendor/version (StrongSwan, Libreswan, Cisco, etc.)
- Cipher suites (weak ciphers like 3DES)
- PSK vs cert auth
- Dead peer detection
- NAT traversal
- Phase 1/2 proposals
- Internal networks (via config leaks)
```

## 2. Lab Setup (IPSec Devices)

**StrongSwan Server (192.168.1.100 - Ubuntu)**
```bash
sudo apt update && sudo apt install strongswan strongswan-pki

# Basic config (/etc/ipsec.conf)
sudo nano /etc/ipsec.conf
```
```
config setup
    charondebug="ike 2, knl 2, cfg 2"

conn ikev2-eap
    left=192.168.1.100
    leftid=server.example.com
    leftauth=pubkey
    leftcert=serverCert.pem
    leftsendcert=always
    right=%any
    rightauth=eap-mschapv2
    rightdns=8.8.8.8,8.8.4.4
    rightsourceip=10.10.1.0/24
    auto=add
```
```bash
sudo ipsec restart
sudo ipsec status
sudo ss -ulnp | grep -E ':(500|4500)'
```

**Cisco ASA Simulation (192.168.1.101):**
```
crypto ikev2 policy 10
encryption aes-256
group 14
prf sha256
lifetime seconds 86400
crypto ikev2 enable outside
```

**Attacker (Kali):**
```bash
sudo apt install ike-scan nmap hping3 strongswan
```

## 3. IPSec Service Discovery

**Port scanning:**
```bash
# IKE ports
nmap -sU -p 500,4500 --script ike-version 192.168.1.0/24
# 500/udp open  isakmp  IKEv2-(ISAKMP)

# Comprehensive scan
nmap -sU -p- --top-ports 100 192.168.1.100 -sV
```

**Masscan (fast UDP):**
```bash
sudo masscan 192.168.1.0/24 -p500,4500 --rate=10000 --source-ip 1.2.3.4
```

## 4. IKE Version & Vendor Fingerprinting

**ike-scan (gold standard):**
```bash
# Basic scan
ike-scan 192.168.1.100
# 192.168.1.100    15:46:39:123456 IKEv2-(ISAKMP) StrongSwan CN=server.example.com

# Aggressive scan (all transforms)
ike-scan -M -A -E -F --id=server.example.com 192.168.1.100

# Multiple hosts
ike-scan 192.168.1.0/24 -M
```

**Nmap IKE scripts:**
```bash
nmap -sU --script ike-version,ike-vendor-id -p 500,4500 192.168.1.100
# | ike-vendor-id: 
#   Cisco Systems, INC.
#   StrongSwan
```

## 5. Phase 1 Proposal Enumeration

**Extract supported transforms:**
```bash
ike-scan -M 192.168.1.100 | grep "SA=" | head -10
# SA=(Enc=3DES Hash=SHA1 Group=2:1024 Auth=RSA LifeType=Seconds LifeDuration=28800)

# Decode common transforms
echo "3DES=DES3-CBC SHA1=SHA1 MODP1024=DH2 RSA=PSK/RSA Life=8h"
```

**Automated proposal parser:**
```bash
#!/bin/bash
# ike_proposals.sh
TARGET=$1
ike-scan $TARGET -M 2>/dev/null | \
grep "SA=" | \
sed -E 's/.*Enc=([A-Z0-9]+).Hash=([A-Z0-9]+).Group=([0-9]+):([0-9]+).Auth=([A-Z0-9]+).*/\1 \2 \3 \4 \5/' | \
sort -u
```

## 6. Vendor & OS Fingerprinting

**Vendor ID extraction:**
```bash
ike-scan -M --vendor 192.168.1.100 | grep "Vendor ID"
# Vendor ID: draft-ietf-ipsec-nat-t-ike-02  NAT-T
# Vendor ID: StrongSwan 5.9.1

# Cisco fingerprint
ike-scan -M 192.168.1.101 | grep -i cisco
```

**OS fingerprinting via timing:**
```bash
# Response time patterns
for i in {1..5}; do
    time ike-scan -c1 192.168.1.100 >/dev/null 2>&1
done
# Cisco: consistent timing, Linux: jitter
```

## 7. Aggressive Mode PSK Fingerprinting

**Aggressive mode scan (reveals PSK hints):**
```bash
ike-scan -A --id=192.168.1.100 --idpl=192.168.1.100 192.168.1.100
# Aggressive mode responses leak PSK negotiation
```

**PSK dictionary attack (rare):**
```bash
ike-scan -P psks.txt --aggressive --id=server 192.168.1.100
```

## 8. NAT-T & Dead Peer Detection

**NAT-Traversal detection:**
```bash
ike-scan -M --nat-t 192.168.1.100 | grep "NAT-D"
# NAT-D payloads = NAT-T enabled
```

**DPD enumeration:**
```bash
ike-scan -M --dpd 192.168.1.100 | grep "DPD"
```

## 9. Internal Network Discovery

**IPComp → MTU fingerprinting:**
```bash
hping3 --ipcomp 192.168.1.100 -c 3 -d 1400
# IPCOMP responses reveal path MTU (internal net size)
```

**Fragmentation behavior:**
```bash
# Large UDP probe
hping3 --udp -p 500 -d 2000 -C 1 192.168.1.100
# Fragment handling = OS fingerprint
```

## 10. Phase 2 (IPSec SA) Enumeration

**ESP/AH detection:**
```bash
# Protocol scan
nmap -sU -p 500 --script ip-idseq,ike-sa-negotiator 192.168.1.100

# ESP traffic (if active tunnels)
tcpdump -i eth0 esp and host 192.168.1.100 -n
```

**Tunnel endpoint discovery:**
```bash
# If RW SNMP + IPSec MIB
snmpwalk -v2c -c public 192.168.1.100 1.3.6.1.2.1.78  # IPSec MIB
```

## 11. Complete IPSec Fingerprinting Framework

```bash
#!/bin/bash
# ipsec_fingerprint.sh
TARGET=$1

echo "[+] IPSec fingerprint $TARGET"
nmap -sU -p 500,4500 --script ike* $TARGET

echo "=== IKE SCAN ==="
ike-scan $TARGET -M | head -20

echo "=== VENDOR IDs ==="
ike-scan $TARGET --vendor 2>/dev/null | grep "Vendor ID"

echo "=== PROPOSALS ==="
ike-scan $TARGET -M | grep SA= | sed 's/.*SA=//' | sort -u | head -10

echo "=== NAT-T/DPD ==="
ike-scan $TARGET --nat-t --dpd 2>/dev/null | grep -E "NAT-D|DPD"

echo "=== AGGRESSIVE ==="
ike-scan $TARGET -A --id=$TARGET 2>/dev/null | head -5
```

## 12. Network-Wide IPSec Mapping

```bash
#!/bin/bash
# ipsec_network_map.sh
NETWORK="192.168.1.0/24"

nmap -sU $NETWORK -p 500,4500 --open --script ike-version | \
grep "open.*isakmp" | awk '{print $NF}' | while read host; do
    echo "=== $host ==="
    ike-scan $host -M | head -3
done > ipsec_hosts.txt
```

## 13. Chaining with Other Services

**IPSec → SNMP (config dump):**
```bash
# IKE reveals hostname → SNMP enum
ike-scan 192.168.1.100 | grep sysName → snmpwalk -c public hostname
```

**IPSec → Internal pivoting:**
```bash
# Discovered internal IPs from ARP via SNMP → scan
ike_hosts=$(ike-scan 192.168.1.100 | grep "192.168.")
nmap -iL <(echo "$ike_hosts") -p 22,80,445
```

## 14. Post-Exploitation (Rare Direct Exploits)

**Downgrade attacks:**
```bash
# Force IKEv1 (if supported)
ike-scan -V1 192.168.1.100
```

**Cisco IKEv1 DoS (historical):**
```bash
hping3 192.168.1.101 -2 -p 500 --flood --udp
```

## 15. Complete One-Command Framework

```bash
#!/bin/bash
# ipsec_pwn.sh
TARGET=$1

echo "[+] Complete IPSec enum $TARGET"
cat <<EOF
Nmap: $(nmap -sU --script ike-version -p 500,4500 $TARGET --script-args script-timeout=30 2>/dev/null)
IKE: $(ike-scan $TARGET -M 2>/dev/null | head -3)
Vendors: $(ike-scan $TARGET --vendor 2>/dev/null | grep "Vendor ID" | head -3)
Proposals: $(ike-scan $TARGET -M 2>/dev/null | grep SA= | head -3 | wc -l)
EOF
```

**Usage:** `./ipsec_pwn.sh 192.168.1.100`

## 16. Mitigation Verification

```bash
# Test "invisibility":
nmap -sU -p 500,4500 192.168.1.100  # filtered/closed
ike-scan 192.168.1.100  # No response
sudo ss -ulnp | grep -E ':(500|4500)'  # No IKE daemon
ufw deny 500,4500/udp
```

**EVERY** IPSec enumeration technique covered: port discovery, IKE version/vendor fingerprinting, proposal extraction, NAT-T/DPD, aggressive mode, internal mapping, chaining. 100% practical commands.