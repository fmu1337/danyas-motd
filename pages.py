"""Builds page/<id>.html - the MOTD window content for every server (motd.txt on the server = a redirect to this page).
Style C (old HLstatsX InGame look). IE11/edge friendly (plain v34 client: no JS), ClientMod = Chromium.
usage: python pages.py"""
import html, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
STATS = 'https://GE8EEEF55887CD6-ORACLESTATS.adb.eu-frankfurt-1.oraclecloudapps.com/ords/oraclestats/os/v1/top.html?s=%s'
BANS = 'https://ge8eeef55887cd6-oraclebans.adb.eu-frankfurt-1.oraclecloudapps.com/ords/r/oraclebans/oraclebans/home'
e = lambda s: html.escape(str(s), quote=True)

CSS = ("html,body{margin:0;background:#fff;color:#000;font:13px Verdana,Arial,sans-serif}"
       ".hb{background:#282828;color:#fff;padding:12px 16px;border-bottom:3px solid #aeaeae}"
       ".n{font-size:22px;font-weight:bold;letter-spacing:1px}.a{color:#aeaeae;font-size:14px;margin-top:3px}"
       ".w{padding:0 12px 10px}table{width:100%;border-collapse:collapse;margin-top:8px}"
       "td{border:1px solid #aeaeae;padding:4px 8px}.h td{background:#282828;color:#fff;font-weight:bold}"
       ".b1{background:#f3f3f3}td.k{width:150px;font-weight:bold;font-family:'Courier New',monospace}"
       ".bt{margin-top:12px}.bt a{display:inline-block;margin-right:10px;padding:8px 18px;background:#282828;color:#fff;"
       "text-decoration:none;font-weight:bold;border-bottom:3px solid #aeaeae}.bt a:hover{background:#444}")

def page(cfg, s):
    o = ['<!DOCTYPE html><html><head><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta charset="utf-8">'
         '<title>Danyas Server</title><style>%s</style></head><body>' % CSS,
         '<div class="hb"><div class="n">Danyas Server &middot; %s</div><div class="a">%s</div></div><div class="w">' % (e(s['name']), e(s['addr']))]
    if s.get('special'):
        o.append('<table><tr class="h"><td colspan="2">Особенности сервера</td></tr>')
        for i, (k, d) in enumerate(s['special']):
            o.append('<tr class="%s"><td class="k">%s</td><td>%s</td></tr>' % ('b1' if i % 2 == 0 else '', e(k), e(d)))
        o.append('</table>')
    o.append('<table><tr class="h"><td>Основные правила поведения на сервере</td></tr>')
    for x in cfg['rules']:
        o.append('<tr class="b1"><td>%s</td></tr>' % e(x))
    o.append('</table>')
    o.append('<div class="bt"><a href="%s">Топ игроков</a><a href="%s">Список банов</a></div></div></body></html>'
             % (e(STATS % s['stats']), e(BANS)))
    return ''.join(o)

def main():
    cfg = json.load(open(os.path.join(HERE, 'pages.json'), encoding='utf-8'))
    os.makedirs(os.path.join(HERE, 'page'), exist_ok=True)
    for s in cfg['servers']:
        t = page(cfg, s)
        open(os.path.join(HERE, 'page', s['id'] + '.html'), 'w', encoding='utf-8', newline='\n').write(t)
        print('%-6s %5d B' % (s['id'], len(t.encode())))
main()
