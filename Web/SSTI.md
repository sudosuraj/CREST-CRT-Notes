## Server-Side Template Injection

Look for places where user input is rendered into:

- email templates
- PDF generation
- notification previews
- admin customization fields
- error pages or template previews

Strong hints:

- expressions like `{{...}}`, `${...}`, or `<#...>`
- input reflected after server-side rendering rather than raw output


### Step 1: Basic Evaluation

Simple probes:

```text
{{7*7}}
${7*7}
{{7+3}}
```

If the output changes to a computed result, SSTI is likely.

### Step 2: Fingerprint The Engine

Examples:

- Jinja often renders `{{ 7 * '7' }}` as repeated text
- Twig tends to evaluate arithmetic differently
- Java engines often use `${...}` or `#set(...)`

This matters because payloads are engine-specific.

### Step 3: Context Discovery

If safe to do so, test whether objects or configuration are exposed.

Jinja-style examples:

```text
{{ config }}
{{ ''.__class__ }}
{{ ''.__class__.__mro__ }}
```

The goal is to understand the template context before attempting anything heavier.

### Step 4: File Read Or Code Execution

Only after confirming the engine and context should you test higher-impact paths.

Examples that may work in specific engines:

```text
{{ __import__('os').popen('id').read() }}
{{ dump() }}
```

These are not universal. Treat them as engine-specific escalation, not generic SSTI proof.

### Common Engines

#### Jinja

Detection:

```text
{{ 7 * 7 }}
{{ 7 * '7' }}
{{ config }}
```

#### Twig

Detection:

```text
{{ 7 * 7 }}
{{ dump() }}
```

#### Velocity

Detection:

```text
#set($foo = "bar")
```

### Pitfalls

- assuming reflected braces automatically mean SSTI
- using engine-specific RCE payloads before fingerprinting the engine
- overcommitting to command execution when configuration disclosure already proves impact
- forgetting that some SSTI points exist only in admin or email-preview workflows