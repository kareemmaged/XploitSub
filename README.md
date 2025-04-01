

██╗  ██╗██████╗ ██╗      ██████╗ ██╗████████╗███████╗██╗   ██╗██████╗ 
╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██║╚══██╔══╝██╔════╝██║   ██║██╔══██╗
 ╚███╔╝ ██████╔╝██║     ██║   ██║██║   ██║   ███████╗██║   ██║██████╔╝
 ██╔██╗ ██╔═══╝ ██║     ██║   ██║██║   ██║   ╚════██║██║   ██║██╔══██╗
██╔╝ ██╗██║     ███████╗╚██████╔╝██║   ██║   ███████║╚██████╔╝██████╔╝
╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═════╝ 
```

# XploitSub - Advanced Subdomain Enumeration Tool 🚀

**XploitSub** is a powerful and efficient **subdomain enumeration tool** designed for penetration testers and security researchers. It uses **DNS resolution techniques** to identify active subdomains from a given target domain.

---

## ✨ Features

✅ **Fast & Multithreaded** - Uses concurrent threads to maximize efficiency.
✅ **Custom Wordlists** - Supports any custom subdomain wordlist.
✅ **DNS-Based Enumeration** - Resolves valid subdomains via DNS lookups.
✅ **Timeout Control** - Adjust the timeout for better performance.
✅ **Graceful Stop** - Handle Ctrl+C interruptions without losing results.
✅ **Clear Statistics** - Provides tested subdomains count and elapsed time.

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/XploitSub.git
cd XploitSub
pip install -r requirements.txt
```

---

## 🚀 Usage

### Basic Enumeration
```bash
python XploitSub.py example.com -w wordlist.txt
```

### Using Custom Threads and Timeout
```bash
python xploitsub.py example.com -w wordlist.txt -t 20 --timeout 3
```

### Using a URL Instead of Domain
```bash
python xploitsub.py -u https://example.com -w wordlist.txt
```

---

## 🛠 Requirements

- Python 3.x
- `dnspython`
- `requests`
- `argparse`

Install dependencies with:
```bash
pip install -r requirements.txt
```

Happy Hacking! 🚀
