"""Builds the MOTD window pages (English only). One header on every page: [Danyas Servers v] [<server>] [Bans] [Stats].
  page/<id>.html            server tab (mode, add-ons, commands, rules)   <- motd.txt on the server redirects here
  page/stats-<id>[-pN].html top players (OracleStats top.json, 10 per page, 30 players)
  page/bans-<id>[-pN].html  recent bans (OracleBans bans/recent JSON, 15 per page, 100 bans)
IE11/edge friendly, no JS (dropdown = CSS :hover). usage: python pages.py (the Actions cron runs it every 15 min)"""
import glob, html, json, os, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
OS = 'https://GE8EEEF55887CD6-ORACLESTATS.adb.eu-frankfurt-1.oraclecloudapps.com/ords/oraclestats/os/v1/top.json?s=%s&n=30'
BANSJSON = 'https://ge8eeef55887cd6-oraclebans.adb.eu-frankfurt-1.oraclecloudapps.com/ords/oraclebans/ob/v1/bans/recent?limit=100'
e = lambda s: html.escape(str(s), quote=True)
PER_STATS, PER_BANS = 10, 15

RULES = ['Cheats, forbidden scripts and models are prohibited.',
         'Do not spam the voice or text chat.',
         'Do not impersonate the administration.',
         'Do not disrespect the administration.',
         'Do not argue with or dispute admin decisions.',
         'Do not insult other players or provoke conflicts.']

# draft (11-19): mode / add-ons per server, from the server passports; owner to confirm
BASE = 'SourceMod 1.13, OracleBans, OracleStats'
INFO = {
    'dm': ('Deathmatch: instant respawn, free-for-all', BASE),
    'zriot': ('Zombie Riot: survive waves of zombies day by day', BASE),
    'fun': ('MultiMod Fun: minigames and deathrun maps', BASE + ', VIP, shop'),
    'knf': ('Knife Arena: knife-only duels', BASE + ', VIP, knife top'),
    'gg': ('GunGame: advance through weapons with every kill', BASE),
    'rpg': ('RPG Deathmatch: credits, levels and character upgrades', BASE),
    'dd2': ('Dust2 only (de_dust2)', BASE + ', VIP, quake sounds'),
    'zm': ('Zombie:Reloaded: humans vs zombies', BASE + ', shop, Z-Props, betting'),
    'pub': ('Public server (16+)', BASE),
    'test': ('Test server (copy of DM)', BASE),
}
# player commands (11-19, collected by the server chats; only ones not marked "not verified" there). Standard SourceMod ones are omitted.
STATS_CMD = ('!top, !rank, !statsme', 'top players, your rank and your stats')
COMMANDS = {
    'dm': [('guns', 'weapon menu (type it in chat, no "!")'), ('!vip, !class', 'VIP class menu'), ('!viptest', 'free VIP trial, once a week'),
           ('!st', 'who sprayed the spray you look at')],
    'zriot': [],
    'fun': [('!shop', 'shop'), ('!rs', 'reset your score'), ('!settings', 'personal settings'), ('!strafe', 'auto-strafe'),
            ('!topspeed', 'best speeds table'), ('!scout', 'get a scout (deathrun maps, CT)'), ('!comms', 'your mute / gag status')],
    'knf': [('!ktop', 'top knife players'), ('!kme', 'your knife stats'), ('!kbot', 'worst players'), ('!vip', 'VIP menu'),
            ('!viptest', 'free VIP trial'), ('!vipkey <key>', 'activate a VIP key'), ('!cw', 'weapon models menu'), ('!comms', 'your mute / gag status')],
    'gg': [('level', 'your level and weapon'), ('weapons', 'weapons by level'), ('score', 'levels of all players'), ('rules', 'GunGame rules'),
           ('top', 'top players by wins')],
    'rpg': [('rpg, !rpg', 'character upgrades menu'), ('rpgrank', 'your RPG rank'), ('rpgtop', 'RPG top 10'), ('rpgstats', 'your RPG stats'),
            ('frags', 'exchange frags for credits')],
    'dd2': [('!vip', 'VIP menu'), ('!viptest', 'free VIP trial'), ('!vipkey <key>', 'activate a VIP key'), ('!viplist', 'VIP list'),
            ('!rankme', 'RankMe stats menu'), ('!topkills', 'tops: kills, deaths, hs, knife... (!topdeaths, !tophs)'), ('!quake', 'kill sounds menu')],
    'zm': [('!shop', 'shop'), ('!guns', 'weapon menu (in-game money)'), ('!ak, !awp, !m4 ...', 'buy a specific weapon'),
           ('!bet h|z <sum>', 'bet on humans / zombies'), ('!zprops', 'props menu'), ('!zvolume', 'zombie sounds volume'), ('!hitmarker', 'hit marker settings')],
    'pub': [('!menu', 'player menu'), ('!rs', 'reset your score'), ('!sp, !afk', 'go spectate'), ('!admins', 'admins online'), ('!vip', 'VIP menu'),
            ('!viptest', 'free VIP trial'), ('!cw', 'weapon models menu'), ('!quake', 'kill sounds menu'), ('!comms', 'your mute / gag status')],
    'test': [('!menu', 'player menu'), ('!rs', 'reset your score'), ('!sp, !afk', 'go spectate'), ('!admins', 'admins online'), ('!vip', 'VIP menu'),
             ('!viptest', 'free VIP trial')],
}

CSS = ("html,body{margin:0;background:#fff;color:#000;font:13px Verdana,Arial,sans-serif}"
       "table{width:100%;border-collapse:collapse}"
       "td{border:1px solid #aeaeae;padding:2px 6px}.h td{background:#282828;color:#fff;font-weight:bold}.b1{background:#f3f3f3}"
       ".nav{background:#282828;border-bottom:3px solid #aeaeae;height:34px}.nav a,.nav .sv{float:left;display:block;height:34px;line-height:34px;padding:0 18px;"
       "color:#fff;text-decoration:none;font-weight:bold;font-size:13px}.nav a:hover{background:#444}.nav a.on{background:#fff;color:#282828}"
       ".nav .dd{float:left;position:relative}.nav .sv{cursor:default;color:#ffb400}.nav .dd:hover .sv{background:#444}"
       ".nav ul{display:none;position:absolute;left:0;top:34px;margin:0;padding:0;list-style:none;background:#282828;border:1px solid #aeaeae;z-index:9;width:190px}"
       ".nav .dd:hover ul{display:block}.nav li a{float:none;height:26px;line-height:26px;font-weight:normal;padding:0 14px}"
       ".nav li a.on{background:#444;color:#ffb400}"
       "table.info td{vertical-align:top}td.k{width:90px;font-weight:bold}td.c{width:160px;white-space:nowrap;font-weight:bold;font-family:'Courier New',monospace}"
       "table.lay{border:0;margin-top:10px}table.lay>tbody>tr>td{border:0;padding:0 8px;vertical-align:top;width:50%}"
       "table.st{table-layout:fixed;margin-top:0}.st td{overflow:hidden;white-space:nowrap;text-overflow:ellipsis;padding:3px 5px;font-size:11px}"
       ".st .h td{text-align:center}.st td.n{text-align:right}.st td.p{text-align:left}"
       ".sh{font-size:14px;font-weight:bold;padding:8px 2px 4px}.pg{padding:6px 2px;font-size:11px}.pg a,.pg b{margin-right:8px}.wrap{padding:0 10px}")


def pfile(base, pg):
    return base + ('.html' if pg == 1 else '-p%d.html' % pg)


def pager(base, pg, total):
    if total <= 1:
        return ''
    out = ['<div class="pg">']
    if pg > 1:
        out.append('<a href="%s">&laquo; Prev</a>' % pfile(base, pg - 1))
    for i in range(1, total + 1):
        out.append('<b>%d</b>' % i if i == pg else '<a href="%s">%d</a>' % (pfile(base, i), i))
    if pg < total:
        out.append('<a href="%s">Next &raquo;</a>' % pfile(base, pg + 1))
    out.append('</div>')
    return ''.join(out)


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.load(r)
    except Exception as ex:
        print('fetch failed', url[:80], ex)
        return None


def fmt_time(sec):
    m = int(sec) // 60
    return '%dh %dm' % (m // 60, m % 60) if m >= 60 else '%dm' % m


def fmt_dur(m):
    m = int(m or 0)
    if m == 0:
        return 'Permanent'
    if m < 60:
        return '%d min' % m
    if m < 1440:
        return '%d h' % (m // 60)
    return '%d d' % (m // 1440)


def shell(s, servers, tab, body):
    dd = ''.join('<li><a%s href="%s.html">%s</a></li>' % (' class="on"' if x['id'] == s['id'] else '', x['id'], e(x['name']))
                 for x in servers if x['id'] != 'test' or s['id'] == 'test')
    tabs = [('srv', s['id'] + '.html', s['name']), ('bans', 'bans-%s.html' % s['id'], 'Bans'), ('stats', 'stats-%s.html' % s['id'], 'Stats')]
    nav = ''.join('<a%s href="%s">%s</a>' % (' class="on"' if t == tab else '', h, e(n)) for t, h, n in tabs)
    return ('<!DOCTYPE html><html lang="en"><head><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta charset="utf-8">'
            '<title>Danyas Server</title><style>%s</style></head><body>'
            '<div class="nav"><div class="dd"><span class="sv">Danyas Servers &#9662;</span><ul>%s</ul></div>%s</div>'
            '<div class="wrap">%s</div></body></html>' % (CSS, dd, nav, body))


def server_body(s):
    mode, addons = INFO[s['id']]
    rows = ['<tr class="b1"><td class="k">Mode</td><td>%s</td></tr>' % e(mode),
            '<tr><td class="k">Add-ons</td><td>%s</td></tr>' % e(addons),
            '<tr class="b1"><td class="k">Address</td><td>%s</td></tr>' % e(s['addr'])]
    left = '<div class="sh">Server</div><table class="info">%s</table>' % ''.join(rows)
    left += '<div class="sh">Rules</div><table>%s</table>' % ''.join('<tr class="b1"><td>%s</td></tr>' % e(x) for x in RULES)
    cmds = ([STATS_CMD] if s['id'] != 'zriot' else [('!top, !rank', 'top players and your rank')]) + COMMANDS.get(s['id'], [])
    right = '<div class="sh">Commands</div><table class="info">%s</table>' % ''.join(
        '<tr class="%s"><td class="c">%s</td><td>%s</td></tr>' % ('b1' if i % 2 == 0 else '', e(k), e(d)) for i, (k, d) in enumerate(cmds))
    return '<table class="lay"><tr><td>%s</td><td>%s</td></tr></table>' % (left, right)


def stats_body(s, d, pg):
    if not d:
        return '<div class="sh">Stats are temporarily unavailable.</div>'
    pl = d['players']
    total = max(1, (len(pl) + PER_STATS - 1) // PER_STATS)
    rows = ['<div class="sh">Top players: %s</div>' % e(d['name']),
            '<table class="st"><colgroup><col width="32"><col><col width="56"><col width="52"><col width="60"><col width="62"><col width="52"><col width="64"></colgroup>'
            '<tr class="h"><td>#</td><td>Player</td><td>Skill</td><td>Kills</td><td>Deaths</td><td>K/D</td><td>HS%</td><td>Time</td></tr>']
    for i, p in enumerate(pl[(pg - 1) * PER_STATS:pg * PER_STATS]):
        hs = int(round(100.0 * p['hs'] / p['kills'])) if p['kills'] else 0
        rows.append('<tr class="%s"><td class="n">%d</td><td class="p" title="%s">%s</td><td class="n">%d</td><td class="n">%d</td><td class="n">%d</td><td class="n">%.2f</td><td class="n">%d</td><td class="n">%s</td></tr>'
                    % ('b1' if i % 2 == 0 else '', p['pos'], e(p['name']), e(p['name']), p['skill'], p['kills'], p['deaths'], p['kd'], hs, fmt_time(p['time'])))
    rows.append('</table>')
    rows.append(pager('stats-' + s['id'], pg, total))
    if not pl:
        rows.append('<div class="sh" style="font-weight:normal">No ranked players yet.</div>')
    return ''.join(rows)


def bans_body(s, bans, pg):
    if bans is None:
        return '<div class="sh">Ban list is temporarily unavailable.</div>'
    total = max(1, (len(bans) + PER_BANS - 1) // PER_BANS)
    rows = []
    for i, b in enumerate(bans[(pg - 1) * PER_BANS:pg * PER_BANS]):
        st = {'active': 'Active', 'unbanned': 'Unbanned', 'expired': 'Expired'}.get(b.get('status'), '')
        dt = time.strftime('%Y-%m-%d', time.gmtime(b['created'])) if b.get('created') else ''
        rows.append('<tr class="%s"><td class="p" title="%s">%s</td><td class="p" title="%s">%s</td><td>%s</td><td>%s</td><td>%s</td><td class="p">%s</td></tr>'
                    % ('b1' if i % 2 == 0 else '', e(b.get('name', '')), e(b.get('name', '')), e(b.get('reason', '')), e(b.get('reason', '')),
                       dt, fmt_dur(b.get('duration_min')), st, e(b.get('server', ''))))
    return ('<div class="sh">Recent bans (%d)</div>'
            '<table class="st"><colgroup><col width="20%%"><col><col width="84"><col width="78"><col width="80"><col width="92"></colgroup>'
            '<tr class="h"><td>Player</td><td>Reason</td><td>Date</td><td>Length</td><td>Status</td><td>Server</td></tr>%s</table>%s'
            % (len(bans), ''.join(rows), pager('bans-' + s['id'], pg, total)))


def w(name, text):
    with open(os.path.join(HERE, 'page', name), 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def main():
    cfg = json.load(open(os.path.join(HERE, 'pages.json'), encoding='utf-8'))
    servers = cfg['servers']
    os.makedirs(os.path.join(HERE, 'page'), exist_ok=True)
    for f in glob.glob(os.path.join(HERE, 'page', '*-p[0-9]*.html')):
        os.remove(f)  # generated pagination pages, rebuilt below
    bj = fetch(BANSJSON)
    bans = bj['bans'] if bj and isinstance(bj.get('bans'), list) else None
    for s in servers:
        w(s['id'] + '.html', shell(s, servers, 'srv', server_body(s)))
        d = fetch(OS % s['stats'])
        d = d if d and 'players' in d and d.get('name') else None
        n = max(1, (len(d['players']) + PER_STATS - 1) // PER_STATS) if d else 1
        for pg in range(1, n + 1):
            w(pfile('stats-' + s['id'], pg), shell(s, servers, 'stats', stats_body(s, d, pg)))
        n = max(1, (len(bans) + PER_BANS - 1) // PER_BANS) if bans else 1
        for pg in range(1, n + 1):
            w(pfile('bans-' + s['id'], pg), shell(s, servers, 'bans', bans_body(s, bans, pg)))
        print('%-6s ok' % s['id'])


main()
