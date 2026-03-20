# Complete Network Reconnaissance & Analysis Guide - EVERY Topic Covered

## 1. Network Connections - Ethernet (Copper/Fiber)

**DHCP auto-configuration (requests IP from DHCP server on copper Ethernet):**
```bash
sudo dhclient eth0  # Broadcasts DHCP DISCOVER on eth0 interface
```

**Static IP configuration (manually sets IP/mask/gateway on copper Ethernet):**
```bash
sudo ip addr add 192.168.1.100/24 dev eth0     # Assigns IP address and subnet mask
sudo ip link set eth0 up                       # Activates the Ethernet interface
sudo ip route add default via 192.168.1.1      # Sets default gateway (router IP)
```

**Fiber Ethernet (same as copper, SFP module):**
```bash
sudo ethtool -S eth0  # Shows fiber link statistics (same commands)
```

## 2. Network Connections - WiFi (802.11 a/b/g/n/ac/ax)

**WiFi network scanning (discovers available access points):**
```bash
sudo iwlist wlan0 scan | grep ESSID  # Scans all 802.11 channels, lists SSIDs
```

**WiFi WPA2 connection (authenticates to enterprise WPA2 AP):**
```bash
sudo wpa_supplicant -B -i wlan0 -c <(wpa_passphrase "SSID" "password")  # Creates temp config, connects in background
sudo dhclient wlan0  # Requests IP via DHCP after association
```

**WiFi WPA3 SAE (modern secure WiFi):**
```bash
wpa_supplicant -c <(wpa_passphrase "SSID" "password" --sae) -i wlan0 -B  # WPA3 SAE authentication
```

## 3. Ethernet VLANs & VLAN Tagging (IEEE 802.1Q)

**Load VLAN module (enables 802.1Q tagging support):**
```bash
sudo modprobe 8021q  # Kernel module for VLAN subinterfaces
```

**Create VLAN interface (tags Ethernet frames with VLAN ID):**
```bash
sudo ip link add link eth0 name eth0.100 type vlan id 100  # Creates eth0.100 tagged VLAN 100
sudo ip addr add 192.168.100.10/24 dev eth0.100            # Assigns IP to VLAN interface
sudo ip link set eth0.100 up                               # Brings VLAN interface online
```

**Windows VLAN tagging (PowerShell):**
```powershell
New-Vlan -InterfaceAlias "Ethernet" -VlanID 100  # Creates VLAN 100 tagged interface
New-NetIPAddress -InterfaceAlias "Ethernet 100" -IPAddress 192.168.100.10 -PrefixLength 24  # Static IP
```

**VLAN tagged traffic analysis (captures 802.1Q headers):**
```bash
sudo tcpdump -i eth0 -e -nn vlan  # Shows VLAN tags (0x8100 EtherType)
# eth0: 00:11:22:33:44:55 > 66:77:88:99:aa:bb, ethertype 802.1Q (0x8100), length 102: vlan 100
```

**VLAN hopping security test (double tagging):**
```bash
# Scapy VLAN hop (sends double-tagged frame)
scapy -c "sendp(Ether()/Dot1Q(vlan=100)/Dot1Q(vlan=200)/IP(dst='192.168.200.1')/ICMP())"
```

## 4. IPv4 Protocol - Interface Configuration

**Static IP (IPv4 layer 3 addressing):**
```bash
sudo ip addr flush dev eth0        # Removes all IPs from interface
sudo ip addr add 10.0.0.100/24 dev eth0  # Layer 3 IPv4 assignment
```

**DHCP client (IPv4 dynamic addressing):**
```bash
sudo dhclient -r eth0  # Releases current DHCP lease
sudo dhclient eth0     # Requests new IPv4 lease via DHCP
```

## 5. IPv4 Host Discovery - ARP/ICMP

**ARP discovery (Layer 2 broadcast discovery):**
```bash
sudo arp-scan --localnet  # Sends ARP requests to all IPs on local subnet
sudo arping -c 3 -I eth0 192.168.1.0/24  # ARP pings entire subnet
```

**ICMP ping sweep (Layer 3 discovery):**
```bash
for i in {1..254}; do ping -c1 -W1 192.168.1.$i &>/dev/null && echo "192.168.1.$i"; done
```

**Nmap comprehensive discovery (ARP+ICMP+TCP):**
```bash
nmap -sn 192.168.1.0/24  # -sn = no port scan, just host discovery
```

## 6. IPv4 Routing Configuration

**Static route addition (IPv4 Layer 3 forwarding):**
```bash
sudo ip route add 172.16.0.0/16 via 192.168.1.254  # Routes specific subnet via gateway
sudo ip route replace 172.16.0.0/16 via 192.168.1.253  # Replaces existing route
```

**View routing table (shows IPv4 forwarding paths):**
```bash
ip route show table all  # All routing tables (main, local, etc.)
```

**Policy-based routing (source-based IPv4 routing):**
```bash
sudo ip rule add from 192.168.1.100 table 100  # Traffic from this IP uses table 100
sudo ip route add default via 192.168.1.254 table 100  # Table 100 default gateway
```

## 7. Standard Pentesting - Network Mapping/Port Scanning

**Network mapping (full service discovery):**
```bash
nmap -sS -sV -sC -O 192.168.1.0/24 -oA fullmap  # SYN scan + version + scripts + OS
```

**Port scanning (service enumeration):**
```bash
nmap -p- -T4 192.168.1.100  # All 65535 TCP ports, aggressive timing
sudo nmap -sU --top-ports 100 192.168.1.100  # Top 100 UDP ports
```

**Service exploitation (Nmap scripts):**
```bash
nmap -p 21,22,23,25,53,80,110,111,135,139,143,443,993,995,1723,3306,3389,5900,8080 \
--script vuln 192.168.1.0/24  # Vulnerability scanning
```

## 8. IPv4 Protocols Awareness - ICMP/IGMP/TCP/UDP/IPsec

**ICMP types (network diagnostics):**
```bash
hping3 --icmp --icmp-ts 192.168.1.1  # ICMP timestamp
hping3 --icmp --icmp-addr 192.168.1.1  # ICMP address mask
```

**TCP 3-way handshake:**
```bash
hping3 --syn -p 80 -c 1 192.168.1.100  # TCP SYN packet
```

**UDP amplification:**
```bash
hping3 --udp -p 53 --data 1000 --flood 192.168.1.100  # UDP flood
```

**IPsec detection (covered previously):**
```bash
ike-scan 192.168.1.100  # IKEv1/v2 detection
```

## 9. Network Mapping Tools

**Traceroute variants (path discovery):**
```bash
traceroute 8.8.8.8                    # UDP traceroute (default)
traceroute -I 8.8.8.8                  # ICMP traceroute
traceroute -T -p 443 8.8.8.8           # TCP traceroute HTTPS
mtr --report 8.8.8.8                   # Traceroute + packet loss
```

**Active service queries:**
```bash
# DNS reverse mapping
for i in {1..254}; do host 192.168.1.$i 2>/dev/null; done

# SNMP network inventory
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.4.22.1.12  # ARP table (internal hosts)
```

**Logical diagram generation:**
```bash
nmap -oX map.xml 192.168.1.0/24 -T4 -A
xsltproc map.xml -o map.dot  # Converts Nmap XML to Graphviz
dot -Tpng map.dot -o network.png  # Renders network diagram
```

## 10. Host Criteria Identification

**Find all FTP servers:**
```bash
nmap -p 21 --open 192.168.1.0/24 -oG - | grep "21/open" | awk '{print $2}'
```

**Find Cisco routers:**
```bash
nmap --script cisco-* 192.168.1.0/24 | grep "Cisco"
sudo nmap -sV --version-intensity 9 192.168.1.0/24 | grep -i cisco
```

**Windows hosts only:**
```bash
nmap -O 192.168.1.0/24 | grep "Windows" | awk '{print $NF}'
```

## 11. Network Devices Analysis

**Router configuration (SNMP Cisco config):**
```bash
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.4.1.9.9.96.1.1.1.1.2.49  # Running config
```

**Switch CDP/LLDP discovery:**
```bash
sudo nmap --script cdp-neighbors-discover,lldp2csv 192.168.1.0/24  # Switch neighbors
```

**Firewall detection (response analysis):**
```bash
nmap -p 22,80,443 --reason 192.168.1.1  # filtered=no response vs rejected=RST
sudo nmap --packet-trace -p 80 192.168.1.1  # Shows firewall drops
```

## 12. Network Filtering & Bypass Methods

**Fragmentation bypass (splits packets past simple filters):**
```bash
nmap -f -p 80 192.168.1.1  # 8-byte TCP fragments
sudo hping3 -c 3 -d 24 -S -w 64 -p 80 --fragment 192.168.1.1  # Custom fragments
```

**Source port bypass (trusted service ports):**
```bash
nmap --source-port 53 -p 80 192.168.1.1     # DNS source port
nmap --source-port 20 -p 80 192.168.1.1     # FTP data port
```

**Idle/Zombie scan (third-party host scans target):**
```bash
sudo nmap -sI 192.168.1.254 192.168.1.1     # Zombie host IP predicts sequence numbers
```

**Decoy scanning (hides real source):**
```bash
nmap -D RND:10 -p 80 192.168.1.1            # 10 random decoy IPs
```

## 13. Traffic Analysis - Capture

**Live capture to PCAP (standard Wireshark format):**
```bash
sudo tcpdump -i eth0 -w traffic.pcap host 192.168.1.100 and port 80  # HTTP only
```

**Filtered real-time capture:**
```bash
sudo tshark -i eth0 -f "tcp port 443" -w https.pcap  # TLS traffic
sudo tshark -i eth0 -2 -r capture.pcap -Y "http"      # HTTP from PCAP
```

## 14. Traffic Analysis - Credential Recovery

**HTTP POST credentials:**
```bash
tshark -r traffic.pcap -Y "http.request.method == POST and frame.len > 200" \
-T fields -e http.request.uri -e http.file_data -e frame.number
```

**NTLM authentication hashes:**
```bash
tshark -r traffic.pcap -Y "ntlm" -T fields -e ntlmssp.ntlm_auth -e ntlmssp.ntlm_hash
# Crack: hashcat -m 5600 hashes.txt rockyou.txt
```

**FTP plaintext passwords:**
```bash
tshark -r traffic.pcap -Y "ftp.request.command == PASS" -T fields -e ftp.request.arg -e frame.number
```

**HTTP Basic Auth:**
```bash
tshark -r traffic.pcap -Y "http.authbasic" -T fields -e http.authbasic -e http.host
```

**SMB credentials:**
```bash
tshark -r traffic.pcap -Y "smb.cmd == 0x72" -T fields -e smb.file -e smb2.auth_frame
```

## 15. Traffic Analysis - Vulnerability Detection

**SQL injection signatures:**
```bash
tshark -r traffic.pcap -Y "http contains 'union select' or http contains '1=1--' or http contains \"' or '\"'" \
-T fields -e http.request.uri -e frame.number
```

**Directory traversal:**
```bash
tshark -r traffic.pcap -Y "http contains '../' or http contains '%2e%2e%2f' or http contains '%5c%2e%2e'" \
-T fields -e http.request.uri
```

**XSS payloads:**
```bash
tshark -r traffic.pcap -Y "http contains '<script>' or http contains 'javascript:'" -T fields -e http.request.uri
```

**SMB EternalBlue:**
```bash
tshark -r traffic.pcap -Y "smb.cmd == 0x72 and smb.trans2.cmd == 0x0e" -T fields -e frame.number -e smb.file
```

## 16. Complete Automated Recon

```bash
#!/bin/bash
# full_network_recon.sh
NETWORK=$1 INTERFACE=$2

# 1. VLAN discovery (tagged traffic)
sudo tcpdump -i $INTERFACE -c 100 -e vlan 2>/dev/null | grep "vlan " | sort -u

# 2. Host discovery (ARP/ICMP)
sudo nmap -sn $NETWORK -oG hosts.txt

# 3. Service mapping
sudo nmap -sS -sV -sC -O $(grep "Up" hosts.txt | awk '{print $2}') -oA services

# 4. UDP services (DNS/NBT/LLMNR)
sudo nmap -sU --top-ports 50 $(grep "Up" hosts.txt | awk '{print $2}')

# 5. Capture traffic (10min)
sudo timeout 600 tcpdump -i $INTERFACE -w recon_$(date +%s).pcap &

# 6. Analyze capture
wait
tshark -r recon_*.pcap -Y "http or ntlm or ftp or smb" -T fields -e frame.number -e http.request.uri -e ntlmssp.ntlm_hash
```

