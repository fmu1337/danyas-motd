"""Builds page/<id>.html (ru, default) and page/<id>.<lang>.html (uk, en) - MOTD window content for every server
(motd.txt on the server = a redirect to page/<id>.html). Style C (old HLstatsX InGame look). IE11/edge friendly
(plain v34 client: no JS -> language switcher links), ClientMod = Chromium (JS picks the language from navigator.language).
usage: python pages.py"""
import html, json, os, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
STATS = 'https://GE8EEEF55887CD6-ORACLESTATS.adb.eu-frankfurt-1.oraclecloudapps.com/ords/oraclestats/os/v1/top.html?s=%s&n=10'
TOPJSON = STATS.replace('top.html?s=%s&n=10', 'top.json?s=%s&n=10')
BANSJSON = 'https://ge8eeef55887cd6-oraclebans.adb.eu-frankfurt-1.oraclecloudapps.com/ords/oraclebans/ob/v1/bans/recent?limit=30'
BANS = 'https://ge8eeef55887cd6-oraclebans.adb.eu-frankfurt-1.oraclecloudapps.com/ords/r/oraclebans/oraclebans/home'
e = lambda s: html.escape(str(s), quote=True)
LANGS = ['en']  # owner 11-18: English only
BANSDATA = None
LABEL = {'ru': 'RU', 'uk': 'UA', 'en': 'EN'}

T = {
 'ru': {'rules': 'Правила сервера', 'special': 'Особенности сервера', 'bans': 'Список банов', 'rule': [
  'Запрещено использование читов, запрещенных скриптов и моделей.',
  'Запрещено засорение голосового и текстового чата.',
  'Запрещено выдавать себя за администрацию.',
  'Запрещено неуважительное отношение к администрации.',
  'Запрещено пререкаться и оспаривать действия администрации.',
  'Запрещено оскорблять других игроков и разжигать конфликты.']},
 'uk': {'rules': 'Правила сервера', 'special': 'Особливості сервера', 'bans': 'Список банів', 'rule': [
  'Заборонено використання читів, заборонених скриптів та моделей.',
  'Заборонено засмічення голосового та текстового чату.',
  'Заборонено видавати себе за адміністрацію.',
  'Заборонено неповажне ставлення до адміністрації.',
  'Заборонено сперечатися та оскаржувати дії адміністрації.',
  'Заборонено ображати інших гравців та розпалювати конфлікти.']},
 'en': {'rules': 'Server rules', 'special': 'Server features', 'bans': 'Ban list', 'rule': [
  'Cheats, forbidden scripts and models are prohibited.',
  'Do not spam the voice or text chat.',
  'Do not impersonate the administration.',
  'Do not disrespect the administration.',
  'Do not argue with or dispute admin decisions.',
  'Do not insult other players or provoke conflicts.']},
}
# descriptions of special commands: ru text (from pages.json) -> {lang: text}
D = {
 'магазин': {'uk': 'магазин', 'en': 'shop'},
 'меню VIP': {'uk': 'меню VIP', 'en': 'VIP menu'},
 'топ ножевых игроков': {'uk': 'топ ножових гравців', 'en': 'knife players top'},
 'личная статистика (без «!»)': {'uk': 'особиста статистика (без «!»)', 'en': 'personal stats (no "!")'},
 'худшие игроки': {'uk': 'найгірші гравці', 'en': 'worst players'},
 'меню улучшений персонажа': {'uk': 'меню покращень персонажа', 'en': 'character upgrades menu'},
 'мой ранг в RPG': {'uk': 'мій ранг у RPG', 'en': 'my RPG rank'},
 'топ RPG': {'uk': 'топ RPG', 'en': 'RPG top'},
 'моя RPG-статистика': {'uk': 'моя RPG-статистика', 'en': 'my RPG stats'},
 'магазин оружия': {'uk': 'магазин зброї', 'en': 'weapon shop'},
 'общий магазин': {'uk': 'загальний магазин', 'en': 'general shop'},
 'ставки': {'uk': 'ставки', 'en': 'bets'},
}

CSS = (".st{table-layout:fixed;margin-top:0}.st td{overflow:hidden;white-space:nowrap;text-overflow:ellipsis;padding:3px 5px;font-size:11px}.st .h td{text-align:center}.st td.n{text-align:right}.st td.p{text-align:left}.sh{font-size:14px;font-weight:bold;padding:6px 2px}"
       "html,body{margin:0;background:#fff;color:#000;font:13px Verdana,Arial,sans-serif}"
       ".lg{text-align:right;padding:6px 12px 0;font-size:11px}.lg a{color:#282828;margin-left:8px}.lg b{margin-left:8px}"
       "table{width:100%;border-collapse:collapse;margin-top:8px}"
       "td{border:1px solid #aeaeae;padding:2px 6px}.h td{background:#282828;color:#fff;font-weight:bold}"
       ".b1{background:#f3f3f3}td.k{width:105px;font-weight:bold;font-family:'Courier New',monospace}"
       "table.lay{margin:0;border:0}table.lay>tbody>tr>td{border:0;padding:0;vertical-align:top}td.l{width:205px;font-size:10px;padding:0 6px 8px 8px!important}td.r{padding:0 12px 0 0!important}iframe{width:100%;height:390px;border:1px solid #aeaeae;background:#1b1b1b}.bt{margin-top:12px}.bt a{display:inline-block;margin-right:10px;padding:8px 18px;background:#282828;color:#fff;"
       "text-decoration:none;font-weight:bold;border-bottom:3px solid #aeaeae}.bt a:hover{background:#444}")


def fname(s, lang):
    return s['id'] + '.html'


def fetch_top(code):
    try:
        with urllib.request.urlopen(TOPJSON % code, timeout=20) as r:
            d = json.load(r)
        if 'players' in d and d.get('name'):
            return d
    except Exception as ex:
        print('fetch failed', code, ex)
    return None


def fetch_bans():
    try:
        with urllib.request.urlopen(BANSJSON, timeout=20) as r:
            d = json.load(r)
        if isinstance(d.get('bans'), list):
            return d['bans']
    except Exception as ex:
        print('bans fetch failed', ex)
    return None


def fmt_dur(m):
    m = int(m or 0)
    if m == 0:
        return 'Permanent'
    if m < 60:
        return '%d min' % m
    if m < 1440:
        return '%d h' % (m // 60)
    return '%d d' % (m // 1440)


def bans_page(s, bans):
    rows = []
    for i, b in enumerate(bans):
        st = {'active': 'Active', 'unbanned': 'Unbanned', 'expired': 'Expired'}.get(b.get('status'), '')
        dt = time.strftime('%Y-%m-%d', time.gmtime(b['created'])) if b.get('created') else ''
        rows.append('<tr class="%s"><td class="p" title="%s">%s</td><td class="p" title="%s">%s</td><td>%s</td><td>%s</td><td>%s</td><td class="p">%s</td></tr>'
                    % ('b1' if i % 2 == 0 else '', e(b.get('name', '')), e(b.get('name', '')), e(b.get('reason', '')), e(b.get('reason', '')),
                       dt, fmt_dur(b.get('duration_min')), st, e(b.get('server', ''))))
    body = ('<div class="sh">Recent bans (last %d) &middot; <a href="%s.html">&laquo; Back</a></div>'
            '<table class="st"><colgroup><col width="20%%"><col><col width="86"><col width="84"><col width="76"><col width="92"></colgroup>'
            '<tr class="h"><td>Player</td><td>Reason</td><td>Date</td><td>Length</td><td>Status</td><td>Server</td></tr>%s</table>'
            % (len(bans), s['id'], ''.join(rows)))
    return ('<!DOCTYPE html><html lang="en"><head><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta charset="utf-8">'
            '<title>Danyas Server - bans</title><style>%s</style></head><body><div style="padding:0 10px">%s</div></body></html>' % (CSS, body))


def fmt_time(sec):
    m = int(sec) // 60
    return '%dh %dm' % (m // 60, m % 60) if m >= 60 else '%dm' % m


def stats_html(d):
    rows = ['<div class="sh">Top players: %s</div>' % e(d['name']),
            '<table class="st"><colgroup><col width="28"><col><col width="48"><col width="46"><col width="58"><col width="60"><col width="48"><col width="58"></colgroup>'
            '<tr class="h"><td>#</td><td>Player</td><td>Skill</td><td>Kills</td><td>Deaths</td><td>K/D</td><td>HS%</td><td>Time</td></tr>']
    for i, p in enumerate(d['players'][:10]):
        hs = int(round(100.0 * p['hs'] / p['kills'])) if p['kills'] else 0
        rows.append('<tr class="%s"><td class="n">%d</td><td class="p" title="%s">%s</td><td class="n">%d</td><td class="n">%d</td><td class="n">%d</td><td class="n">%.2f</td><td class="n">%d</td><td class="n">%s</td></tr>'
                    % ('b1' if i % 2 == 0 else '', p['pos'], e(p['name']), e(p['name']), p['skill'], p['kills'], p['deaths'], p['kd'], hs, fmt_time(p['time'])))
    rows.append('</table>')
    if not d['players']:
        rows.append('<div class="sh" style="font-weight:normal">No ranked players yet.</div>')
    return ''.join(rows)


def page(s, lang):
    t = T[lang]
    left = []
    if s.get('special'):
        left.append('<table><tr class="h"><td colspan="2">%s</td></tr>' % e(t['special']))
        for i, (k, d) in enumerate(s['special']):
            d = d if lang == 'ru' else D.get(d, {}).get(lang, d)
            left.append('<tr class="%s"><td class="k">%s</td><td>%s</td></tr>' % ('b1' if i % 2 == 0 else '', e(k), e(d)))
        left.append('</table>')
    left.append('<table><tr class="h"><td>%s</td></tr>' % e(t['rules']))
    for x in t['rule']:
        left.append('<tr class="b1"><td>%s</td></tr>' % e(x))
    left.append('</table>')
    d = fetch_top(s['stats'])
    bans_url = ('bans-%s.html' % s['id']) if BANSDATA else BANS
    right = stats_html(d) if d else '<iframe src="%s" frameborder="0" scrolling="auto"></iframe>' % e(STATS % s['stats'])
    sw = ''
    js = ''
    if False:  # default page: ClientMod (Chromium) picks the language of the player; old client has no JS
        js = ("<script>try{var l=(navigator.language||'').slice(0,2).toLowerCase(),m={uk:'.uk',en:'.en'};"
              "if(m[l])location.replace('%s'+m[l]+'.html')}catch(x){}</script>" % s['id'])
    return ('<!DOCTYPE html><html lang="%s"><head><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta charset="utf-8">'
            '<title>Danyas Server</title><style>%s</style>%s</head><body>'
            '%s'
            '<table class="lay"><tr><td class="l">%s<div class="bt"><a href="%s">%s</a></div></td>'
            '<td class="r">%s</td></tr></table></body></html>'
            % (lang, CSS, js, sw, ''.join(left), e(bans_url), e(t['bans']), right))


def main():
    global BANSDATA
    BANSDATA = fetch_bans()
    cfg = json.load(open(os.path.join(HERE, 'pages.json'), encoding='utf-8'))
    os.makedirs(os.path.join(HERE, 'page'), exist_ok=True)
    for s in cfg['servers']:
        for lang in LANGS:
            t = page(s, lang)
            open(os.path.join(HERE, 'page', fname(s, lang)), 'w', encoding='utf-8', newline='\n').write(t)
        if BANSDATA:
            open(os.path.join(HERE, 'page', 'bans-%s.html' % s['id']), 'w', encoding='utf-8', newline='\n').write(bans_page(s, BANSDATA))
        print('%-6s %5d B' % (s['id'], len(t.encode())))
main()
