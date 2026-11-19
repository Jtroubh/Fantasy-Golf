"""Nightly: download the Official World Golf Ranking and write owgr.json for the site."""
import json, re, time, unicodedata, urllib.request

URL = ("https://apiweb.owgr.com/api/owgr/rankings/getRankings?regionId=0&pageSize=10000"
       "&pageNumber=1&countryId=0&sortString=Rank+ASC")

def slug(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'^-+|-+$', '', re.sub(r'[^a-z0-9]+', '-', s)) or 'x'

def base(s):
    return re.sub(r'\s+', ' ', re.sub(r'\s*\([^)]*\)', '', s)).strip()

req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
data = json.load(urllib.request.urlopen(req, timeout=60))
rows = data['rankingsList']
raw = []
for x in rows:
    p = x['player']
    raw.append(dict(rank=int(x['rank']), name=(p.get('fullName') or '').strip(),
                    ctry=((p.get('country') or {}).get('name') or ''),
                    lw=x.get('lastWeekRank'), am=bool(p.get('isAmateur')) or bool(re.search(r'\(\s*am\s*\)', p.get('fullName') or '', re.I))))
cnt = {}
for p in raw:
    k = slug(base(p['name'])); cnt[k] = cnt.get(k, 0) + 1
seen, players = set(), []
for p in sorted(raw, key=lambda p: p['rank']):
    clean = re.sub(r'\s*\(\s*am\s*\)', '', p['name'], flags=re.I)
    n = re.sub(r'\s+', ' ', re.sub(r'\s*\(', ' (', clean)).strip() if cnt[slug(base(p['name']))] > 1 else base(p['name'])
    if slug(n) in seen:
        n = f"{n} ({p['rank']})"
    seen.add(slug(n))
    players.append([p['rank'], n, p['ctry'], p['lw'] if isinstance(p['lw'], int) else None, 1 if p['am'] else 0])
if len(players) < 3000:
    raise SystemExit(f"Only {len(players)} players returned; not updating.")
as_of = time.strftime('%b %d, %Y')
json.dump({'meta': {'count': len(players), 'asOf': as_of, 'importedAt': int(time.time() * 1000), 'source': 'owgr.com'},
           'players': players}, open('owgr.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print(len(players), players[0])
