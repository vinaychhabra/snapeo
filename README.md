# Snapeo Studios website (production: https://www.snapeo.in)

Static site for GitHub Pages. No server needed.

## What is in this folder
| Path | What it is |
|---|---|
| `index.html`, `portfolio/`, `films/`, `experience/`, `about/`, `contact/` | One real page (URL) for each section, so Google can index each one |
| `assets/config.js` | **The one file you edit**: photos, videos, phone numbers, awards. No rebuild needed |
| `assets/style.min.css`, `assets/app.min.js` | Minified site code (generated) |
| `assets/fonts/` | Self-hosted fonts (faster than Google Fonts) |
| `favicon.ico`, `favicon.svg`, `assets/icons/`, `manifest.webmanifest` | Favicon, phone home-screen icons |
| `assets/og.jpg` | 1200x630 image shown when the link is shared on WhatsApp, Facebook, LinkedIn, X |
| `sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt` | Search engine and AI-assistant files |
| `CNAME` | `www.snapeo.in` (tells GitHub Pages the domain) |
| `404.html` | Friendly "page not found" |
| `src/`, `build.py`, `tools/`, `package.json` | Source and build tools (only needed if you change the code or SEO copy) |

## Deploy (GitHub Pages)
1. Put **everything in this folder** at the root of your GitHub repo (index.html must be at the top level), including `CNAME` and `.nojekyll`.
2. Repo > Settings > Pages > Source: "Deploy from a branch", branch `main`, folder `/ (root)`.
3. Custom domain: `www.snapeo.in`, then tick **Enforce HTTPS** once the certificate is ready.
4. DNS at your domain provider:
   - `www` CNAME to `<your-github-username>.github.io`
   - Apex `snapeo.in`: four A records `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`. GitHub then redirects `snapeo.in` to `www.snapeo.in` automatically.
5. Remove the old `v2.snapeo.in` entry from DNS if it is no longer used (or add a redirect to www.snapeo.in).

## After it goes live (important for SEO / AEO / GEO)
1. Google Search Console: add `https://www.snapeo.in/`, submit `https://www.snapeo.in/sitemap.xml`, then "Request indexing" for the 6 pages.
2. Bing Webmaster Tools: import from Search Console (this also feeds ChatGPT search and Copilot).
3. **Google Business Profile** for "Snapeo Studios, Rudrapur": the biggest local-SEO win. Use the same name, phone and website as the site, and add photos and reviews.
4. Test sharing: paste the link in WhatsApp, and check https://search.google.com/test/rich-results for the pages.
5. Keep your name, phone, email and city identical everywhere (Instagram bio, Google Business Profile, wedding directories). Search engines and AI assistants trust consistent facts.

## Editing content
- Photos, videos, awards, phone numbers: edit `assets/config.js`, save, upload. Done.
- Page titles, descriptions, FAQ and the SEO text: edit the top of `build.py`, then run:
  ```
  npm install
  python3 build.py
  ```
  and upload the changed files.

## Make it much faster: host your photos locally
Google Drive links are slow and can be rate-limited. For the best speed:
```
pip install pillow
python3 tools/optimize_images.py  /path/to/your/photos
```
This creates `img/` with small WebP copies. Upload `img/` next to `index.html`, then in `assets/config.js` set:
```
widths:[480,900,1600],
imageTemplate:"/img/{src}-{w}.webp",
```
and replace each photo link with just the file name without extension (for example `"DSC_0412"`).
