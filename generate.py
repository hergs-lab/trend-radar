"""
Social Trend Radar — weekly generator
Calls the Anthropic API with web search enabled, generates the HTML report,
and writes it to docs/index.html (served by GitHub Pages).
"""

import anthropic
import os
from datetime import datetime

# ── Prompt ────────────────────────────────────────────────────────────────────

def build_prompt(date_str: str) -> str:
    return f"""
You are producing the City of Sydney Digital Content Team's weekly Social Trend Radar.
Today's date is {date_str}.

## Your task

Research what is currently trending on TikTok, Instagram, LinkedIn, and YouTube,
then produce a single self-contained HTML file that the team can open in a browser
during their Monday ideation meeting.

## Research instructions

Run targeted web searches for each platform using queries like:
- "TikTok trending content formats {date_str[:7]}"
- "Instagram Reels trends creators {date_str[:7]}"
- "LinkedIn content trends engagement {date_str[:7]}"
- "YouTube trending video formats {date_str[:7]}"
- "social media creator trends what's working {date_str[:7]}"

For each platform identify 3 trends. For each trend surface:
1. What the trend looks like in practice
2. Specific named creators or brands doing it well (or a category description if none found)
3. Why it is working (algorithm context or audience behaviour)

Prioritise sources: Later, Sprout Social, Social Insider, Hootsuite blog,
platform newsrooms, creator newsletters, marketing trade press.

## HTML output requirements

Produce a complete, self-contained HTML file. All CSS must be inline in a
<style> tag. No external CSS files. Use Google Fonts via a <link> tag.

### Design system (City of Sydney — Digital Design Language)

IMPORTANT: Do NOT use Google Fonts. Do NOT include any <link> tag for fonts.

Font stack: 'Helvetica Now', Helvetica, Arial, sans-serif — used for everything.
Helvetica Now is a licensed font; the fallback to Helvetica (available on macOS/iOS)
and system sans-serif is correct and intentional.

Font weight guidance (from CoS typography spec):
- Large headings (page title, platform headings): font-weight 700 (Display Bold)
- Small headings (card titles, section labels): font-weight 700 (Text Bold)
- Body text: font-weight 400 (Text Regular)
- XS-Cap labels (trend numbers, tag labels): font-weight 700 (Micro Bold), uppercase, letter-spacing 0.12em

Colour tokens — City of Sydney Digital Design Language (Isobar/Sitecore):
  --bg:        #041C2C   (Core Deep Blue 100 — primary dark background)
  --surface:   #0a2a3d   (slightly lighter dark surface for cards)
  --surface2:  #0f3350   (card hover state)
  --border:    #1a3d52   (border/divider on dark)
  --text:      #ffffff   (Core White — primary text on dark)
  --muted:     #7a9ab0   (Core Deep Blue 75 adjusted for dark bg contrast)
  --soft:      #a8bfcc   (soft label text on dark bg)
  --cos-blue:  #0850A1   (Core Blue 100 — interactive/link colour)
  --cos-green: #188838   (Core Green 110 — accessible link on white)
  --cos-red:   #B00020   (Potts Point Red 110 — ERROR STATES ONLY, never use as accent)
  --cos-light: #F2ECE7   (Core Light — warm light background, used sparingly)
  --accent:    #188838   (Core Green 110 — CoS primary accent, use for signal tags and labels)

Top brand bar: 5px solid #041C2C with a 2px bottom border in #188838 (Core Green 110)

Platform accent colours (left card border and platform heading only — these are product brand colours, not CoS brand):
  TikTok:    #ff2d55
  Instagram: #e1a84a
  LinkedIn:  #4a9eed
  YouTube:   #e84040

### Page structure

1. A 5px solid bar at the very top in #041C2C with a 2px bottom border in #188838 (Core Green 110 — CoS brand bar)
2. Header: "Social Trend Radar" as large bold heading + "Week of {date_str}" + platform colour dots
3. Nav bar with smooth-scroll anchors: TikTok | Instagram | LinkedIn | YouTube
4. Four platform sections, each containing a 3-column card grid
5. Footer with sources

### Card structure (every card must have all five elements)

- Trend number (e.g. TK-01) — small caps label in platform colour
- Trend title — semibold, 18px
- Insight line — single sharp sentence, font-weight 500, most prominent text element,
  separated from detail by a border-bottom
- Detail paragraph — 2-3 sentences, muted colour, supporting context
- Creators panel — boxed panel with label "DOING IT WELL" in platform colour,
  containing 2 named entries (creator name + one-line reason why).
  If no specific account was found, use a category description.
- Tags row — 2-3 short uppercase labels. Signal tags use --accent colour.

### Other requirements

- Staggered fade-up animation on section load
- Sticky nav bar
- Scroll hint in bottom-right corner that fades on scroll
- Mobile responsive (single column below 900px)
- No JavaScript frameworks — vanilla JS only
- The file must be completely self-contained and render correctly when opened
  directly in a browser with no internet connection (except Google Fonts)

### Enduring trends section

After the four platform sections and before the footer, include an "Enduring Trends" section.

Research instructions for this section:
Search for phrases like "social media formats still working 2025", "evergreen content trends",
"durable social media strategies", "content formats with lasting engagement". Identify 4-5
trends that have been consistently present and effective for 6+ months across platforms.
These should NOT be new or emerging — they are durable behaviours that teams should keep
in their ongoing content mix.

For each enduring trend provide:
1. A short name (3-5 words)
2. A one-line rationale (why it keeps working, ~20 words)
3. A momentum signal: "still growing", "plateaued", or "declining/maturing"

HTML structure for this section:

<section class="enduring-section">
  <div class="enduring-header">
    <div>
      <div class="enduring-label">Always in the mix</div>
      <div class="enduring-title">Enduring Trends</div>
      <div class="enduring-subtitle">Not new — but still working. Durable formats worth keeping in your content mix.</div>
    </div>
  </div>
  <div class="enduring-strip">
    <div class="enduring-item">
      <div class="enduring-name">[Trend name]</div>
      <div class="enduring-rationale">[One-line rationale]</div>
      <span class="enduring-momentum [growing|plateaued|declining]">[↑ Still growing | → Plateaued | ↓ Maturing]</span>
    </div>
    <!-- repeat for each trend -->
  </div>
</section>

CSS for enduring section (include in the <style> block):

  .enduring-section {{
    background: #F2ECE7;
    padding: 52px 80px;
    border-top: 1px solid #d4ccc6;
  }}
  .enduring-header {{ margin-bottom: 32px; }}
  .enduring-label {{
    font-family: 'Helvetica Now', Helvetica, Arial, sans-serif;
    font-size: 10px; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #188838;
  }}
  .enduring-title {{
    font-family: 'Helvetica Now', Helvetica, Arial, sans-serif;
    font-size: 22px; font-weight: 700; color: #041C2C;
  }}
  .enduring-subtitle {{
    font-family: 'Helvetica Now', Helvetica, Arial, sans-serif;
    font-size: 13px; color: #4E5A5F; margin-top: 4px;
  }}
  .enduring-strip {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1px; background: #d4ccc6; border: 1px solid #d4ccc6;
  }}
  .enduring-item {{
    background: #ffffff; padding: 20px 24px;
    display: flex; flex-direction: column; gap: 6px;
  }}
  .enduring-name {{
    font-family: 'Helvetica Now', Helvetica, Arial, sans-serif;
    font-size: 14px; font-weight: 700; color: #041C2C;
  }}
  .enduring-rationale {{
    font-family: 'Helvetica Now', Helvetica, Arial, sans-serif;
    font-size: 12.5px; color: #4E5A5F; line-height: 1.5;
  }}
  .enduring-momentum {{
    margin-top: 6px; display: inline-block;
    font-family: 'Helvetica Now', Helvetica, Arial, sans-serif;
    font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; padding: 3px 8px; border-radius: 2px; align-self: flex-start;
  }}
  .enduring-momentum.growing {{ background: rgba(24,136,56,0.1); color: #188838; }}
  .enduring-momentum.plateaued {{ background: rgba(8,80,161,0.08); color: #0850A1; }}
  .enduring-momentum.declining {{ background: rgba(78,90,95,0.1); color: #4E5A5F; }}

### Nav bar

The nav bar must contain these links in this order:
TikTok | Instagram | LinkedIn | YouTube | Archive

The Archive link must point to: /trend-radar/archive.html
Style it identically to the other nav links.

### Headline link

The "Social Trend Radar" heading in the header must be wrapped in an anchor tag
linking to /trend-radar/ so it acts as a home link. Style it with no underline,
inheriting the heading colour.

### Page completeness

The page MUST include all of the following — do not omit any:
1. Brand bar
2. Header with linked headline
3. Nav bar (TikTok, Instagram, LinkedIn, YouTube, Archive)
4. All four platform sections with 3 cards each
5. Enduring Trends section (the cream-background strip before the footer)
6. Footer with sources

## Output

CRITICAL: Return ONLY the raw HTML. Absolutely nothing before <!DOCTYPE html> —
no commentary, no "here is the file", no "I've researched...", no explanation of
any kind. The very first character of your response must be < and the very last
must be >. Any text outside the HTML tags will break the page.
""".strip()


# ── API call ──────────────────────────────────────────────────────────────────

def generate(date_str: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"Generating trend radar for {date_str}...")

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=16000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": build_prompt(date_str)}],
    )

    # Extract the final text block (after any tool use turns)
    html = ""
    for block in message.content:
        if block.type == "text":
            html = block.text

    # Strip any accidental markdown fences
    if html.startswith("```"):
        html = html.split("\n", 1)[1]
        html = html.rsplit("```", 1)[0]

    # Strip any prose before the DOCTYPE — belt and braces
    if "<!DOCTYPE" in html:
        html = html[html.index("<!DOCTYPE"):]

    return html.strip()


# ── Archive index builder ─────────────────────────────────────────────────────

def build_archive(docs_dir: str) -> str:
    """Scan docs/ for dated HTML files and build a simple archive index page."""
    import re

    dated_files = []
    for fname in sorted(os.listdir(docs_dir), reverse=True):
        if re.match(r"^\d{4}-\d{2}-\d{2}\.html$", fname):
            date_str = fname.replace(".html", "")
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                label = dt.strftime("%-d %B %Y")  # e.g. "17 March 2026"
            except ValueError:
                label = date_str
            dated_files.append((date_str, label, fname))

    rows = ""
    for date_str, label, fname in dated_files:
        rows += f"""
        <a class="archive-row" href="/trend-radar/{fname}">
          <span class="archive-date">{label}</span>
          <span class="archive-arrow">→</span>
        </a>"""

    if not rows:
        rows = '<p class="archive-empty">No archived issues yet. Check back after the first Monday run.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Social Trend Radar — Archive</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Helvetica Now', Helvetica, Arial, sans-serif;
    background: #F2ECE7;
    color: #041C2C;
    min-height: 100vh;
  }}
  .brand-bar {{
    background: #041C2C;
    height: 5px;
    border-bottom: 2px solid #188838;
  }}
  header {{
    padding: 52px 80px 36px;
    background: #F2ECE7;
    border-bottom: 1px solid #d4ccc6;
  }}
  .header-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #188838;
    margin-bottom: 12px;
  }}
  .header-title {{
    font-size: clamp(36px, 4vw, 56px);
    font-weight: 700;
    color: #041C2C;
    line-height: 1;
  }}
  .header-sub {{
    font-size: 14px;
    color: #4E5A5F;
    margin-top: 10px;
  }}
  .header-sub a {{
    color: #0850A1;
    text-decoration: none;
  }}
  .header-sub a:hover {{ text-decoration: underline; }}
  main {{
    max-width: 700px;
    margin: 52px auto;
    padding: 0 80px;
  }}
  .archive-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 24px;
    background: #ffffff;
    border: 1px solid #d4ccc6;
    margin-bottom: 2px;
    text-decoration: none;
    color: #041C2C;
    transition: background 0.15s;
  }}
  .archive-row:hover {{ background: #041C2C; color: #ffffff; }}
  .archive-date {{ font-size: 15px; font-weight: 700; }}
  .archive-arrow {{ font-size: 18px; color: #188838; }}
  .archive-empty {{ color: #4E5A5F; font-size: 14px; padding: 24px 0; }}
  footer {{
    text-align: center;
    padding: 40px 80px;
    font-size: 11px;
    color: #4E5A5F;
    border-top: 1px solid #d4ccc6;
    margin-top: 80px;
  }}
  @media (max-width: 600px) {{
    header, main, footer {{ padding-left: 20px; padding-right: 20px; }}
  }}
</style>
</head>
<body>
<div class="brand-bar"></div>
<header>
  <div class="header-label">City of Sydney — Digital Content Team</div>
  <div class="header-title">Trend Radar<br>Archive</div>
  <div class="header-sub">
    <a href="/trend-radar/">← Current issue</a>
  </div>
</header>
<main>
  {rows}
</main>
<footer>City of Sydney Social Trend Radar — generated weekly by Claude</footer>
</body>
</html>"""


# ── Write output ──────────────────────────────────────────────────────────────

def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    html = generate(date_str)

    os.makedirs("docs", exist_ok=True)

    # 1. Save dated archive copy
    dated_path = f"docs/{date_str}.html"
    with open(dated_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Written archive copy to {dated_path}")

    # 2. Overwrite index.html with current week
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Written to docs/index.html ({len(html):,} chars)")

    # 3. Regenerate archive index
    archive_html = build_archive("docs")
    with open("docs/archive.html", "w", encoding="utf-8") as f:
        f.write(archive_html)
    print("Written docs/archive.html")


if __name__ == "__main__":
    main()
