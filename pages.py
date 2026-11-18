"""Builds page/<id>.html (ru, default) and page/<id>.<lang>.html (uk, en) - MOTD window content for every server
(motd.txt on the server = a redirect to page/<id>.html). Style C (old HLstatsX InGame look). IE11/edge friendly
(plain v34 client: no JS -> language switcher links), ClientMod = Chromium (JS picks the language from navigator.language).
usage: python pages.py"""
import html, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
STATS = 'https://GE8EEEF55887CD6-ORACLESTATS.adb.eu-frankfurt-1.oraclecloudapps.com/ords/oraclestats/os/v1/top.html?s=%s'
BANS = 'https://ge8eeef55887cd6-oraclebans.adb.eu-frankfurt-1.oraclecloudapps.com/ords/r/oraclebans/oraclebans/home'
e = lambda s: html.escape(str(s), quote=True)
LANGS = ['ru', 'uk', 'en']
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

CSS = ("html,body{margin:0;background:#fff;color:#000;font:13px Verdana,Arial,sans-serif}"
       ".lg{text-align:right;padding:6px 12px 0;font-size:11px}.lg a{color:#282828;margin-left:8px}.lg b{margin-left:8px}"
       "table{width:100%;border-collapse:collapse;margin-top:8px}"
       "td{border:1px solid #aeaeae;padding:2px 6px}.h td{background:#282828;color:#fff;font-weight:bold}"
       ".b1{background:#f3f3f3}td.k{width:105px;font-weight:bold;font-family:'Courier New',monospace}"
       "table.lay{margin:0;border:0}table.lay>tbody>tr>td{border:0;padding:0;vertical-align:top}td.l{width:38%;font-size:11px;padding:0 8px 8px 12px!important}td.r{padding:0 12px 0 0!important}iframe{width:100%;height:420px;border:1px solid #aeaeae;background:#1b1b1b}.bt{margin-top:12px}.bt a{display:inline-block;margin-right:10px;padding:8px 18px;background:#282828;color:#fff;"
       "text-decoration:none;font-weight:bold;border-bottom:3px solid #aeaeae}.bt a:hover{background:#444}")


def fname(s, lang):
    return s['id'] + ('' if lang == 'ru' else '.' + lang) + '.html'


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
    sw = ''.join('<b>%s</b>' % LABEL[l] if l == lang else '<a href="%s">%s</a>' % (fname(s, l), LABEL[l]) for l in LANGS)
    js = ''
    if lang == 'ru':  # default page: ClientMod (Chromium) picks the language of the player; old client has no JS
        js = ("<script>try{var l=(navigator.language||'').slice(0,2).toLowerCase(),m={uk:'.uk',en:'.en'};"
              "if(m[l])location.replace('%s'+m[l]+'.html')}catch(x){}</script>" % s['id'])
    return ('<!DOCTYPE html><html lang="%s"><head><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta charset="utf-8">'
            '<title>Danyas Server</title><style>%s</style>%s</head><body>'
            '<div class="lg">%s</div>'
            '<table class="lay"><tr><td class="l">%s<div class="bt"><a href="%s">%s</a></div></td>'
            '<td class="r"><iframe src="%s" frameborder="0" scrolling="auto"></iframe></td></tr></table></body></html>'
            % (lang, CSS, js, sw, ''.join(left), e(BANS), e(t['bans']), e(STATS % s['stats'])))


def main():
    cfg = json.load(open(os.path.join(HERE, 'pages.json'), encoding='utf-8'))
    os.makedirs(os.path.join(HERE, 'page'), exist_ok=True)
    for s in cfg['servers']:
        for lang in LANGS:
            t = page(s, lang)
            open(os.path.join(HERE, 'page', fname(s, lang)), 'w', encoding='utf-8', newline='\n').write(t)
        print('%-6s %5d B' % (s['id'], len(t.encode())))
main()
