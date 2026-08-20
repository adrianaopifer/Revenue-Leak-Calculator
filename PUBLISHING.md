# Publishing the Opifer Revenue Leak Calculator

Before pushing any public Calculator change:

1. Keep the production page in `index.html`. Do not edit the similarly named legacy HTML file.
2. Preserve one `index, follow` robots directive and the exact self-canonical
   `https://calculator.opiferai.com/`.
3. Keep the title, description, Open Graph, Twitter and WebApplication schema accurate.
4. Keep `robots.txt` crawlable and pointing to the Calculator sitemap.
5. Keep `sitemap.xml` limited to the canonical Calculator URL and update `lastmod` after a real change.
6. Keep `og-calculator.png` at 1200 × 630 pixels.
7. Run `python3 scripts/validate-seo.py`. Do not push if it fails.
8. After GitHub Pages deploys, verify the page, social image, `robots.txt` and `sitemap.xml` return HTTP 200.
