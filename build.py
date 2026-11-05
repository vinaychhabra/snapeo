#!/usr/bin/env python3
"""Snapeo Studios static build.

Reads  src/app.src.js, src/style.css, assets/config.js
Writes index.html, portfolio/, films/, experience/, about/, contact/ (each index.html),
       404.html, sitemap.xml, robots.txt, llms.txt, llms-full.txt, manifest.webmanifest,
       CNAME, assets/style.min.css, assets/app.min.js

Run:  npm install && python3 build.py
Photos, videos and phone numbers live in assets/config.js (no rebuild needed).
SEO copy, FAQ, page titles and descriptions live in this file (rebuild after editing).
"""
import hashlib, html, json, os, re, subprocess, sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
SITE = "https://www.snapeo.in"
TODAY = os.environ.get("BUILD_DATE") or date.today().isoformat()
BIZ = SITE + "/#business"
WA_NUM, PHONES = "917017889843", ["+91 95578 82097", "+91 98373 10900"]
WA_DISPLAY, EMAIL = "+91 70178 89843", "snapeostudios@gmail.com"
IG1, IG2 = "https://www.instagram.com/snapeo_studios", "https://www.instagram.com/snapeo_invites"
OG = SITE + "/assets/og.jpg"
OG_ALT = "Snapeo Studios, wedding photography and films in Rudrapur, Uttarakhand"
tel = lambda n: "tel:+" + re.sub(r"\D", "", n)
WA = f"https://wa.me/{WA_NUM}"
e = html.escape

ORDER = ["home", "portfolio", "films", "experience", "about", "contact"]
PATH = {"home": "/", "portfolio": "/portfolio/", "films": "/films/", "experience": "/experience/", "about": "/about/", "contact": "/contact/"}
LABEL = {"home": "Home", "portfolio": "Portfolio", "films": "Films", "experience": "Experience", "about": "About", "contact": "Enquire"}
URL = {k: SITE + v for k, v in PATH.items()}
META = {
    "home": ("Snapeo Studios | Wedding Photography & Films in Rudrapur",
             "Snapeo Studios is a wedding photography and films studio in Rudrapur, Uttarakhand, covering weddings, pre-wedding shoots and portraits across India."),
    "portfolio": ("Wedding Photography Portfolio | Snapeo Studios",
                  "Browse wedding, pre-wedding and editorial photographs by Snapeo Studios, a wedding photography studio in Rudrapur, Uttarakhand serving couples across India."),
    "films": ("Wedding Films & Cinematography | Snapeo Studios",
              "Watch cinematic wedding films and pre-wedding films by Snapeo Studios, Rudrapur. Highlight films and longer features with real sound, vows and speeches."),
    "experience": ("Wedding Photography & Film Packages | Snapeo Studios",
                   "See what a Snapeo Studios wedding includes: candid photography, a highlight film, a feature film and hand-bound albums. Every wedding is quoted individually."),
    "about": ("About Snapeo Studios | Wedding Photographers in Rudrapur",
              "Snapeo Studios takes a limited number of weddings each season. One calm, small team shoots photography and film together in Rudrapur, across India and abroad."),
    "contact": ("Check Your Date & Get a Quote | Snapeo Studios",
                f"Check your wedding date with Snapeo Studios in Rudrapur, Uttarakhand. Message on WhatsApp {WA_DISPLAY} or send the enquiry form. We reply within a day or two."),
}
FAQ = [
    ("Where is Snapeo Studios located?", "Snapeo Studios is based in Rudrapur, Uttarakhand, India, and shoots weddings across India and abroad."),
    ("What services does Snapeo Studios offer?", "Wedding photography, cinematic wedding films, pre-wedding shoots, hand-bound wedding albums and destination wedding coverage. Photography and film are handled by one small team."),
    ("How early should we book Snapeo Studios?", "As soon as you have a date or a shortlist of dates. Popular dates, especially November to February, are taken first."),
    ("Does Snapeo Studios travel for weddings?", "Yes. Snapeo Studios shoots across India and abroad and handles its own logistics."),
    ("Can we book photography and film together?", "Yes, and most couples do. One team covers both, so the day feels calmer and the photos and film match."),
    ("How much does Snapeo Studios charge for a wedding?", f"Every wedding is quoted individually based on days, events and deliverables. Message {WA_DISPLAY} on WhatsApp for a quote."),
]
STEPS = [
    ("Say hello", "Message your wedding date and city on WhatsApp or through the enquiry form."),
    ("Meet", "Talk through your families, rituals and what matters most."),
    ("Plan", "The team prepares timelines and locations with your planner."),
    ("Celebrate", "A calm, small team photographs and films your wedding days."),
    ("Receive", "Your gallery, film and album are delivered."),
]
FILMS = [("Moni & Kartik (pre-wedding)", "https://vimeo.com/1238447668/49f65594b9"),
         ("Parimal & Abhijeet", "https://vimeo.com/1238442921/849bc381e8"),
         ("Tanushree & Dhwaj", None)]


def faq_html():
    return '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ) + "</div>"


def contact_block():
    return (f'<h3>Contact Snapeo Studios</h3><address>WhatsApp: <a href="{WA}">{WA_DISPLAY}</a><br>'
            f'Call: <a href="{tel(PHONES[0])}">{PHONES[0]}</a>, <a href="{tel(PHONES[1])}">{PHONES[1]}</a><br>'
            f'Email: <a href="mailto:{EMAIL}">{EMAIL}</a><br>'
            f'Instagram: <a href="{IG1}" rel="noopener">@snapeo_studios</a> and <a href="{IG2}" rel="noopener">@snapeo_invites</a><br>'
            'Location: Rudrapur, Uttarakhand, India</address>')


def film_links():
    out = [f'<a href="{u}" rel="noopener">{e(n)}</a>' if u else e(n) for n, u in FILMS]
    return ", ".join(out[:-1]) + " and " + out[-1]


TABLE = ('<table><caption class="sr">Wedding package deliverables</caption><thead><tr><th scope="col">Deliverable</th><th scope="col">What you get</th></tr></thead><tbody>'
         '<tr><td>Photography</td><td>Candid and portrait coverage of every event, hand-edited, in a private online gallery</td></tr>'
         '<tr><td>Highlight film</td><td>A short cinematic film of the wedding, ready to share</td></tr>'
         '<tr><td>Feature film</td><td>A longer film with the speeches, vows and rituals</td></tr>'
         '<tr><td>Album</td><td>An archival, hand-bound album designed with you</td></tr>{extra}</tbody></table>')

SEO = {}
SEO["home"] = f'''<div class="seo-in"><h2>Wedding photography and films in Rudrapur, Uttarakhand</h2>
<p class="lead">Snapeo Studios is a wedding photography and wedding film studio based in Rudrapur, Uttarakhand. One small team shoots candid photos and cinematic films together, covering every ritual from haldi and mehendi to pheras and vidaai. We work across Uttarakhand, travel anywhere in India and abroad, and quote every wedding individually. To check your date, message us on <a href="{WA}">WhatsApp at {WA_DISPLAY}</a>.</p>
<h3>What does Snapeo Studios offer?</h3><ul>
<li><strong>Wedding photography:</strong> candid and portrait coverage for every ceremony, edited by hand and delivered in a private gallery.</li>
<li><strong>Wedding films:</strong> a cinematic highlight film and a longer feature that keeps the speeches and the vows.</li>
<li><strong>Pre-wedding shoots:</strong> relaxed sessions in Nainital, Bhimtal, the Kumaon hills or a location you choose.</li>
<li><strong>Albums:</strong> archival, hand-bound albums designed with you, with prints made to be kept.</li>
<li><strong>Destination weddings:</strong> we travel with you across India and abroad and handle our own logistics.</li></ul>
<details class="more"><summary>Read the full guide to our wedding coverage</summary>
<div class="seo-cols"><div>
<h3>Why do couples choose Snapeo Studios?</h3>
<p>We take a limited number of weddings each season so every couple gets full attention. Our style is calm direction and natural light: we guide gently, stay out of the way and let the day unfold. Because photography and film come from the same team, you meet fewer strangers and the photos and film tell one matching story.</p>
<h3>Is a pre-wedding shoot worth it?</h3>
<p>For most couples, yes. A pre-wedding shoot gets you comfortable in front of the camera before the big day, so wedding photos look more relaxed. It also gives you photos for save-the-date invites and a short film to play at the sangeet. Plan it 1 to 2 months before the wedding so the edited photos are ready in time for invites.</p>
<h3>How does Snapeo Studios plan wedding coverage?</h3>
<p>A typical North Indian wedding runs over 2 to 4 days with 4 to 6 separate events. Before the wedding we sit with the couple and build a plan for each event: who is shooting, which family members matter most and which moments cannot be missed. Smaller events like haldi and mehendi need a lighter crew, while the baraat, pheras and reception need more coverage because many things happen at once.</p>
<p>Light changes the plan too. Banquet halls in Rudrapur and Haldwani often have mixed indoor lighting, so the team carries its own lights for stage and night shots. For hill venues in Nainital or Mukteshwar, couple portraits are planned around golden hour, which in winter falls roughly between 4 pm and 5:30 pm.</p>
</div><div>
<h3>What is included in a Snapeo wedding package?</h3>{TABLE.format(extra="")}
<h3>What should you ask a wedding photographer before booking?</h3>
<p>Ask to see two or three full weddings, not just the best single frames, so you know how the photographer handles every event and every kind of light. Check who will actually shoot your wedding and how many people come on each day. Confirm what is included: edited photos, a highlight film, a full film, an album, and how you receive them. Finally, ask how they handle travel and stay for outstation or destination weddings, so the quote has no surprises later.</p>
<h3>Which weddings has Snapeo Studios filmed?</h3>
<p>Recent films include {film_links()}. See more on the <a href="/films/">Films</a> and <a href="/portfolio/">Portfolio</a> pages.</p>
</div></div></details>
<h3>Frequently asked questions</h3>{faq_html()}
{contact_block()}
<p>Planning a hill wedding? Check seasons and travel at <a href="https://uttarakhandtourism.gov.in/" rel="noopener">Uttarakhand Tourism</a>.</p></div>'''

SEO["portfolio"] = f'''<div class="seo-in"><h2>About this wedding photography portfolio</h2>
<p class="lead">These photographs come from weddings, pre-wedding shoots and editorial portraits shot by Snapeo Studios, a wedding photography studio in Rudrapur, Uttarakhand. Use the filters above to browse by type, and tap any photo to see it larger.</p>
<ul><li><strong>Wedding:</strong> ceremonies and rituals from haldi and mehendi to the baraat, varmala, pheras and vidaai, shot in natural light.</li>
<li><strong>Pre-wedding:</strong> relaxed couple sessions planned around golden hour, in the hills or at a location you choose.</li>
<li><strong>Editorial:</strong> details, jewellery, outfits and portraits that tell the quieter parts of the story.</li></ul>
<p>Want to see a full wedding and not just the best frames? <a href="{WA}">Message us on WhatsApp</a> or visit the <a href="/contact/">enquiry page</a>, and see our <a href="/films/">wedding films</a> too.</p></div>'''

SEO["films"] = f'''<div class="seo-in"><h2>Wedding films by Snapeo Studios</h2>
<p class="lead">Every wedding is unique and so are our films. Snapeo Studios makes a cinematic highlight film and a longer feature that keeps the real sound, the speeches and the vows. Photography and film come from one small team in Rudrapur, so the photos and the film match.</p>
<p>Recent films include {film_links()}. To talk about a film for your wedding or pre-wedding shoot, <a href="{WA}">message us on WhatsApp</a> or use the <a href="/contact/">enquiry form</a>. You can also browse our <a href="/portfolio/">photo portfolio</a>.</p></div>'''

SEO["experience"] = f'''<div class="seo-in"><h2>What is included in a Snapeo Studios wedding</h2>
{TABLE.format(extra='<tr><td>Destination coverage</td><td>Travel across India and abroad, with logistics handled by the studio</td></tr>')}
<p>Every wedding is quoted individually based on days, events and deliverables. <a href="{WA}">Message {WA_DISPLAY} on WhatsApp</a> or <a href="/contact/">request availability</a> and we will share details.</p>
<h3>Frequently asked questions</h3>{faq_html()}</div>'''

SEO["about"] = f'''<div class="seo-in"><h2>About Snapeo Studios, wedding photographers in Rudrapur</h2>
<p class="lead">Snapeo Studios is a wedding photography and wedding film studio based in Rudrapur, Uttarakhand. We take a limited number of weddings each season, so every couple receives our best work. Photography and film come from one calm, small team that works across Uttarakhand and travels anywhere in India and abroad.</p>
<p>Our approach is simple: be present, stay quiet and let the day unfold. We shoot in natural light with calm direction, and we plan each event with the couple before the wedding. Explore our <a href="/portfolio/">portfolio</a> and <a href="/films/">films</a>, or <a href="/contact/">check your date</a>.</p></div>'''

SEO["contact"] = f'''<div class="seo-in"><h2>Contact Snapeo Studios in Rudrapur, Uttarakhand</h2>
<p class="lead">Share your wedding date and city and we will tell you if we are free. We reply personally, usually within a day or two.</p>{contact_block()}</div>'''

# ------------------------------------------------------------ structured data
business = {
    "@type": ["LocalBusiness", "ProfessionalService"], "@id": BIZ, "name": "Snapeo Studios", "url": SITE + "/",
    "logo": {"@type": "ImageObject", "url": SITE + "/assets/icons/icon-512.png", "width": 512, "height": 512},
    "image": [OG],
    "description": "Wedding photography and wedding films studio based in Rudrapur, Uttarakhand, serving couples across India and abroad.",
    "telephone": ["+91-7017889843", "+91-9557882097", "+91-9837310900"], "email": EMAIL, "priceRange": "₹₹",
    "address": {"@type": "PostalAddress", "addressLocality": "Rudrapur", "addressRegion": "Uttarakhand", "addressCountry": "IN"},
    "contactPoint": [{"@type": "ContactPoint", "telephone": "+91-7017889843", "contactType": "customer service", "areaServed": "IN"}],
    "areaServed": [{"@type": "City", "name": "Rudrapur"}, {"@type": "AdministrativeArea", "name": "Uttarakhand"}, {"@type": "Country", "name": "India"}],
    "sameAs": [IG1, IG2],
    "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Wedding Photography & Films", "itemListElement": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}} for n in
        ["Wedding Photography", "Cinematic Wedding Films", "Pre-Wedding Shoots", "Wedding Albums", "Destination Wedding Coverage"]]},
}
website = {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Snapeo Studios", "publisher": {"@id": BIZ}, "inLanguage": "en-IN"}
WPTYPE = {"home": "WebPage", "portfolio": "CollectionPage", "films": "CollectionPage", "experience": "WebPage", "about": "AboutPage", "contact": "ContactPage"}


def faq_ld(u):
    return {"@type": "FAQPage", "@id": u + "#faq", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}


def jsonld(k):
    u = URL[k]
    g = []
    if k in ("home", "contact"):
        g.append(business)
    if k == "home":
        g.append(website)
    page = {"@type": WPTYPE[k], "@id": u + "#webpage", "url": u, "name": META[k][0], "description": META[k][1],
            "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": BIZ}, "inLanguage": "en-IN", "dateModified": TODAY,
            "primaryImageOfPage": {"@type": "ImageObject", "url": OG}}
    if k != "home":
        page["breadcrumb"] = {"@id": u + "#breadcrumb"}
        g.append({"@type": "BreadcrumbList", "@id": u + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Contact" if k == "contact" else LABEL[k], "item": u}]})
    g.append(page)
    if k in ("home", "contact", "experience"):
        g.append(faq_ld(u))
    if k == "about":
        g.append({"@type": "HowTo", "@id": u + "#booking", "name": "How to book Snapeo Studios for your wedding",
                  "step": [{"@type": "HowToStep", "position": i + 1, "name": n, "text": t} for i, (n, t) in enumerate(STEPS)]})
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False, separators=(",", ":")) + "</script>"


# ------------------------------------------------------------ assets
def read(p):
    return open(p, encoding="utf-8").read()


def write(p, s):
    d = os.path.dirname(p)
    if d:
        os.makedirs(d, exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)


def build_assets(samples):
    app = read("src/app.src.js")
    app = app.replace("/*@PAGES*/{}", json.dumps({k: {"t": META[k][0], "d": META[k][1], "u": URL[k]} for k in ORDER}, ensure_ascii=False, separators=(",", ":")))
    app = app.replace("/*@SEO*/{}", json.dumps(SEO, ensure_ascii=False, separators=(",", ":")))
    app = app.replace("/*@FAQ*/[]", json.dumps(FAQ, ensure_ascii=False, separators=(",", ":")))
    write("build/app.pre.js", app)
    words = set(re.findall(r"[A-Za-z0-9_-]+", app + read("assets/config.js") + "\n".join(samples) + "\n".join(SEO.values())))
    write("build/usage.json", json.dumps({"classes": sorted(words), "ids": sorted(words)}))
    r = subprocess.run(["node", "tools/minify.js"], capture_output=True, text=True)
    if r.returncode:
        sys.exit("minify failed:\n" + r.stderr)
    print(r.stdout.strip())


def ver(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()[:8]


def head(k, v):
    t, d = META[k]
    u = URL[k]
    return f'''<!DOCTYPE html>
<html lang="en-IN" data-page="{k}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(t)}</title>
<meta name="description" content="{e(d)}">
<link rel="canonical" href="{u}">
<link rel="alternate" hreflang="en-IN" href="{u}">
<link rel="alternate" hreflang="x-default" href="{u}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<meta name="theme-color" content="#fbf5f1">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Snapeo Studios">
<meta property="og:title" content="{e(t)}">
<meta property="og:description" content="{e(d)}">
<meta property="og:url" content="{u}">
<meta property="og:image" content="{OG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(OG_ALT)}">
<meta property="og:locale" content="en_IN">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(t)}">
<meta name="twitter:description" content="{e(d)}">
<meta name="twitter:image" content="{OG}">
<meta name="twitter:image:alt" content="{e(OG_ALT)}">
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<link rel="alternate" type="text/plain" href="/llms.txt" title="LLMs.txt">
<link rel="preload" href="/assets/fonts/bodoni-logo.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/cormorant.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/hanken.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preconnect" href="https://lh3.googleusercontent.com" crossorigin>
<link rel="dns-prefetch" href="//i.vimeocdn.com"><link rel="dns-prefetch" href="//player.vimeo.com">
<link rel="stylesheet" href="/assets/style.min.css?v={v['css']}">
{jsonld(k)}
<noscript><style>#pre{{display:none}}body.loading{{overflow:auto}}.up,.rv{{opacity:1!important;transform:none!important}}</style></noscript>
<script>setTimeout(function(){{var p=document.getElementById("pre");if(p&&document.body.classList.contains("loading")){{p.remove();document.body.classList.remove("loading")}}}},9000)</script>
<script src="/assets/config.js?v={v['cfg']}" defer></script>
<script src="/assets/app.min.js?v={v['js']}" defer></script>
</head>'''


def body(k):
    nav = "".join(f'<a{chr(32) + "class=" + chr(34) + "cta" + chr(34) if o == "contact" else ""} href="{PATH[o]}">{LABEL[o]}</a>' for o in ORDER)
    return f'''<body class="loading" data-page="{k}"><a class="skip" href="#view">Skip to content</a><i id="sp"></i>
<div id="pre" aria-hidden="true"><div class="pre-in"><div class="pre-mark" id="pm"></div><i class="pre-line"></i></div></div>
<header id="hd"><a class="logo" href="/" id="lg" aria-label="Snapeo Studios, home">Snapeo Studios</a><button class="burger" id="bg" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="nv"><i></i><i></i></button>
<nav id="nv" aria-label="Primary">{nav}</nav></header>
<main id="app"><div id="view"></div><section id="seo" class="seo wrap" data-r="{k}" aria-label="About Snapeo Studios">{SEO[k]}</section></main>
<footer id="ft"><div class="ft-in"><div><p>Snapeo Studios, wedding photography and films in Rudrapur, Uttarakhand, India.<br>WhatsApp <a href="{WA}">{WA_DISPLAY}</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></p></div></div></footer>
<div id="lb" role="dialog" aria-modal="true" aria-label="Viewer"><button id="lx" type="button">Close</button><div id="lbc"></div></div>
<noscript><p class="nj">Please turn on JavaScript to see the animated portfolio. You can still reach us on <a href="{WA}">WhatsApp {WA_DISPLAY}</a>.</p></noscript>
</body></html>'''


def main():
    build_assets([body(k) for k in ORDER])
    v = {"css": ver("assets/style.min.css"), "js": ver("assets/app.min.js"), "cfg": ver("assets/config.js")}
    for k in ORDER:
        write("index.html" if k == "home" else f"{k}/index.html", head(k, v) + "\n" + body(k))
    write("404.html", f'''<!DOCTYPE html><html lang="en-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | Snapeo Studios</title><meta name="robots" content="noindex"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/style.min.css?v={v['css']}"></head><body><main style="min-height:100vh;display:grid;place-items:center;text-align:center;padding:24px"><div><h1 style="font-size:clamp(2.4rem,8vw,5rem)">This page <em>wandered off</em></h1><p style="margin:18px auto 28px">The page you are looking for is not here. Our home page has everything.</p><a class="btn solid" href="/">Back to Snapeo Studios</a></div></main></body></html>''')
    urls = "".join(f"<url><loc>{URL[k]}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>{'1.0' if k == 'home' else '0.8'}</priority></url>" for k in ORDER)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    bots = ["*", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "Bingbot", "Googlebot"]
    write("robots.txt", "\n\n".join(f"User-agent: {b}\nAllow: /" for b in bots) + f"\n\nSitemap: {SITE}/sitemap.xml\n")
    write("CNAME", "www.snapeo.in")
    write(".nojekyll", "")
    write("manifest.webmanifest", json.dumps({"name": "Snapeo Studios", "short_name": "Snapeo", "description": "Wedding photography and films in Rudrapur, Uttarakhand",
                                              "start_url": "/", "scope": "/", "display": "standalone", "background_color": "#fbf5f1", "theme_color": "#fbf5f1", "lang": "en-IN",
                                              "icons": [{"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                                                        {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                                                        {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, indent=2))
    write("llms.txt", f'''# Snapeo Studios

> Snapeo Studios is a wedding photography and wedding film studio based in Rudrapur, Uttarakhand, India. One small team shoots photography and film together, and the studio covers weddings across India and abroad.

Key facts:
- Services: wedding photography, cinematic wedding films, pre-wedding shoots, hand-bound albums, destination weddings
- Location: Rudrapur, Uttarakhand, India
- Service area: Uttarakhand, Pan India and abroad
- Booking: WhatsApp {WA_DISPLAY}, calls {PHONES[0]} / {PHONES[1]}
- Email: {EMAIL}
- Pricing: every wedding is quoted individually based on days, events and deliverables

## Pages
- [Home]({SITE}/): services, booking steps, FAQs
- [Portfolio]({URL['portfolio']}): wedding, pre-wedding and editorial photos
- [Films]({URL['films']}): wedding films
- [Experience]({URL['experience']}): what is included
- [About]({URL['about']}): the studio and how it works
- [Enquire]({URL['contact']}): check dates and request a quote

## Social
- [Instagram @snapeo_studios]({IG1})
- [Instagram @snapeo_invites]({IG2})

## Optional
- [Full details]({SITE}/llms-full.txt)
''')
    write("llms-full.txt", f'''# Snapeo Studios: full reference

Snapeo Studios is a wedding photography and wedding film studio based in Rudrapur, Uttarakhand, India. It takes a limited number of weddings each season. Style: calm direction, natural light, candid moments. Photography and film are shot by one small team.

## Services
- Photography: candid and portrait coverage for every ceremony, hand-edited, delivered in a private gallery
- Films: cinematic highlight film plus a longer feature with speeches and vows
- Pre-wedding shoots
- Albums: archival, hand-bound, designed with the couple
- Destination weddings: across India and abroad, logistics handled by the studio

## Booking process
''' + "\n".join(f"{i + 1}. {n}: {t}" for i, (n, t) in enumerate(STEPS)) + '''

## Recent films
- Moni & Kartik (pre-wedding): https://vimeo.com/1238447668/49f65594b9
- Parimal & Abhijeet: https://vimeo.com/1238442921/849bc381e8
- Tanushree & Dhwaj

## FAQ
''' + "\n".join(f"Q: {q}\nA: {a}" for q, a in FAQ) + f'''

## Contact
- WhatsApp: {WA_DISPLAY}
- Phone: {PHONES[0]}, {PHONES[1]}
- Email: {EMAIL}
- Instagram: {IG1}
- Website: {SITE}/
''')
    print("built", len(ORDER), "pages; versions", v)


if __name__ == "__main__":
    main()
