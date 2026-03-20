# CREST CRT Notes

These notes are being upgraded from quick-reference cheat sheets into workflow-driven study material for CREST CRT preparation.

## Current State

Many files currently contain:

- tool commands without the decision process around them
- payload lists without context selection
- enumeration steps without follow-on actions
- exploitation ideas without verification or reporting notes

That makes them useful as memory joggers, but weak as end-to-end revision material.

## Target Format For Each Note

Each topic should eventually answer these questions:

1. What does this issue or service matter for in a CRT-style engagement?
2. How do I recognize it quickly during recon or testing?
3. What is the shortest safe workflow from detection to confirmation?
4. What branches do I follow if the first technique fails?
5. What evidence do I need for reporting?
6. What common mistakes waste time or create false positives?

## Recommended Structure

Use this structure when expanding or rewriting a topic:

1. Overview
2. Why It Matters
3. Recognition Cues
4. Enumeration Or Testing Workflow
5. Exploitation Paths
6. Verification Steps
7. Post-Exploitation Or Impact
8. Reporting Notes
9. Fast Checklist

## Priority Topics

The most important notes to turn into full-chain guides first are:

- network enumeration
- SMB
- WinRM
- SQL injection
- XSS
- Linux privilege escalation
- Windows privilege escalation

These topics appear often enough in labs and internal testing workflows that they should read like playbooks, not snippets.

## How To Study With This Repo

Use the notes in this order:

1. Start with `Infrastructure/Network.md` to build host and service triage discipline.
2. Move to service notes such as SMB, WinRM, MSSQL, MySQL, LDAP, and SSH.
3. Use the web notes to map input points to exploit classes and escalation paths.
4. Finish with local privilege escalation notes once you already have code execution.

When revising a note, test yourself on:

- how to detect it
- how to validate it without guessing
- how to move from enumeration to impact
- what proof you would save for the report

## Scope

The goal is not to create a giant payload dump. The goal is to create concise notes that preserve the full reasoning chain from reconnaissance to finding validation to evidence collection.
