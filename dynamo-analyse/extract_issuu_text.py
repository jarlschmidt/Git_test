#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulls the raw searchable-text layer out of an issuu.com publication and dumps
cleaned, readable text fragments to stdout (or a file).

issuu's reader stores a per-page "text info" blob (protobuf, undocumented
schema) that contains every word/line issuu indexed for search — including
full article body text, not just the cover. We don't have the .proto schema,
so instead of parsing the protobuf structure properly, we just scan the raw
bytes for runs of printable Danish/English text (regex over decoded UTF-8) —
crude, but the actual sentences come through clean; only a minority of
fragments are protobuf-structure noise that happens to also be printable.

Usage: python3 extract_issuu_text.py <issuu_user>/<issuu_docname> [out.txt]
Example: python3 extract_issuu_text.py dtudk/dynamo_55
"""
import sys, re, json, urllib.request, gzip, io

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept-Encoding": "gzip",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
        return raw

def get_text_info_uri(user_doc):
    url = f"https://reader3.isu.pub/{user_doc}/reader3_4.json"
    data = json.loads(fetch(url))
    if data.get("error"):
        raise RuntimeError(f"reader3 error for {user_doc}: {data}")
    doc = data["document"]
    return "https://" + doc["textInfo"]["uri"], doc.get("pages", [])

FRAGMENT_RE = re.compile(r"[A-Za-zÆØÅæøåÉé0-9 ,.\-:;!?()%/\"'&+]{9,}")
# fragments that are almost certainly protobuf-structure noise, not real text:
# no vowels, or no lowercase+uppercase word-like pattern
def looks_like_real_text(s):
    s = s.strip()
    if len(s) < 9:
        return False
    letters = sum(c.isalpha() for c in s)
    if letters < 6:
        return False
    vowels = sum(c.lower() in "aeiouyæøå" for c in s)
    if vowels < max(2, letters // 6):
        return False
    return True

def extract_text(user_doc):
    uri, pages = get_text_info_uri(user_doc)
    raw = fetch(uri)
    text = raw.decode("utf-8", errors="ignore")
    frags = FRAGMENT_RE.findall(text)
    good = [f.strip() for f in frags if looks_like_real_text(f)]
    # de-dup consecutive repeats, join with newlines
    out = []
    prev = None
    for f in good:
        if f != prev:
            out.append(f)
        prev = f
    return "\n".join(out), len(pages)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    user_doc = sys.argv[1]
    text, npages = extract_text(user_doc)
    out = f"=== {user_doc} ({npages} pages) ===\n{text}\n"
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Wrote {sys.argv[2]} ({len(text)} chars, {npages} pages)")
    else:
        print(out)
