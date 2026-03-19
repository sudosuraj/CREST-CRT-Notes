# Remote Procedure Call / Portmapper / rpcbind (TCP/UDP 111)

`rpcbind` (aka portmapper) maps RPC program numbers to network ports. Enumerating it can reveal RPC-based services (commonly NFS-related) and their ports. Default: **111/TCP + 111/UDP**.

## Detection

### nmap
```
nmap -sS -sV -p 111 <IP>
nmap -sU -sV -p 111 <IP>
nmap -p 111 --script rpcinfo <IP>
nmap -sV -p- <IP> # detect rpc on high ports
nmap --script rpc-grind -p <PORT> <IP> # fingerprint suspected RPC
```

## Enumeration
### rpcinfo (local tool)
```
rpcinfo -p <IP>
rpcinfo -p <IP> | sort -n
```

### rpcbind
```
nc -nv <IP> 111
```


## MS-RPC Enumeartion (Windows via SMG)

### rpcclient
```
rpcclient -U "" -N <TARGET_IP>
#empty username (-U "")
#no password (-N)
```

#### Domain User enumeration
```
> enumdomusers
```
#### Domain Group enumeration
```
> enumdomgroups
```
#### Get Group Information
```
querygroup 0x200
```

#### Query member of a group
```
querygroupmem 0x200
```

#### Query user account
```
queryuser 0x1f4
```




