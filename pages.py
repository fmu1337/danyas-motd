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
       "table{width:100%;border-collapse:collapse;margin-top:8px}"
       "td{border:1px solid #aeaeae;padding:2px 6px}.h td{background:#282828;color:#fff;font-weight:bold}"
       ".b1{background:#f3f3f3}td.k{width:105px;font-weight:bold;font-family:'Courier New',monospace}"
       "table.lay{margin:0;border:0}table.lay>tbody>tr>td{border:0;padding:0;vertical-align:top}td.l{width:46%;font-size:11px;padding:0 8px 8px 12px!important}td.r{padding:8px 12px 0 0!important}iframe{width:100%;height:380px;border:1px solid #aeaeae;background:#1b1b1b}.bt{margin-top:12px}.bt a{display:inline-block;margin-right:10px;padding:8px 18px;background:#282828;color:#fff;"
       "text-decoration:none;font-weight:bold;border-bottom:3px solid #aeaeae}.bt a:hover{background:#444}")

def page(cfg, s):
    left = []
    if s.get('special'):
        left.append('<table><tr class="h"><td colspan="2">Особенности сервера</td></tr>')
        for i, (k, d) in enumerate(s['special']):
            left.append('<tr class="%s"><td class="k">%s</td><td>%s</td></tr>' % ('b1' if i % 2 == 0 else '', e(k), e(d)))
        left.append('</table>')
    left.append('<table><tr class="h"><td>Правила сервера</td></tr>')
    for x in cfg['rules']:
        left.append('<tr class="b1"><td>%s</td></tr>' % e(x))
    left.append('</table>')
    extra = ''
    if s['id'] == 'test':
        extra = '<a target="_blank" href="https://fmu1337.github.io/danyas-motd/">Лендинг (target=_blank, тест)</a>'
    return ('<!DOCTYPE html><html><head><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta charset="utf-8">'
            '<title>Danyas Server</title><style>%s</style></head><body>'
            '<div class="hb"><div class="n">Danyas Server &middot; %s</div><div class="a">%s</div></div>'
            '<table class="lay"><tr><td class="l">%s<div class="bt"><a href="%s">Список банов</a>%s</div></td>'
            '<td class="r"><iframe src="%s" frameborder="0" scrolling="auto"></iframe></td></tr></table></body></html>'
            % (CSS, e(s['name']), e(s['addr']), ''.join(left), e(BANS), extra, e(STATS % s['stats'])))

def main():
    cfg = json.load(open(os.path.join(HERE, 'pages.json'), encoding='utf-8'))
    os.makedirs(os.path.join(HERE, 'page'), exist_ok=True)
    for s in cfg['servers']:
        t = page(cfg, s)
        open(os.path.join(HERE, 'page', s['id'] + '.html'), 'w', encoding='utf-8', newline='\n').write(t)
        print('%-6s %5d B' % (s['id'], len(t.encode())))
main()
