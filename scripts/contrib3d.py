#!/usr/bin/env python3
"""Isometric 3D contribution calendar for a GitHub user, as SVG, with no dependencies but the gh CLI.
Same file names as the github-profile-3d-contrib Action; refreshed daily by scripts/refresh.sh under launchd.
Usage: scripts/contrib3d.py JT5D profile-3d-contrib"""
import datetime, json, math, subprocess, sys, os
user, out = sys.argv[1], sys.argv[2]
q = 'query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount weekday}}}}}}'
cal = json.loads(subprocess.check_output(['gh', 'api', 'graphql', '-f', f'query={q}', '-f', f'u={user}'], env={**os.environ, 'NO_COLOR': '1', 'CLICOLOR_FORCE': '0', 'GH_FORCE_TTY': ''}))['data']['user']['contributionsCollection']['contributionCalendar']
cells = [(w, d['weekday'], d['contributionCount']) for w, wk in enumerate(cal['weeks']) for d in wk['contributionDays']]
top = max(c for _, _, c in cells) or 1
S, H = 10, 60                                  # cell size, tallest bar
cx, cy = math.cos(math.pi / 6) * S, math.sin(math.pi / 6) * S
def iso(x, y, z): return (x - y) * cx, (x + y) * cy - z
def pts(ps): return ' '.join(f'{a:.1f},{b:.1f}' for a, b in ps)
THEMES = {'profile-green.svg': ('#ffffff', '#24292f', ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']),
          'profile-night-green.svg': ('#0d1117', '#c9d1d9', ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353'])}
def shade(hexc, k): r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5)); return '#%02x%02x%02x' % tuple(max(0, min(255, int(v * k))) for v in (r, g, b))
os.makedirs(out, exist_ok=True)
for name, (bg, fg, scale) in THEMES.items():
    polys = []
    for w, d, c in sorted(cells, key=lambda t: (t[0] + t[1], t[0])):
        lvl = 0 if c == 0 else 1 + min(3, int(4 * math.log1p(c) / math.log1p(top) - 1e-9))
        h = 2 + (H * math.log1p(c) / math.log1p(top) if c else 0)
        col = scale[lvl]
        x, y = w, d
        tops = [iso(x, y, h), iso(x + 1, y, h), iso(x + 1, y + 1, h), iso(x, y + 1, h)]
        left = [iso(x, y + 1, h), iso(x + 1, y + 1, h), iso(x + 1, y + 1, 0), iso(x, y + 1, 0)]
        right = [iso(x + 1, y, h), iso(x + 1, y + 1, h), iso(x + 1, y + 1, 0), iso(x + 1, y, 0)]
        polys += [f'<polygon points="{pts(left)}" fill="{shade(col, .72)}"/>', f'<polygon points="{pts(right)}" fill="{shade(col, .86)}"/>', f'<polygon points="{pts(tops)}" fill="{col}"/>']
    xs = [iso(x, y, 0)[0] for x in (0, 54) for y in (0, 7)]
    minx, maxx, miny, maxy = min(xs) - 10, max(xs) + 10, -H - 10, iso(54, 7, 0)[1] + 10
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx:.0f} {miny - 30:.0f} {maxx - minx:.0f} {maxy - miny + 30:.0f}" role="img" aria-label="{cal["totalContributions"]} contributions in the last year">'
           f'<rect x="{minx:.0f}" y="{miny - 30:.0f}" width="100%" height="100%" fill="{bg}"/>'
           f'<text x="{minx + 16:.0f}" y="{miny - 8:.0f}" fill="{fg}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif" font-size="14">{cal["totalContributions"]:,} contributions in the last year · updated {datetime.date.today()}</text>'
           + ''.join(polys) + '</svg>')
    open(os.path.join(out, name), 'w').write(svg)
print(cal['totalContributions'], 'contributions,', len(cells), 'days')
