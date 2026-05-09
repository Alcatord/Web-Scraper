# 🕷️ WebScraper — Pure Python Web Scraper

<div align="center">

```
 ██╗    ██╗███████╗██████╗     ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
 ██║    ██║██╔════╝██╔══██╗    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
 ██║ █╗ ██║█████╗  ██████╔╝    ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
 ██║███╗██║██╔══╝  ██╔══██╗    ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
 ╚███╔███╔╝███████╗██████╔╝    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
  ╚══╝╚══╝ ╚══════╝╚═════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
```

![Python](https://img.shields.io/badge/Python-3.6%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![No Dependencies](https://img.shields.io/badge/Dependencies-ZERO-brightgreen?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Web Scraper — Pure Python | Zero external dependencies**

*Scrape pages · Crawl sites · Extract links, images, emails, tables & forms*

</div>

---

## 📖 What is WebScraper?

WebScraper is a **pure Python** web scraping tool with **zero external libraries**.  
No BeautifulSoup. No requests. No lxml. Just Python's stdlib.

It can scrape a single page in detail, crawl an entire website using BFS,  
or process a bulk list of URLs — then export everything to JSON or CSV.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Single Page Scrape** | Deep extraction of all data from one URL |
| 🕸️ **BFS Crawler** | Multi-page crawl with same-domain filtering |
| 📋 **Bulk Scrape** | Feed a `.txt` file of URLs and scrape them all |
| 🏷️ **Meta Tags** | Extracts all `<meta>` tags (SEO, OG, Twitter cards...) |
| 📰 **Headings** | H1–H6 hierarchy with level awareness |
| 🔗 **Links** | All `<a href>` links with optional title |
| 🖼️ **Images** | `src`, `alt`, `width`, `height` for every image |
| ✉️ **Email Finder** | Regex scan + `mailto:` detection across the page |
| 📊 **Table Extractor** | Parses `<table>` rows and columns into lists |
| 📝 **Form Detector** | Finds `<form>` elements, actions, methods, and inputs |
| 🌐 **Server Fingerprinting** | Reads response headers: `Server`, `X-Powered-By`... |
| 💾 **Export** | JSON (full), CSV (links), CSV (emails) |
| ⏱️ **Rate Limiting** | Configurable delay between requests (polite scraping) |
| 🍪 **Cookie Handling** | Automatic cookie jar for session-aware scraping |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/Alcatord/WebScraper.git
cd WebScraper

# Run it
python3 webscraper.py
```

On Windows:
```cmd
python webscraper.py
```

---

## 🖥️ Usage

### Mode 1 — Single Page

```
Mode:
  1) Single page — deep scrape one URL
  2) Crawler     — BFS multi-page scrape
  3) Bulk URLs   — scrape a list from file

Choice [1]: 1
URL: https://example.com
```

Extracts everything from that one page and displays it in the terminal.

---

### Mode 2 — BFS Crawler

```
Choice [1]: 2
Start URL: https://example.com
Max pages [10]: 20
Delay between requests (sec) [1]: 1.5
Same domain only? [Y/n]: Y
```

Starts from the given URL, follows all links in BFS order,  
stays on the same domain (optional), respects the delay between requests.

---

### Mode 3 — Bulk URLs

Create a text file with one URL per line:

```
urls.txt
────────
https://site1.com
https://site2.com/page
https://site3.org/about
```

Then:
```
Choice [1]: 3
File path: urls.txt
Delay (sec) [1]: 1
```

---

## 📋 Sample Output

```
══════════════════════════════════════════════════════════════════════════
URL   : https://example.com
Title : Example Domain
Status: 200  |  Size: 1,256 bytes
Scraped: 2025-01-15T14:32:00

META TAGS
  description          A sample webpage for testing
  og:title             Example Domain

HEADINGS (1)
  H1 Example Domain

PARAGRAPHS (1)
  ▸ This domain is for use in illustrative examples...

LINKS (1)
  → https://www.iana.org/domains/reserved

IMAGES (0)

EMAILS FOUND (0)
══════════════════════════════════════════════════════════════════════════
```

---

## 📁 Export Formats

After scraping, you can export:

| Option | File | Contents |
|---|---|---|
| `1` | `scrape_domain_TIMESTAMP.json` | Full structured data for all pages |
| `2` | `links_domain_TIMESTAMP.csv` | All links with source URL |
| `3` | `emails_domain_TIMESTAMP.csv` | Deduplicated emails with source URL |
| `4` | All of the above | Everything at once |

---

## 🛠️ How It Works

```
┌─────────────────────────────────────────────────┐
│               WebScraper Flow                   │
│                                                 │
│  1. User chooses mode (single/crawl/bulk)       │
│  2. Fetcher sends HTTP request                  │
│       ├─→ Cookie jar for sessions               │
│       ├─→ Realistic User-Agent header           │
│       ├─→ SSL without cert verification         │
│       └─→ Rate limiting (configurable delay)    │
│  3. PageParser (html.parser) extracts:          │
│       ├─→ Title, meta tags                      │
│       ├─→ Headings H1–H6                        │
│       ├─→ Paragraphs, links, images             │
│       ├─→ Emails (regex + mailto:)              │
│       ├─→ Tables (rows × cols)                  │
│       └─→ Forms (action, method, inputs)        │
│  4. Display results in terminal                 │
│  5. Export to JSON / CSV                        │
└─────────────────────────────────────────────────┘
```

### Libraries Used (all stdlib)

| Library | Used For |
|---|---|
| `urllib.request` | HTTP GET requests with redirects |
| `urllib.parse` | URL joining, parsing, encoding |
| `html.parser` | Built-in HTML parsing (no lxml/BS4) |
| `http.cookiejar` | Automatic cookie management |
| `json` | JSON export |
| `csv` | CSV export |
| `ssl` | HTTPS with flexible cert handling |
| `re` | Email regex extraction |
| `concurrent.futures` | Parallel bulk scraping |

---

## ⚖️ Legal Disclaimer

> **Only scrape websites you own or have explicit permission to scrape.**  
> Always check a site's `robots.txt` before scraping.  
> Respect rate limits — don't flood servers with requests.  
> This tool is for **educational purposes** and **authorized data collection** only.  
> The author is not responsible for any misuse.

---

## 📁 Project Structure

```
WebScraper/
├── webscraper.py    ← main scraper script
├── urls.txt         ← (optional) URL list for bulk mode
└── README.md        ← this file
```

---

## 🔮 Roadmap

- [ ] JavaScript rendering support (via subprocess + Node)
- [ ] Proxy rotation
- [ ] robots.txt parser & respect
- [ ] Recursive depth control for crawler
- [ ] HTML report export
- [ ] SQLite storage backend

---

## 👤 Developer

<div align="center">

**Alcatord (Alca)**

*Cybersecurity · Frontend Dev · Python & C · Web Detective*

[![GitHub](https://img.shields.io/badge/GitHub-Alcatord-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Alcatord)
[![Instagram](https://img.shields.io/badge/Instagram-alca__tord-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://instagram.com/alca_tord)

</div>

---

<div align="center">

*Made with 🖤 by [Alcatord](https://github.com/Alcatord)*

</div>
