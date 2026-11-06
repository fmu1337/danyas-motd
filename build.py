"""Builds MOTD templates for the Danyas CS:S v34 servers: motd/<id>.html (one per server, from servers.json).

The game servers (SourceMod plugin motd_gen) download motd/<id>.html on every map start, fill {MAP} {NEXTMAP} {TIMELEFT}
{PLAYERS} {MAXPLAYERS} {LEADER} {DATE} {TIME} {HOSTNAME} and show it in the MOTD window.
Window engines: ClientMod = Chromium; plain v34 = IE11 (edge mode) with JavaScript disabled -> HTML + CSS without
CSS variables and without JS. Images over http/https work in both.
usage: python build.py
"""
import html, json, os, re, socket, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
MOTD_MAX = 2046

CSS_FULL = """body{margin:0;padding:0;background:#FFF;color:#000;font-family:Verdana,Arial,Helvetica,sans-serif;font-size:8pt}
a{color:#000}
.hb{background:#282828;color:#FFF;border-bottom:3px solid #AEAEAE}
.hb td{padding:6px 8px;color:#FFF}
.t{font-size:15pt;font-weight:bold;letter-spacing:1px}
.st{font-size:8pt;color:#AEAEAE}
.cur{font-size:10pt;font-weight:bold;text-align:right}
.dt{width:100%;border-collapse:collapse;border:1px solid #AEAEAE;margin-top:6px}
.dt td{padding:3px 5px;border:1px solid #AEAEAE;font-size:8pt;text-align:left}
.dh td{background:#282828;color:#FFF;font-weight:bold}
.bg1{background:#F3F3F3}
.bg2{background:#FFF}
.me td{background:#FFF1B8;font-weight:bold}
.c{text-align:center}
.cmd{font-family:"Courier New",Courier,monospace;font-weight:bold;white-space:nowrap}
.ft{color:#777;font-size:7pt;text-align:center;padding:6px}"""

CSS_SMALL = ("body{margin:0;font:8pt Verdana}"
             ".h{background:#282828;color:#FFF;padding:5px 8px;font-size:12pt;font-weight:bold}"
             "table{width:100%;border-collapse:collapse}"
             "td{border:1px solid #AEAEAE;padding:2px 5px;font-size:8pt}"
             ".d td{background:#282828;color:#FFF;font-weight:bold}"
             ".b{background:#F3F3F3}")


def a2s(addr, timeout=2.0):
    host, _, port = addr.partition(':')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    req = b'\xff\xff\xff\xffTSource Engine Query\x00'
    try:
        s.sendto(req, (host, int(port)))
        d = s.recv(1400)
        if d[4] == 0x41:
            s.sendto(req + d[5:9], (host, int(port)))
            d = s.recv(1400)
        p = 6
        out = []
        for _ in range(4):
            e = d.index(b'\0', p); out.append(d[p:e].decode('utf8', 'replace')); p = e + 1
        p += 2
        return {'map': out[1], 'players': d[p], 'max': d[p + 1], 'bots': d[p + 2]}
    except Exception:
        return None
    finally:
        s.close()


def esc(s):
    return html.escape(str(s), quote=True)


def rules(cfg, srv):
    r = []
    for x in cfg['rules']:
        if '{age}' in x:
            if not srv.get('age'):
                continue
            x = x.replace('{age}', str(srv['age']))
        r.append(x)
    return r


def page_full(cfg, srv, live):
    o = ['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">',
         '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">',
         '<title>%s</title><style type="text/css">%s</style></head>' % (esc(cfg['title']), CSS_FULL),
         '<body>',
         '<table class="hb" width="100%%" cellspacing="0" cellpadding="0"><tr>'
         '<td><div class="t">%s</div><div class="st">%s</div></td>'
         '<td class="cur">%s<br><span class="st">%s</span></td></tr></table>'
         % (esc(cfg['title'].upper()), esc(cfg['subtitle']), esc(srv['name']), esc(srv['addr']))]
    # servers
    o.append('<table class="dt"><tr class="dh"><td style="width:32%">&nbsp;Сервер</td><td style="width:24%">&nbsp;Адрес</td>')
    if live is not None:
        o.append('<td class="c" style="width:32%">Карта</td><td class="c" style="width:12%">Игроки</td>')
    o.append('</tr>')
    for i, s in enumerate(cfg['servers']):
        cls = 'me' if s['id'] == srv['id'] else 'bg%d' % (i % 2 + 1)
        o.append('<tr class="%s"><td>%s</td><td>%s</td>' % (cls, esc(s['name']), esc(s['addr'])))
        if live is not None:
            q = live.get(s['id'])
            if q:
                o.append('<td class="c">%s</td><td class="c">%d/%d</td>' % (esc(q['map']), q['players'] - q['bots'], q['max']))
            else:
                o.append('<td class="c">&mdash;</td><td class="c">выкл.</td>')
        o.append('</tr>')
    o.append('</table>')
    # commands
    if srv.get('commands'):
        o.append('<table class="dt"><tr class="dh"><td colspan="2">&nbsp;Команды сервера (в чат)</td></tr>')
        for i, (c, d) in enumerate(srv['commands']):
            o.append('<tr class="bg%d"><td class="cmd" style="width:22%%">%s</td><td>%s</td></tr>' % (i % 2 + 1, esc(c), esc(d)))
        o.append('</table>')
    # rules
    o.append('<table class="dt"><tr class="dh"><td>&nbsp;%s</td></tr>' % esc(cfg['rules_title']))
    for x in rules(cfg, srv):
        o.append('<tr class="bg1"><td><strong>%s</strong></td></tr>' % esc(x))
    o.append('</table>')
    foot = ' &middot; '.join('<a href="%s">%s</a>' % (esc(u), esc(t)) for t, u in cfg.get('links', []))
    if live is not None:
        foot += (' &middot; ' if foot else '') + 'обновлено %s UTC' % time.strftime('%d.%m %H:%M', time.gmtime())
    o.append('<div class="ft">%s</div></body></html>' % foot)
    return '\n'.join(o)


def template_small(cfg, srv):
    """Template for the motd_gen plugin (cfg/motd_template.html). Optional blocks <!--oN-->..<!--/oN--> are cut by
    the plugin, lowest N first, until the page fits into MOTD_MAX: o1 = server list, o2.. = rules from the last one.
    Bytes matter (2046 max), so it uses HTML4 optional end tags (</td>, </tr>) and unquoted attributes."""
    head = ('<!DOCTYPE html><html><head><meta http-equiv=X-UA-Compatible content=IE=edge><meta http-equiv=Content-Type content="text/html; charset=utf-8">'
            '<style>%s</style></head><body>' % CSS_SMALL)
    top = ('<div class=h>%s &middot; %s</div>'
           '<table><tr class=b><td>Карта: <b>{MAP}</b> &middot; следующая: <b>{NEXTMAP}</b> &middot; осталось {TIMELEFT}'
           '<tr class=b><td>Онлайн: <b>{PLAYERS}/{MAXPLAYERS}</b> &middot; лидер: {LEADER}</table>'
           % (esc(cfg['title']), esc(srv['name'])))
    cmds = ''
    if srv.get('commands'):
        cmds = '<table><tr class=d><td colspan=2>Команды' + ''.join(
            '<tr><td><b>%s</b><td>%s' % (esc(c), esc(d)) for c, d in srv['commands']) + '</table>'
    rl = rules(cfg, srv)
    rows = []
    for i, x in enumerate(rl):
        n = len(rl) - i + 1          # last rule -> o2, first rule -> o<len+1>
        row = '<tr><td>%s' % esc(x)
        rows.append('<!--o%d-->%s<!--/o%d-->' % (n, row, n) if 2 <= n <= 9 else row)
    r = '<table><tr class=d><td>Правила' + ''.join(rows) + '</table>'
    others = '<!--o1--><table><tr class=d><td colspan=2>Наши серверы' + ''.join(
        '<tr%s><td>%s<td>%s' % (' class=b' if s['id'] == srv['id'] else '', esc(s['name']), esc(s['addr']))
        for s in cfg['servers']) + '</table><!--/o1-->'
    if not cfg.get('motd_rules', True):
        r = ''
    if not cfg.get('motd_servers', True):
        others = ''
    return head + top + cmds + r + others + '</body></html>'


def fill(tpl, mp, nextmap, limit=MOTD_MAX):
    """Python copy of motd_gen.sp: substitute, cut optional blocks until it fits, strip markers."""
    s = tpl.replace('{MAP}', mp).replace('{NEXTMAP}', nextmap)
    for k, v in (('{TIMELEFT}', '59:59'), ('{PLAYERS}', '12'), ('{MAXPLAYERS}', '32'), ('{LEADER}', 'LongPlayerName1234567890 (99)')):
        s = s.replace(k, v)
    cut = []
    for i in range(1, 10):
        if len(re.sub(r'<!--/?o\d-->', '', s).encode('utf-8')) <= limit:
            break
        o, c = '<!--o%d-->' % i, '<!--/o%d-->' % i
        a = s.find(o)
        if a != -1 and s.find(c, a) != -1:
            s = s[:a] + s[s.find(c, a) + len(c):]
            cut.append(i)
    s = re.sub(r'<!--/?o\d-->', '', s)
    return s, cut


def main():
    cfg = json.load(open(os.path.join(HERE, 'servers.json'), encoding='utf-8'))
    out = os.path.join(HERE, 'motd')
    os.makedirs(out, exist_ok=True)
    for srv in cfg['servers']:
        tpl = template_small(cfg, srv)
        open(os.path.join(out, srv['id'] + '.html'), 'w', encoding='utf-8', newline=chr(10)).write(tpl)
        small, cut = fill(tpl, 'gg_aim_ag_texture_jungle-l', 'de_dust2_unlimited_fixed_v2')
        print('%-6s template %5d B, filled %5d B' % (srv['id'], len(tpl.encode()), len(small.encode())))


if __name__ == '__main__':
    main()
