# RPC And rpcbind

## Why It Matters

`rpcbind` and RPC enumeration rarely matter on their own. They matter because they expose what other RPC-backed services are available, especially:

- NFS
- mountd
- status services
- legacy Unix RPC services
- Windows RPC enumeration through related tooling

## Workflow

1. detect RPC and `rpcbind`
2. enumerate registered programs and ports
3. map those ports to follow-on services
4. pivot into the real target service such as NFS or MS-RPC

## Detection

```bash
nmap -sS -sV -p 111 <ip>
nmap -sU -sV -p 111 <ip>
nmap -p 111 --script rpcinfo <ip>
```

High ports may also host RPC-backed programs, so full or targeted service scans matter.

## Step 1: Enumerate Registered Programs

```bash
rpcinfo -p <ip>
rpcinfo -p <ip> | sort -n
nc -nv <ip> 111
```

You are looking for:

- NFS-related services
- mount services
- status and lock services
- anything unexpected on dynamic ports

## Step 2: Follow The Real Service

RPC enumeration is usually the pre-step to:

- NFS share enumeration
- mountd testing
- Windows domain/user enumeration through `rpcclient`

### Windows-Oriented Enumeration

```bash
rpcclient -U "" -N <target_ip>
```

Useful commands:

```text
enumdomusers
enumdomgroups
querygroup 0x200
querygroupmem 0x200
queryuser 0x1f4
```

## Pitfalls

- treating port 111 as the finding instead of a recon step
- not following up on mapped dynamic ports
- confusing Unix RPC service discovery with Windows SMB/RPC enumeration

## Reporting Notes

Capture:

- the RPC programs exposed
- the dynamic ports mapped
- the follow-on service this enabled you to enumerate

## Fast Checklist

```text
1. Detect rpcbind
2. List registered programs
3. Map dynamic ports to real services
4. Follow up on NFS or Windows RPC paths
```
