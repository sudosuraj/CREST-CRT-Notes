# NetBIOS

## Why It Matters

NetBIOS is mainly useful for host identification and naming intelligence. It can reveal:

- workstation or server names
- domain or workgroup names
- whether file sharing is active

It is often an early clue that feeds into SMB and RPC testing.

## Workflow

1. detect NetBIOS name service
2. enumerate names and flags
3. map results into SMB and Windows-host targeting

## Enumeration

```bash
nmblookup -A 10.10.10.10
nbtscan 10.10.10.10
nbtscan 192.168.1.0/24
sudo nmap -sU -sV -T4 --script nbstat -p 137 -Pn -n 10.10.10.10
```

## Interpreting Results

Common flags:

- `<00>` hostname or domain/workgroup name
- `<20>` file-sharing service present
- `<03>` legacy messenger service entry

The most useful output is usually:

- hostname
- domain or workgroup
- confirmation that SMB-related services are likely worth following up

## Pitfalls

- treating NetBIOS itself as the objective
- not pivoting immediately into SMB and RPC checks

## Reporting Notes

Capture:

- disclosed hostnames
- domain or workgroup data
- evidence of file-sharing capability

## Fast Checklist

```text
1. Query NetBIOS names
2. Note hostname and domain/workgroup
3. Use the result to drive SMB/RPC follow-up
```
