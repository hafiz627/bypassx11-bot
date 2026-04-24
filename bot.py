import os, re, time, asyncio, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "YAHAN_TOKEN_LIKHO")

# ─── Service Lists ─────────────────────────────────────────────────────────────

SIMPLE_DOMAINS = [
    'bit.ly','tinyurl.com','rebrand.ly','short.io','bl.ink','t2m.io','tiny.cc',
    'ow.ly','t.co','g.co','fb.me','amzn.to','t.ly','ln.run','shorturl.at',
    'buff.ly','rb.gy','s.id','soo.gd','clicky.me','u.to','srt.am','mitly.us',
    'snip.ly','urlzs.com','clk.sh','is.gd','v.gd','cutt.ly','shrtco.de',
    'tiny.one','ity.im','1url.com','shorturl.at','brieflink.com','rb.gy',
    'urlshort.net','smallurl.co','shrinkurl.com','inshorturl.com','tii.la',
    'cutsly.com','cut.pe','linksly.co','soo.gd','rly.cx','oke.io','short.pe',
]

ADLINKFLY_DOMAINS = [
    'lksfy.com','shrinkme.io','exe.io','earnow.online','za.gl','ouo.io','bc.vc',
    'adshort.co','adshort.in','cuty.io','shorte.st','adf.ly','droplink.co',
    'cpmshort.com','softurl.in','teraboxlinks.com','arolinks.com','shareus.io',
    'gplinks.in','gplinks.co','fc.lc','clksh.com','linkvertise.com',
    'linksly.co','clicksfly.com','shrink.me','earnl.com','cashurl.in',
    'paidurl.com','earncash.co','linkshrink.net','earnlnk.com','adlinkfly.com',
    'adsrt.com','flylink.me','shortz.me','urlmin.com','lnkr.co','mflinks.com',
    'mflinks.xyz','shortlink.top','yelink.co','adfoc.us','shortest.io',
    'shortzon.com','smartlinks.pro','upfiles.io','clik.pw','yolink.co',
    'rewl.co','shortgo.me','gofile.io',
]

LINKINBIO_DOMAINS = ['linktr.ee','bio.link','taplink.cc']

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# ─── Classify URL ──────────────────────────────────────────────────────────────

def classify(url):
    try:
        domain = urlparse(url).netloc.lower().replace('www.','')
        if any(d in domain for d in LINKINBIO_DOMAINS): return 'linkinbio'
        if any(d in domain for d in ADLINKFLY_DOMAINS): return 'adlinkfly'
        if any(d in domain for d in SIMPLE_DOMAINS):    return 'simple'
        return 'unknown'
    except:
        return 'unknown'

# ─── Extract URL from HTML ─────────────────────────────────────────────────────

def extract_from_html(html, original_url=''):
    patterns = [
        r'content=["\'][0-9]*;?\s*url=([^"\'>\s]+)',
        r'window\.location(?:\.href)?\s*[=\(]\s*["\`]([^"\`\n]+)["\`]',
        r'location\.replace\(["\']([^"\']+)["\']',
        r'"(?:destination|url|link|redirect_url|longUrl|bypass_url)"\s*:\s*"([^"\\]+)"',
        r"'(?:destination|url|link|redirect_url)'\s*:\s*'([^'\\]+)'",
        r'href=["\']([^"\']+)["\'][^>]*>(?:Continue|Proceed|Skip|Go|Click|Download)',
        r'<a[^>]+class=["\'][^"\']*(?:btn|button|skip)[^"\']*["\'][^>]*href=["\']([^"\']+)["\']',
    ]
    for p in patterns:
        m = re.search(p, html, re.I)
        if m:
            found = m.group(1).strip().strip('"\'')
            if found.startswith('http') and found != original_url:
                return found
    return None

# ─── Bypass Methods ────────────────────────────────────────────────────────────

def bypass_simple(url):
    """Simple redirect follow"""
    try:
        s = requests.Session()
        s.max_redirects = 10
        r = s.get(url, headers=HEADERS, allow_redirects=True, timeout=15)
        if r.url != url:
            return r.url
        found = extract_from_html(r.text, url)
        if found: return found
        soup = BeautifulSoup(r.text, 'html.parser')
        meta = soup.find('meta', attrs={'http-equiv': re.compile('refresh', re.I)})
        if meta:
            content = meta.get('content','')
            m = re.search(r'url=(.+)', content, re.I)
            if m: return m.group(1).strip().strip('"\'')
        return r.url
    except:
        return None

def bypass_adlinkfly(url):
    """Full 2-step AdLinkFly bypass"""
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        code = parsed.path.strip('/')

        # Step 1: GET page
        r1 = session.get(url, timeout=15, allow_redirects=True)

        # If already redirected to final destination
        if r1.url != url and not any(d in r1.url for d in ADLINKFLY_DOMAINS):
            return r1.url

        html = r1.text
        soup = BeautifulSoup(html, 'html.parser')

        # Quick extract attempt
        quick = extract_from_html(html, url)
        if quick: return quick

        # Extract token
        token = ''
        ti = soup.find('input', {'name': '_token'})
        if ti: token = ti.get('value','')
        if not token:
            mc = soup.find('meta', {'name': 'csrf-token'})
            if mc: token = mc.get('content','')
        if not token:
            tm = re.search(r'_token["\'\s:=]+["\']([^"\']{20,})["\']', html)
            if tm: token = tm.group(1)

        # Step 2: POST to /links/go
        post_headers = {
            **HEADERS,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': url,
            'Origin': base,
        }
        post_data = {'_token': token, 'code': code}

        time.sleep(1.5)  # slight delay to avoid bot detection

        r2 = session.post(f"{base}/links/go", data=post_data, headers=post_headers, timeout=15)

        # Parse JSON
        try:
            j = r2.json()
            for key in ['url','destination','link','redirect','target','bypass_url']:
                if j.get(key,'').startswith('http'):
                    return j[key]
        except:
            pass

        # Parse HTML fallback
        found = extract_from_html(r2.text, url)
        if found: return found

        # Try alternate endpoints
        for endpoint in ['/go', '/out', '/redirect', '/visit']:
            try:
                r3 = session.post(f"{base}{endpoint}", data=post_data, headers=post_headers, timeout=10)
                try:
                    j = r3.json()
                    for key in ['url','destination','link','redirect']:
                        if j.get(key,'').startswith('http'):
                            return j[key]
                except:
                    pass
                found = extract_from_html(r3.text, url)
                if found: return found
            except:
                continue

        # Final fallback: bypass.vip API
        return bypass_api(url)

    except Exception as e:
        return bypass_api(url)

def bypass_api(url):
    """bypass.vip public API — general fallback"""
    try:
        r = requests.get(
            f"https://bypass.vip/v2?url={quote(url, safe='')}",
            timeout=20
        )
        d = r.json()
        for key in ['destination','result','bypassed_link','url']:
            if d.get(key,'').startswith('http'):
                return d[key]
    except:
        pass

    # Second fallback API
    try:
        r = requests.get(
            f"https://api.bypass.vip/bypass?url={quote(url, safe='')}",
            timeout=15
        )
        d = r.json()
        for key in ['destination','result','url']:
            if d.get(key,'').startswith('http'):
                return d[key]
    except:
        pass

    return None

def bypass_url(url):
    """Master bypass function"""
    kind = classify(url)

    if kind == 'linkinbio':
        return url, 'linkinbio'

    elif kind == 'simple':
        result = bypass_simple(url)
        if not result or result == url:
            result = bypass_api(url)
        return result, 'simple redirect'

    elif kind == 'adlinkfly':
        result = bypass_adlinkfly(url)
        return result, 'adlinkfly'

    else:
        # Unknown: try simple first, then adlinkfly, then API
        result = bypass_simple(url)
        if result and result != url:
            return result, 'auto (simple)'
        result = bypass_adlinkfly(url)
        if result:
            return result, 'auto (adlinkfly)'
        result = bypass_api(url)
        return result, 'auto (api)'

# ─── URL Extractor from text ───────────────────────────────────────────────────

def extract_urls(text):
    return re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)

# ─── Telegram Handlers ─────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ *BypassX Bot*\n\n"
        "Koi bhi shortlink bhejo — seedha bypass kar dunga!\n\n"
        "*Supported:*\n"
        "› bit.ly, tinyurl, t.co, rb.gy, is.gd + 30 more\n"
        "› lksfy.com, adf.ly, ouo.io, shrinkme, exe.io\n"
        "› linkvertise, gplinks, bc.vc, za.gl + 40 more\n"
        "› cpmshort, softurl, teraboxlinks, arolinks\n\n"
        "*Commands:*\n"
        "/bypass <link> — Link bypass karo\n"
        "/help — Help dekho\n\n"
        "Ya seedha link paste karo! 🚀",
        parse_mode='Markdown'
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *BypassX Help*\n\n"
        "• Koi bhi shortlink directly bhejo\n"
        "• Ya `/bypass <url>` likho\n"
        "• Ek saath 5 links tak bhej sakte ho\n\n"
        "⚠️ linktr.ee / bio.link bypass nahi hoti\n"
        "(ye landing pages hain, shortlinks nahi)",
        parse_mode='Markdown'
    )

async def process_bypass(update: Update, url: str):
    short_url = url[:55] + '...' if len(url) > 55 else url
    msg = await update.message.reply_text(
        f"⏳ Bypassing...\n`{short_url}`",
        parse_mode='Markdown'
    )
    try:
        loop = asyncio.get_event_loop()
        result, service = await loop.run_in_executor(None, bypass_url, url)

        if result and result.startswith('http') and result != url:
            await msg.edit_text(
                f"✅ *Bypass Successful!*\n\n"
                f"📎 *Original:*\n`{url}`\n\n"
                f"🎯 *Direct Link:*\n`{result}`\n\n"
                f"🔍 Method: `{service}`",
                parse_mode='Markdown'
            )
        elif service == 'linkinbio':
            await msg.edit_text(
                f"ℹ️ *Link-in-Bio Page*\n\n"
                f"`{url}`\n\n"
                "Ye ek landing page hai — bypass nahi hoti.",
                parse_mode='Markdown'
            )
        else:
            await msg.edit_text(
                f"❌ *Bypass Nahi Hua*\n\n"
                f"`{url}`\n\n"
                "Is service ka bypass abhi possible nahi.\n"
                "Manually try karo: bypass.vip",
                parse_mode='Markdown'
            )
    except Exception as e:
        await msg.edit_text(f"❌ Error: `{str(e)[:150]}`", parse_mode='Markdown')

async def bypass_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /bypass <url>")
        return
    await process_bypass(update, ctx.args[0])

async def handle_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    urls = extract_urls(update.message.text or '')
    if not urls:
        await update.message.reply_text("Koi valid URL nahi mili. HTTP link bhejo.")
        return
    for url in urls[:5]:
        await process_bypass(update, url)

# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    token = BOT_TOKEN
    if token == "YAHAN_TOKEN_LIKHO":
        print("❌ BOT_TOKEN set nahi hai! Environment variable mein dalo.")
        return

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("bypass", bypass_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))

    print("✅ BypassX Bot chal raha hai...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
