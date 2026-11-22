#!/usr/bin/env python3
"""Pull PGA TOUR hole-by-hole scoring averages (course stats) for the current
tournament and write data/holes.json for the league site's projected scores."""
import json, re, sys, time, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-US,en;q=0.9"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")

def next_data(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("no __NEXT_DATA__ on page")
    return json.loads(m.group(1))

def find(o, pred):
    if isinstance(o, dict):
        if pred(o):
            return o
        for v in o.values():
            r = find(v, pred)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, pred)
            if r is not None:
                return r
    return None

def holes(stats):
    out = {}
    for h in stats or []:
        n = h.get("courseHoleNum")
        try:
            if n:
                out[str(n)] = [int(h.get("parValue")), round(float(h.get("scoringAverage")), 3)]
        except (TypeError, ValueError):
            pass
    return out

def main():
    lb = get("https://www.pgatour.com/leaderboard")
    paths = re.findall(r'/tournaments/(\d{4})/([a-z0-9-]+)/(R\d{7})', lb)
    if not paths:
        raise SystemExit("could not find the current tournament on the leaderboard page")
    yr, slug, tid = paths[0]
    data = next_data(get(f"https://www.pgatour.com/tournaments/{yr}/{slug}/{tid}/course-stats"))
    cs = find(data, lambda o: isinstance(o.get("courses"), list) and o["courses"] and isinstance(o["courses"][0], dict) and "roundHoleStats" in o["courses"][0])
    if not cs:
        raise SystemExit("no course stats on page")
    name = slug.replace("-", " ").title()
    courses = []
    for c in cs["courses"]:
        rounds, allr = {}, {}
        for r in c.get("roundHoleStats") or []:
            hs = holes(r.get("holeStats"))
            if r.get("roundNum") is None:
                allr = hs
            else:
                rounds[str(r["roundNum"])] = hs
        courses.append({"id": c.get("courseId"), "name": c.get("courseName"), "code": c.get("courseCode"),
                        "par": c.get("par"), "host": bool(c.get("hostCourse")), "all": allr, "rounds": rounds})
    if not any(c["all"] for c in courses):
        raise SystemExit("course stats empty; leaving existing file")
    out = {"tournamentId": tid, "slug": slug, "name": name, "source": "pgatour.com course stats",
           "updatedAt": int(time.time() * 1000), "courses": courses}
    try:
        old = json.load(open("data/holes.json"))
        if old.get("tournamentId") == tid and old.get("courses") == courses:
            print("no change"); return
    except Exception:
        pass
    json.dump(out, open("data/holes.json", "w"), separators=(",", ":"))
    print("wrote", tid, slug, len(courses), "courses")

if __name__ == "__main__":
    main()
