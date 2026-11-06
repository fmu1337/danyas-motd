"""Builds MOTD templates for the Danyas CS:S v34 servers.

motd/<id>.html     template per server (from servers.json); the game servers (SourceMod plugin motd_gen) download it on
                   every map start, fill {MAP} {NEXTMAP} {TIMELEFT} {PLAYERS} {MAXPLAYERS} {LEADER} {DATE} {TIME}
                   {HOSTNAME} and show it in the MOTD window
preview/<id>.html  the same page filled with sample data, to look at in a browser

Window engines: ClientMod = Chromium; plain v34 = IE11 (edge mode, needs X-UA-Compatible) with JavaScript disabled
-> HTML + CSS3 without CSS variables and without JS. Window ~870x470, keep it without scrolling.
Size: the page goes to players through a string table (motd_gen sm_motdgen_tablemax, 4096 on the servers).
usage: python build.py
"""
import html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE_MAX = 4096

CSS = """html{height:100%%;background:#0d0d0d}
html,body{margin:0;padding:0;color:#ddd;font-family:'Segoe UI',Tahoma,Arial,sans-serif;font-size:14px;overflow:hidden}
body{background:#121212;background:radial-gradient(circle at 90%% 0,%(g)s,rgba(0,0,0,0) 55%%),linear-gradient(#161616,#0d0d0d);height:100%%}
.w{padding:18px 22px}
.top{background:#1d1d1d;background:linear-gradient(90deg,#262626,#151515);border-left:5px solid %(c)s;border-radius:6px;padding:16px 20px;box-shadow:0 0 18px rgba(0,0,0,.6)}
.top table{width:100%%;border-collapse:collapse}
.n{font-size:32px;font-weight:bold;letter-spacing:2px;color:#fff;text-transform:uppercase}
.s{color:#888;font-size:13px;letter-spacing:1px}
.a{text-align:right;color:%(c)s;font-size:17px;font-weight:bold}
.st{display:-ms-flexbox;display:flex;margin:16px -6px 0}
.c{-ms-flex:1 1 0px;flex:1 1 0;min-width:0;margin:0 6px;background:#1b1b1b;background:rgba(30,30,30,.85);border:1px solid #2c2c2c;border-top:3px solid %(c)s;border-radius:6px;padding:11px 12px}
.c.m{-ms-flex:1.7 1 0px;flex:1.7 1 0}
.l{color:#888;font-size:12px;text-transform:uppercase;letter-spacing:1px}
.v{color:#fff;font-size:17px;font-weight:bold;margin-top:4px;word-wrap:break-word;word-break:break-all}
h2{margin:20px 0 8px;font-size:13px;color:%(c)s;text-transform:uppercase;letter-spacing:2px}
.cm{display:-ms-flexbox;display:flex;-ms-flex-wrap:wrap;flex-wrap:wrap;margin:0 -4px}
.k{width:50%%;box-sizing:border-box;padding:0 4px 8px}
.k div{background:#1b1b1b;background:rgba(30,30,30,.85);border:1px solid #2c2c2c;border-radius:6px;padding:10px 12px}
.k b{display:inline-block;min-width:105px;color:%(c)s;font-family:Consolas,'Courier New',monospace;font-size:16px}
.k span{color:#bbb;font-size:14px}
.f{margin-top:14px;color:#666;font-size:12px;text-align:center}"""


def esc(s):
    return html.escape(str(s), quote=True)


def glow(c, a=0.22):
    c = c.lstrip('#')
    return 'rgba(%d,%d,%d,%.2f)' % (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)


def template(cfg, srv):
    c = srv.get('color', '#ff6a00')
    head = ('<!DOCTYPE html><html><head><meta http-equiv="X-UA-Compatible" content="IE=edge">'
            '<meta charset="utf-8"><title>%s</title><style>%s</style></head><body><div class="w">'
            % (esc(cfg['title']), CSS % {'c': c, 'g': glow(c)}))
    top = ('<div class="top"><table><tr><td><div class="n">%s</div><div class="s">%s &middot; %s</div></td>'
           '<td class="a">%s</td></tr></table></div>'
           % (esc(srv['name']), esc(cfg['title'].upper()), esc(cfg['subtitle']), esc(srv['addr'])))
    cards = [('Карта', '{MAP}', ' m'), ('Следующая', '{NEXTMAP}', ' m'), ('До смены', '{TIMELEFT}', ''),
             ('Онлайн', '{PLAYERS} / {MAXPLAYERS}', ''), ('Лидер', '{LEADER}', ' m')]
    st = '<div class="st">' + ''.join('<div class="c%s"><div class="l">%s</div><div class="v" title="%s">%s</div></div>'
                                      % (m, l, v, v) for l, v, m in cards) + '</div>'
    cm = ''
    if srv.get('commands'):
        cm = '<h2>Команды</h2><div class="cm">' + ''.join(
            '<div class="k"><div><b>%s</b><span>%s</span></div></div>' % (esc(k), esc(d)) for k, d in srv['commands']) + '</div>'
    foot = '<div class="f">%s</div>' % esc(cfg.get('footer', ''))
    return head + top + st + cm + foot + '</div></body></html>'


SAMPLE = {'{MAP}': 'gg_aim_ag_texture_jungle-l', '{NEXTMAP}': 'cs_italy', '{TIMELEFT}': '17:42', '{PLAYERS}': '7',
          '{MAXPLAYERS}': '32', '{LEADER}': 'ᵈᵃᶰʸᵃˢ (24)', '{DATE}': '06.11.2026', '{TIME}': '12:00', '{HOSTNAME}': 'Danyas'}


def main():
    cfg = json.load(open(os.path.join(HERE, 'servers.json'), encoding='utf-8'))
    for d in ('motd', 'preview'):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
    for srv in cfg['servers']:
        t = template(cfg, srv)
        if len(t.encode('utf-8')) > TABLE_MAX - 200:
            raise SystemExit('%s: template %d B is too close to the %d B limit' % (srv['id'], len(t.encode()), TABLE_MAX))
        open(os.path.join(HERE, 'motd', srv['id'] + '.html'), 'w', encoding='utf-8', newline='\n').write(t)
        p = t
        for k, v in SAMPLE.items():
            p = p.replace(k, esc(v))
        open(os.path.join(HERE, 'preview', srv['id'] + '.html'), 'w', encoding='utf-8', newline='\n').write(p)
        print('%-6s %5d B' % (srv['id'], len(t.encode('utf-8'))))


if __name__ == '__main__':
    main()
