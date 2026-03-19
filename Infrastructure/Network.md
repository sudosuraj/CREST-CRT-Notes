# Network Enumeration

## Host Discovery

### Fping
```
fping -a -g -q 10.10.10.0/24 | tee ips.txt
```

### Nmap Ping Scan
```
nmap -sn 192.168.1.0/24
```

### Nmap ARP Ping (local networks)
```
nmap -PR 192.168.1.0/24
```

### ARP-Scan (local, reliable)
```
sudo arp-scan -I eth0 10.10.10.0/24
```

### NetDiscover(passive)
```
sudo netdiscover -r 10.10.10.0/24
```

### Massscan (fast, local ranges)
```
masscan 10.0.0.0/24
```

### Simple Bash-One Liner utilising ping
```
for i in {1..254}; do ping -c 1 -W 1 192.168.1.$i &>/dev/null && echo "Host 192.168.1.$i is up"; done
```



## TCP Port Scanning

### Nmap scan for Common TCP ports
 
```
sudo nmap -sS -Pn -n -T4 -iL ips.txt -oA nmap-sS-common
```

### nmap scan for all / FULL TCP scan
```
sudo nmap -sS -Pn -n -T4 -p- -iL ips.txt -oA nmap-sS-allPorts
```

### Verify Open TCP Ports (3-way handshake)
```
sudo nmap -sT -Pn -n -p <PORTS> -T4 -iL ips.txt -oA nmap-sT-verifyopen
```

### Detailed / Aggressive Scan (services, scripts, OS) 
```
nmap -Pn -A -p <LIST> -iL ips.txt -oA detailednmap
```

### Service Detection and Script
```
nmap -sV -sC -Pn -T4 -p 10.10.10.10 -oA nmap-sV-sC-detailed
```
 
## UDP Port Scanning

### Common UDP ports
```
nmap -sU -Pn -n -iL ips.txt -oA nmap-sU-common
```

### UDP Scripts & Version Detection (confirmed ports)
```
nmap -sU -sC -sV -Pn -n -T2 -iL ips.txt -p <list> -oA nmap-sU-Scripts-openPorts
```

### Masscan
```
masscan 10.0.0.0/24 --udp masscan -p1-65535,U:1-65535 10.10.10.10 --rate=1000 -e tun0
```


## OS Fingerprinting

### nmap OS Detection

```
nmap -O 10.10.10.1
```

### TTL Inspection
```
ping 10.10.10.1
```
* Windows = 128
* Linux = 64
* Cisco = 255

### p0f (passive OS Fingerprinting)
```
p0f -i <network_interface>
```

## Internet Information Gathering and Reconnaissance

### Nslookup

#### Resolve a given hostname to the corresponding IP
```
nslookup target.com
```

#### Reverse DNS lookup
```
nslookup -type=PTR IP_address
```

#### MX (Mail Exchange) lookup
```
nslookup -type=MX domain.com
```

### DNSRecon

#### Performing General Enumeration against target
```
dnsrecon -d domain.com -D /usr/share/wordlists/dnsmap.txt -t std --xml ouput.xml 
```
#### DNS reverse of all of the addresses
```
dnsrecon -r  127.0.0.0/24 -n  <IP_DNS> 
dnsrecon -r  127.0.1.0/24 -n  <IP_DNS>
dnsrecon -r  <IP_DNS>/24 -n  <IP_DNS>
```

### Dig
```
dig ANY @<DNS_IP> <DOMAIN>     #Any information

dig A @<DNS_IP> <DOMAIN>       #Regular DNS request

dig AAAA @<DNS_IP> <DOMAIN>    #IPv6 DNS request

dig TXT @<DNS_IP> <DOMAIN>     #Information

dig MX @<DNS_IP> <DOMAIN>      #Emails related

dig NS @<DNS_IP> <DOMAIN>      #DNS that resolves that name

dig -x 192.168.0.2 @<DNS_IP>   #Reverse lookup

dig -x 2a00:1450:400c:c06::93 @<DNS_IP> #reverse IPv6 lookup
```

### Zone Transfer

#### Dig
```
dig axfr @<DNS_IP> <DOMAIN> 
```

#### DNSRecon
```
dnsrecon -d active.htb -a  -n  <IP_DNS> 
```

## Network Connection
### Telnet
```
telnet 10.10.10.10 21
```

## VLAN Tagging

### Connecting to VLAN

#### Windows
```
New-NetVLAN -InterfaceAlias "Ethernet" -VLANID 10
```

#### Linux

1. Identify your physical interface
```
ip -4 a
```
* Look for the interface that has your IP (e.g. `eth0`, `ens18`).

2. Create VLAN Interface (tagging step)
```
sudo ip link add link ens18 name ens18.10 type vlan id 10
```
* `ens18` = physical interface (parent)
* `ens18.10` = new VLAN interface name (convention: `<iface>.<vlanid>`)
* `id 10` = VLAN ID

3. Assign an IP address to the VLAN interface
```
sudo ip addr add 192.168.10.88/24 dev ens18.10
```
* Setting 192.168.10.88 as the IP of the VLAN interface.

4. If VLAN uses DHCP instead
```
sudo dhclient ens18.10
```

5. Bring the VLAN interface up
```
sudo ip link set ens18.10 up
```
6. Verify it exists and has an IP
```
ip -4 a
```

7. Test connectivity

* Ping another host on that VLAN
```
ping 192.168.10.93
```

* If you have multiple interfaces/routes, force the VLAN interface
```
ping -I ens18.10 192.167.10.93
```

* `-I` forces the ping to go out via the VLAN interface, so you know you're testing VLAN 10.



### Identify VLAN Traffic

1. Identify interfaces that may carry VLANs (e.g `eth0.10`, `ens18.20`)
```
ip link show
```

2. List VLAN interfaces only (e.g. `vlan protocol 802.1Q id <VID>`)
```
ip -d link show
```

3. Catpure VLAN-tagged traffic

```
tcpdump -i eth1 -e vlan
```
**Example Output:** `vlan 10, ethertype IPv4, 192.168.10.88 > 192.168.10.93`

4. Capture traffic for a specific VLAN ID
```
sudo tcpdump -i ens18 -e vlan 10
```

#### Wireshark

* Display filter for VLAN traffic
```
vlan
```

* Filter for specific VLAN ID
```
vlan.id == 10
```


## Configuring Static IP & DHCP

### Linux

1. Identify Interface
```
ip -4 a
```

2. Static IP

#### set IP 172.16.1.10 on the local network for ens18
```
sudo ip addr add 172.16.1.10/24 dev ens18 
```
#### Bring interface up
```
sudo ip link set ens18 up
```

#### Configure the default gateway

```
sudo ip route add default via 172.16.1.1
```
**What the above does**
* Sets the default route
* Tells the OS: "For traffic not destined for my local subnet, send it to 172.16.1.1

#### Configure DNS
```
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

3. DHCP 

* Following command says: "Is there a DHCP Server? Please give me an IP configuration."
```
sudo dhclient ens18
```
* To release first (Following commands say "I'm done with this IP. You can give it back to the pool.")
```
sudo dhclient -r ens18
sudo dhclient ens18
```

#### NetworkManager (alternative way)

##### Static IP
```
nmcli con show
nmcli con modify "<connection-name>" \
  ipv4.method manual \
  ipv4.addresses 172.16.1.10/24 \
  ipv4.gateway 172.16.1.1 \
  ipv4.dns 8.8.8.8
nmcli con up "<connection-name>"
```

##### DHCP
```
nmcli con modify "<connection-name>" ipv4.method auto
nmcli con up "<connection-name>"
```

#### Restart Network Settings
```
sudo systemctl restart NetworkManager.service 
sudo systemctl restart networking.service
```

### Windows

#### netsh
```
netsh interface ip set address name="Ethernet" static <IP_Address> <Subnet_Mask>

netsh interface ip set address name="Ethernet" source=dhcp
```


## IP Routing

### "To reach 192.168.2.0/24, send packets to 192.168.1.1, using eth0"
```
sudo ip route add 192.168.2.0/24 via 192.168.1.1 dev eth0
sudo ip route add <destination_network> via <gateway_ip> dev <interface>
```

### Connect to 172.16.1.1 via gateway 192.168.1.254
```
sudo ip route add 172.16.1.0/24 via 192.168.1.254
# then try to curl to 172.16.1.1 to see if reachable
```
#### If already set up access to 172.16.1.1 above, then we can use that again to double pivot.
#### For example, connect to 10.10.10.1 via 172.16.1.1
```
sudo ip route add 10.10.10.0/24 via 172.16.1.1
```


## Service Identification 

### nmap
```
nmap -sV example.com
```

### netcat
```
nc example.com 80
```
### telnet
```
telnet example.com 80
```

### curl
```
curl -I http://example.com
```

### wget
```
wget --server-response http://example.com
```