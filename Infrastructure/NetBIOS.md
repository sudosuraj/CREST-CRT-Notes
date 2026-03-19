# Netowrk Basic Input Output System

## Enumeration

```
nmblookup -A 10.10.10.10
nbtscan 10.10.10.10
sudo nmap -sU -sV -T4 --script nbstat.nse -p137 -Pn -n 10.10.10.10
```

### nbtscan

* The below command will list NetBIOS names and corresponding IP addresses for network mapping and asset identification
```
nbtscan 192.168.1.0/24
```

## Interpreting NetBIOS Enumeration Results
```
Flag	Meaning
<00>	Indicates the hostname or domain name
<20>	Indicates the system is running file-sharing services
<03>	Indicates the Messenger service is active on the machine
```