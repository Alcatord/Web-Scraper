#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║            WebScraper — Pure Python Scraper             ║
║        by Alcatord | github.com/Alcatord                ║
║   No external dependencies - pure Python stdlib only    ║
╚══════════════════════════════════════════════════════════╝
"""

import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import html.parser
import json
import csv
import os
import sys
import time
import re
import ssl
import threading
import concurrent.futures
from datetime import datetime

# ─────────────────────────────────────────────
#  COLORS
# ─────────────────────────────────────────────
R   = "\033[91m"
G   = "\033[92m"
Y   = "\033[93m"
B   = "\033[94m"
M   = "\033[95m"
C   = "\033[96m"
W   = "\033[97m"
DIM = "\033[2m"
BOLD= "\033[1m"
RST = "\033[0m"

# ─────────────────────────────────────────────
#  BANNER
# ─────────────────────────────────────────────
def banner():
    print(f"""
{C}{BOLD}
 ██╗    ██╗███████╗██████╗     ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
 ██║    ██║██╔════╝██╔══██╗    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
 ██║ █╗ ██║█████╗  ██████╔╝    ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
 ██║███╗██║██╔══╝  ██╔══██╗    ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
 ╚███╔███╔╝███████╗██████╔╝    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
  ╚══╝╚══╝ ╚══════╝╚═════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
{RST}
{DIM}          Web Scraper — Pure Python | by Alcatord{RST}
{Y}══════════════════════════════════════════════════════════════════════════════════════{RST}
""")

# ─────────────────────────────────────────────
#  HTML PARSER — extracts structured data
# ─────────────────────────────────────────────
class PageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.title        = ""
        self.links        = []
        self.images       = []
        self.headings     = []
        self.paragraphs   = []
        self.meta         = {}
        self.emails       = []
        self.tables       = []
        self.forms        = []

        self._in_title    = False
        self._in_heading  = False
        self._in_para     = False
        self._cur_heading = ""
        self._cur_para    = ""
        self._cur_tag     = ""
        self._cur_table   = None
        self._cur_row     = None
        self._cur_cell    = ""
        self._in_cell     = False
        self._in_form     = False
        self._cur_form    = None

    # ── Tag open ────────────────────────────
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._cur_tag = tag

        if tag == "title":
            self._in_title = True

        elif tag in ("h1","h2","h3","h4","h5","h6"):
            self._in_heading  = True
            self._cur_heading = ""

        elif tag == "p":
            self._in_para  = True
            self._cur_para = ""

        elif tag == "a":
            href = a.get("href","").strip()
            text = a.get("title", "") or ""
            if href:
                self.links.append({"href": href, "title": text})
            # email in href
            if href.startswith("mailto:"):
                self.emails.append(href.replace("mailto:","").strip())

        elif tag == "img":
            self.images.append({
                "src": a.get("src",""),
                "alt": a.get("alt",""),
                "width":  a.get("width",""),
                "height": a.get("height",""),
            })

        elif tag == "meta":
            name    = a.get("name","") or a.get("property","")
            content = a.get("content","")
            if name and content:
                self.meta[name] = content

        elif tag == "table":
            self._cur_table = []

        elif tag == "tr":
            self._cur_row = []

        elif tag in ("td","th"):
            self._in_cell  = True
            self._cur_cell = ""

        elif tag == "form":
            self._in_form  = True
            self._cur_form = {
                "action": a.get("action",""),
                "method": a.get("method","GET"),
                "inputs": []
            }

        elif tag == "input" and self._in_form:
            self._cur_form["inputs"].append({
                "name":  a.get("name",""),
                "type":  a.get("type","text"),
                "value": a.get("value",""),
            })

    # ── Tag close ───────────────────────────
    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

        elif tag in ("h1","h2","h3","h4","h5","h6"):
            if self._cur_heading.strip():
                self.headings.append({
                    "level": int(tag[1]),
                    "text":  self._cur_heading.strip()
                })
            self._in_heading = False

        elif tag == "p":
            if self._cur_para.strip():
                self.paragraphs.append(self._cur_para.strip())
            self._in_para = False

        elif tag in ("td","th"):
            if self._cur_row is not None:
                self._cur_row.append(self._cur_cell.strip())
            self._in_cell = False

        elif tag == "tr":
            if self._cur_table is not None and self._cur_row:
                self._cur_table.append(self._cur_row)
            self._cur_row = None

        elif tag == "table":
            if self._cur_table:
                self.tables.append(self._cur_table)
            self._cur_table = None

        elif tag == "form":
            if self._cur_form:
                self.forms.append(self._cur_form)
            self._in_form = False
            self._cur_form = None

    # ── Text ────────────────────────────────
    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_heading:
            self._cur_heading += data
        if self._in_para:
            self._cur_para += data
        if self._in_cell:
            self._cur_cell += data
        # email regex in text
        found = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", data)
        self.emails.extend(found)

    def get_emails(self):
        return list(set(self.emails))

# ─────────────────────────────────────────────
#  HTTP FETCHER
# ─────────────────────────────────────────────
class Fetcher:
    def __init__(self, delay=1.0, timeout=10):
        self.delay   = delay
        self.timeout = timeout
        self.session = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
            urllib.request.HTTPRedirectHandler(),
        )
        self.session.addheaders = [
            ("User-Agent",
             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
             "AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/120.0.0.0 Safari/537.36"),
            ("Accept-Language", "en-US,en;q=0.9"),
            ("Accept", "text/html,application/xhtml+xml,*/*;q=0.8"),
        ]
        self._last_request = 0

    def fetch(self, url):
        """Fetch a URL and return (html_text, status_code, headers)."""
        # Rate limiting
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        # Fix URL
        if not url.startswith("http"):
            url = "https://" + url

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_NONE

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                self._last_request = time.time()
                raw     = resp.read()
                charset = "utf-8"
                ct      = resp.headers.get("Content-Type","")
                m = re.search(r"charset=([\w\-]+)", ct)
                if m:
                    charset = m.group(1)
                html_text = raw.decode(charset, errors="replace")
                return html_text, resp.status, dict(resp.headers)
        except urllib.error.HTTPError as e:
            return None, e.code, {}
        except Exception as e:
            return None, 0, {"error": str(e)}

# ─────────────────────────────────────────────
#  LINK CRAWLER (BFS)
# ─────────────────────────────────────────────
def crawl(start_url, max_pages=10, delay=1.0, same_domain=True):
    """BFS crawl — returns list of {url, data} dicts."""
    fetcher   = Fetcher(delay=delay)
    visited   = set()
    queue     = [start_url]
    results   = []
    base_host = urllib.parse.urlparse(start_url).netloc

    print(f"\n{Y}[*]{RST} Crawling {C}{start_url}{RST} (max {max_pages} pages)\n")

    while queue and len(results) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        print(f"  {B}[→]{RST} {url[:70]}", flush=True)
        html_text, status, headers = fetcher.fetch(url)

        if not html_text:
            print(f"       {R}✗ status {status}{RST}")
            continue

        print(f"       {G}✓ {status} — {len(html_text)} bytes{RST}")

        parser = PageParser()
        try:
            parser.feed(html_text)
        except Exception:
            pass

        page_data = {
            "url":        url,
            "status":     status,
            "title":      parser.title.strip(),
            "meta":       parser.meta,
            "headings":   parser.headings,
            "paragraphs": parser.paragraphs,
            "links":      parser.links,
            "images":     parser.images,
            "emails":     parser.get_emails(),
            "tables":     parser.tables,
            "forms":      parser.forms,
            "size_bytes": len(html_text),
            "scraped_at": datetime.now().isoformat(),
        }
        results.append(page_data)

        # Enqueue discovered links
        for link in parser.links:
            href = link["href"].strip()
            full = urllib.parse.urljoin(url, href)
            parsed = urllib.parse.urlparse(full)
            # same domain filter
            if same_domain and parsed.netloc != base_host:
                continue
            # only http(s)
            if parsed.scheme not in ("http","https"):
                continue
            if full not in visited:
                queue.append(full)

    return results

# ─────────────────────────────────────────────
#  TARGETED SCRAPERS
# ─────────────────────────────────────────────
def scrape_single(url, delay=1.0):
    """Scrape a single URL in detail."""
    fetcher   = Fetcher(delay=delay)
    html_text, status, headers = fetcher.fetch(url)

    if not html_text:
        print(f"  {R}✗ Failed — HTTP {status}{RST}")
        return None

    parser = PageParser()
    parser.feed(html_text)

    return {
        "url":        url,
        "status":     status,
        "title":      parser.title.strip(),
        "meta":       parser.meta,
        "headings":   parser.headings,
        "paragraphs": parser.paragraphs,
        "links":      parser.links,
        "images":     parser.images,
        "emails":     parser.get_emails(),
        "tables":     parser.tables,
        "forms":      parser.forms,
        "size_bytes": len(html_text),
        "scraped_at": datetime.now().isoformat(),
        "headers":    {k: v for k,v in headers.items()
                       if k.lower() in ("server","x-powered-by","content-type","x-frame-options")},
    }

# ─────────────────────────────────────────────
#  DISPLAY
# ─────────────────────────────────────────────
def display_page(data):
    sep = f"{Y}{'═'*70}{RST}"
    print(f"\n{sep}")
    print(f"  {BOLD}{G}URL   :{RST} {C}{data['url']}{RST}")
    print(f"  {DIM}Title :{RST} {BOLD}{data['title']}{RST}")
    print(f"  {DIM}Status:{RST} {G}{data['status']}{RST}  |  {DIM}Size:{RST} {data['size_bytes']:,} bytes")
    print(f"  {DIM}Scraped:{RST} {data['scraped_at']}")
    print(sep)

    # Meta tags
    if data["meta"]:
        print(f"\n  {M}{BOLD}META TAGS{RST}")
        for k, v in list(data["meta"].items())[:8]:
            print(f"    {DIM}{k:<20}{RST} {v[:60]}")

    # Server headers
    if data.get("headers"):
        print(f"\n  {M}{BOLD}SERVER INFO{RST}")
        for k, v in data["headers"].items():
            print(f"    {DIM}{k:<20}{RST} {v}")

    # Headings
    if data["headings"]:
        print(f"\n  {M}{BOLD}HEADINGS ({len(data['headings'])}){RST}")
        for h in data["headings"][:10]:
            indent = "  " * (h["level"] - 1)
            lvl_color = [C, G, Y, M, B, W][min(h["level"]-1, 5)]
            print(f"    {indent}{lvl_color}H{h['level']}{RST} {h['text'][:70]}")

    # Paragraphs
    if data["paragraphs"]:
        print(f"\n  {M}{BOLD}PARAGRAPHS ({len(data['paragraphs'])}){RST}")
        for p in data["paragraphs"][:5]:
            print(f"    {DIM}▸{RST} {p[:100]}...")

    # Links
    if data["links"]:
        print(f"\n  {M}{BOLD}LINKS ({len(data['links'])}){RST}")
        for lnk in data["links"][:8]:
            print(f"    {B}→{RST} {lnk['href'][:70]}")
        if len(data["links"]) > 8:
            print(f"    {DIM}... and {len(data['links'])-8} more{RST}")

    # Images
    if data["images"]:
        print(f"\n  {M}{BOLD}IMAGES ({len(data['images'])}){RST}")
        for img in data["images"][:5]:
            alt = f"  [{img['alt']}]" if img["alt"] else ""
            print(f"    {C}🖼 {RST}{img['src'][:60]}{DIM}{alt}{RST}")

    # Emails
    if data["emails"]:
        print(f"\n  {M}{BOLD}EMAILS FOUND ({len(data['emails'])}){RST}")
        for em in data["emails"]:
            print(f"    {R}✉ {RST}{em}")

    # Tables
    if data["tables"]:
        print(f"\n  {M}{BOLD}TABLES ({len(data['tables'])}){RST}")
        for i, table in enumerate(data["tables"][:2]):
            print(f"    {DIM}Table {i+1} — {len(table)} rows × {max(len(r) for r in table)} cols{RST}")
            for row in table[:3]:
                print(f"      {' | '.join(str(c)[:15] for c in row)}")

    # Forms
    if data["forms"]:
        print(f"\n  {M}{BOLD}FORMS ({len(data['forms'])}){RST}")
        for f in data["forms"]:
            print(f"    {Y}ACTION:{RST} {f['action']}  {DIM}METHOD:{RST} {f['method']}")
            for inp in f["inputs"]:
                print(f"      {DIM}[{inp['type']}]{RST} name={inp['name']}")

    print(f"\n{sep}\n")

# ─────────────────────────────────────────────
#  EXPORT
# ─────────────────────────────────────────────
def export_json(results, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  {G}✓ JSON saved:{RST} {C}{filename}{RST}")

def export_csv_links(results, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_url", "link_href", "link_title"])
        for page in results:
            for lnk in page["links"]:
                writer.writerow([page["url"], lnk["href"], lnk.get("title","")])
    print(f"  {G}✓ Links CSV saved:{RST} {C}{filename}{RST}")

def export_csv_emails(results, filename):
    emails = []
    for page in results:
        for em in page["emails"]:
            emails.append({"email": em, "found_on": page["url"]})
    emails = list({e["email"]: e for e in emails}.values())  # deduplicate
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email","found_on"])
        writer.writeheader()
        writer.writerows(emails)
    print(f"  {G}✓ Emails CSV saved:{RST} {C}{filename}{RST}")

# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────
def main():
    banner()

    print(f"  {Y}Mode:{RST}")
    print(f"    {G}1{RST}) Single page — deep scrape one URL")
    print(f"    {G}2{RST}) Crawler     — BFS multi-page scrape")
    print(f"    {G}3{RST}) Bulk URLs   — scrape a list from file")

    try:
        mode = input(f"\n  Choice [1]: ").strip() or "1"
    except KeyboardInterrupt:
        sys.exit(0)

    results = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── Mode 1: Single ──────────────────────
    if mode == "1":
        try:
            url = input(f"  {Y}URL:{RST} ").strip()
        except KeyboardInterrupt:
            sys.exit(0)
        if not url:
            print(f"  {R}No URL provided.{RST}")
            sys.exit(1)

        print(f"\n{Y}[*]{RST} Scraping {C}{url}{RST} ...\n")
        data = scrape_single(url)
        if data:
            display_page(data)
            results = [data]

    # ── Mode 2: Crawler ─────────────────────
    elif mode == "2":
        try:
            url   = input(f"  {Y}Start URL:{RST} ").strip()
            pages = input(f"  {Y}Max pages [{10}]:{RST} ").strip() or "10"
            delay = input(f"  {Y}Delay between requests (sec) [1]:{RST} ").strip() or "1"
            same  = input(f"  {Y}Same domain only? [Y/n]:{RST} ").strip().lower()
        except KeyboardInterrupt:
            sys.exit(0)

        same_domain = same != "n"
        results = crawl(url, max_pages=int(pages), delay=float(delay), same_domain=same_domain)

        print(f"\n{Y}[*]{RST} Scraped {G}{len(results)}{RST} pages\n")
        for data in results:
            display_page(data)

    # ── Mode 3: Bulk ────────────────────────
    elif mode == "3":
        try:
            fpath = input(f"  {Y}File path (one URL per line):{RST} ").strip()
        except KeyboardInterrupt:
            sys.exit(0)

        if not os.path.exists(fpath):
            print(f"  {R}File not found: {fpath}{RST}")
            sys.exit(1)

        with open(fpath) as f:
            urls = [l.strip() for l in f if l.strip()]

        try:
            delay = float(input(f"  {Y}Delay (sec) [1]:{RST} ").strip() or "1")
        except Exception:
            delay = 1.0

        fetcher = Fetcher(delay=delay)
        print(f"\n{Y}[*]{RST} Bulk scraping {len(urls)} URLs...\n")

        for url in urls:
            data = scrape_single(url, delay=delay)
            if data:
                display_page(data)
                results.append(data)

    # ── Export ──────────────────────────────
    if results:
        print(f"\n{Y}[*]{RST} Export options:\n")
        print(f"    {G}1{RST}) JSON (full data)")
        print(f"    {G}2{RST}) CSV  (links only)")
        print(f"    {G}3{RST}) CSV  (emails only)")
        print(f"    {G}4{RST}) All of the above")
        print(f"    {G}5{RST}) Skip")

        try:
            exp = input(f"\n  Choice [1]: ").strip() or "1"
        except KeyboardInterrupt:
            exp = "5"

        domain = urllib.parse.urlparse(results[0]["url"]).netloc.replace(".", "_")

        if exp in ("1","4"):
            export_json(results, f"scrape_{domain}_{ts}.json")
        if exp in ("2","4"):
            export_csv_links(results, f"links_{domain}_{ts}.csv")
        if exp in ("3","4"):
            export_csv_emails(results, f"emails_{domain}_{ts}.csv")

        # Summary
        total_links  = sum(len(r["links"])  for r in results)
        total_images = sum(len(r["images"]) for r in results)
        total_emails = len(set(e for r in results for e in r["emails"]))
        total_tables = sum(len(r["tables"]) for r in results)

        print(f"\n{Y}{'═'*50}{RST}")
        print(f"  {BOLD}{C}SUMMARY{RST}")
        print(f"{Y}{'═'*50}{RST}")
        print(f"  {DIM}Pages scraped :{RST} {G}{len(results)}{RST}")
        print(f"  {DIM}Links found   :{RST} {Y}{total_links}{RST}")
        print(f"  {DIM}Images found  :{RST} {Y}{total_images}{RST}")
        print(f"  {DIM}Emails found  :{RST} {R}{total_emails}{RST}")
        print(f"  {DIM}Tables found  :{RST} {Y}{total_tables}{RST}")
        print(f"{Y}{'═'*50}{RST}")

    print(f"\n  {DIM}WebScraper by Alcatord — github.com/Alcatord{RST}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {R}[!] Interrupted.{RST}\n")
        sys.exit(0)
