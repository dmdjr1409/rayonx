# RayonX 🩻

> **Pass your code through X-rays. Detect and purge AI code slop, trivial comments, and robotic filler in seconds.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![RayonX Humanity Score](https://img.shields.io/badge/RayonX-100%25%20Human-brightgreen)](#)

```
  ____                              __  __
 |  _ \ __ _ _   _  ___  _ __       \ \/ /
 | |_) / _` | | | |/ _ \| '_ \ _____ \  / 
 |  _ < (_| | |_| | (_) | | | |_____ /  \ 
 |_| \_\__,_|\__, |\___/|_| |_|     /_/\_\
             |___/                        
```

AI code generators are everywhere. While they write functional logic, they also pollute codebases with **robotic boilerplate, trivial comments that insult your intelligence, bloated docstrings, and ghost blocks**.

**RayonX** is an ultra-fast, zero-dependency CLI tool that scans your codebase, computes your **Humanity Index (0–100%)**, and safely strips out the AI slop without altering your runtime logic.

---

## ⚡ Key Capabilities

- 🎯 **Trivial Comment Stripper**: Catches and purges obvious filler like `# Import libraries`, `# Loop through array`, `# Initialize variables`, `# Return response`.
- 🤖 **LLM Phrasing Detector**: Flags typical AI hallucination residue (*"This function leverages..."*, *"Here is the updated code:"*, *"As an AI..."*).
- 👻 **Ghost Block Audit**: Detects blind `try: ... except: pass` patterns generated as lazy placeholders.
- 📝 **Markdown & README Sanitizer**: Spots robotic marketing intros (like *"In today's fast-paced..."*) and abandoned developer placeholders.
- 🛡️ **Zero Dependencies**: Runs out of the box with standard Python (built on Python's native `ast` parser).
- 🎨 **Ready-to-use Badges**: Generates Shields.io badges to show off your repository's human craftsmanship.

---

## 🚀 Quickstart

### Installation

```bash
# Clone the repository
git clone https://github.com/dmdjr1409/rayonx.git
cd rayonx

# Install locally
pip install .
```

Or run standalone without installing:

```bash
python3 -m rayonx.cli check .
```

---

## 💻 Usage

### 1. Audit your repository

```bash
rayonx check .
```

Output:

```text
Detected AI Slop & Code Smells:

  src/services/billing.py
    12: [RX101] Redundant import comment
       > # Import all required libraries
    45: [RX104] Redundant loop explanation comment
       > # Loop through each customer invoice
    89: [RX203] Blind empty try/except block suppressing all errors
       > except Exception: pass

Summary:
  Files scanned : 28
  Lines analyzed: 3,420
  Slop findings : 3

  Humanity Index: ████████████████████░░ 91% Human
```

### 2. Preview removals (Dry Run)

```bash
rayonx clean . --dry-run
```

Displays an exact unified diff of comments that would be stripped without touching any file.

### 3. Clean files in-place

```bash
rayonx clean .
```

Strips auto-removable redundant comments in-place while keeping indentation and business logic intact.

### 4. Get a Badge for your README

```bash
rayonx badge
```

Copy the generated Markdown into your `README.md`:

```markdown
[![RayonX Humanity Score](https://img.shields.io/badge/RayonX-98%25%20Human-brightgreen)](https://github.com/dmdjr1409/rayonx)
```

---

## 📋 Rule Reference

| Code | Category | Description | Auto-Cleanable |
| :--- | :--- | :--- | :---: |
| **RX101** | Trivial Comment | Redundant import/module comments | ✅ Yes |
| **RX102** | Trivial Comment | Redundant variable initialization comments | ✅ Yes |
| **RX103** | Trivial Comment | Redundant return statement comments | ✅ Yes |
| **RX104** | Trivial Comment | Redundant loop explanation comments | ✅ Yes |
| **RX105** | Trivial Comment | Redundant condition check comments | ✅ Yes |
| **RX106** | Trivial Comment | Redundant error handling comments | ✅ Yes |
| **RX107** | Trivial Comment | Redundant end-of-file / section markers | ✅ Yes |
| **RX108** | Trivial Comment | Redundant entry point comments | ✅ Yes |
| **RX201** | LLM Verbosity | Hallmark AI filler phrasing (*"leverages"*, *"robust"*) | ⚠️ Manual |
| **RX202** | LLM Verbosity | Chat conversational residue left in source | ✅ Yes |
| **RX203** | Ghost Block | Blind empty `try/except: pass` suppression | ⚠️ Manual |
| **RX301** | Markdown Slop | Generic AI marketing introductions in documentation | ⚠️ Manual |
| **RX302** | Markdown Slop | Unfilled AI template placeholders | ⚠️ Manual |

---

## 🧪 Testing

```bash
python3 -m unittest discover -s tests -v
```

---

## 📄 License

[MIT](LICENSE) © [Junior Diomande](https://github.com/dmdjr1409)
