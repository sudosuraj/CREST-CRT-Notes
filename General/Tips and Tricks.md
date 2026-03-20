# 1. Quick port scan:

```
ports=$(nmap -p- --min-rate=1000 -T4 $target | grep ^[0-9] | cut -d '/' -f 1 | tr '\n' ',' | sed s/,$//)
echo "[+] Found open ports $ports\n[+] Starting nmap on $ports"

echo "[+] Found open ports: $ports\n[+] Starting nmap on ports: $ports"
nmap -p$ports -sC -sV $target -oN nmap
```

*Avoid `--version-intensity 9` on large networks-use it only on targeted, critical systems.*

```
ports=$(sudo masscan -p1-65535,U:1-65535 $target --rate=1000 -e tun0 | awk -F " " '{print $4}' | awk -F "/" '{print $1}' | sort -n | tr '\n' ',' | sed 's/,$//')
echo "[+] Found open ports: $ports\n[+] Starting nmap on ports: $ports"
nmap -p$ports -sC -sV $target
```
- Port scanning without nmap:
```bash
for PORT in {0..1000}; do timeout 1 bash -c "</dev/tcp/172.19.0.1/$PORT &>/dev/null" 2>/dev/null && echo "port $PORT is open"; done
```
# 2.  Brute Forcing User RIDs

```shell
for i in $(seq 500 1100);do rpcclient -N -U "" $target -c "queryuser 0x$(printf '%x\n' $i)" | grep "User Name\|user_rid\|group_rid" && echo "";done
```

(An alternative to this would be a Python script from [Impacket](https://github.com/SecureAuthCorp/impacket) called [samrdump.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/samrdump.py).)
