#!/usr/bin/env python3
"""
灣聲宮喂官網：每週自動更新節目集數
從 YouTube 四個節目播放清單的 RSS 抓最新完整集數，合併進 data/episodes.json。
只收標題含「#節目名 EPxx」的完整集數（短影音會被排除）。
只用 Python 標準函式庫，不需要安裝任何套件。
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "episodes.json"

PROGRAMS = {
    "showtime": "PLaX14l8p7MqNGkzI3PwyYgDVTsHP-6HYU",  # 哲藝SHOW TIME
    "oldgirls": "PLaX14l8p7MqN3Uo2LS9FZOmwBOQ7eij45",  # 老派少女上線中
    "yong":     "PLaX14l8p7MqNA5O8HCmXSY_BWJJqVJp0t",  # 庸什麼聽音樂
    "backstage": "PLaX14l8p7MqNWGnbw2aKXihl3s0NzTnZd",  # 超後台
}

NS = {
    "a": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}
EP_RE = re.compile(r"[｜|]\s*#[^｜|]*?EP\s*(\d+)\s*$", re.I)


def fetch(playlist_id):
    url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "onesongtalk-site-updater"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return ET.fromstring(r.read())


def parse(root, program):
    out = []
    for e in root.findall("a:entry", NS):
        title = e.findtext("a:title", "", NS).strip()
        m = EP_RE.search(title)
        if not m:
            continue  # 不是完整集數（短影音等）
        vid = e.findtext("yt:videoId", "", NS)
        desc = e.findtext("media:group/media:description", "", NS) or ""
        out.append({
            "id": vid,
            "program": program,
            "ep": int(m.group(1)),
            "title": EP_RE.sub("", title).strip(),
            "published": e.findtext("a:published", "", NS)[:10],
            "summary": desc.strip().split("\n")[0][:120],
            "url": f"https://www.youtube.com/watch?v={vid}",
            "thumb": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
        })
    return out


def main():
    existing = {}
    if DATA.exists():
        for ep in json.loads(DATA.read_text("utf-8")).get("episodes", []):
            existing[ep["id"]] = ep

    added, failed = 0, []
    for program, pid in PROGRAMS.items():
        try:
            for ep in parse(fetch(pid), program):
                if ep["id"] not in existing:
                    added += 1
                existing[ep["id"]] = ep
        except Exception as ex:  # 單一節目失敗不影響其他節目
            failed.append(f"{program}: {ex}")

    eps = sorted(existing.values(), key=lambda x: x["published"], reverse=True)
    latest = eps[0]["published"] if eps else ""
    DATA.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"updated": latest, "episodes": eps}, ensure_ascii=False, indent=1)
    DATA.write_text(payload, "utf-8")
    # 同時輸出 .js 版本，讓網頁直接雙擊打開（file://）也能顯示
    DATA.with_suffix(".js").write_text("window.EPISODES = " + payload + ";\n", "utf-8")
    print(f"共 {len(eps)} 集，新增 {added} 集")
    for f in failed:
        print("抓取失敗 →", f, file=sys.stderr)
    if failed and len(failed) == len(PROGRAMS):
        sys.exit(1)


if __name__ == "__main__":
    main()
