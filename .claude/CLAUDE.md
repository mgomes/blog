# Blog

Mauricio's personal blog at mauriciogomes.com. A **Hugo** static site (v0.164, standard build; extended is not required), deployed to **Cloudflare Pages**.

It used to run on Blot. Nothing about that setup applies any more. If you find advice about `posts/` at the repo root, plain-key-line frontmatter, or pandoc, it is stale.

## Layout

- `content/posts/` — published posts, one markdown file each, YAML frontmatter
- `content/notes/` — short entries (films, shows, books, records, plain notes), served under `/notes/<slug>/`. See Notes below
- `content/about.md`, `content/now.md`, `content/subscribe.md` — standalone pages
- `content/_index.md` — home hero copy: the `tagline` param and the wanted-ad body (the `**WANTED:**` label is part of the markdown)
- `layouts/` — flat Hugo layout names (`home.html`, `page.html`, `section.html`, `term.html`); partials in `layouts/_partials/` (`tearout.html` is the home hero, `tearout-clip.html` its torn-paper clip path); `layouts/_shortcodes/youtube.html` overrides Hugo's built-in so embeds sit in the framed `.embed` box. `home.og.html`, `posts/page.og.html` and `home.ogmanifest.json` only exist for the `just og` build (see OpenGraph cards below). `_partials/stream.html` and `card.html` are the home and notes card grid; `note-object.html` draws a note's object
- `assets/css/` — `main.css` is the entire design; `chroma.css` / `chroma-dark.css` are generated
- `static/glyphs.svg` — the generated glyph sprite notes print on their objects (`just glyphs`)
- `static/` — fonts (MonoLisa and Inter Tight, self-hosted), KaTeX, the vendored justif bundle, `avatar-portrait.png` for the masthead, `favicon.svg` and its PNG renders, the OpenGraph cards (`og-card.png`, `og/<slug>.png`), images under `_Images/`

Drafts are `draft: true` in frontmatter, not a separate directory. `just serve` shows them.

Posts with non-ASCII titles keep an ASCII filename and override the path with `url:` in frontmatter. See `content/posts/computing-pi-in-go.md`, which serves from `/computing-π-in-go/`.

## Commands

| | |
|---|---|
| `just` / `just serve` | dev server on :1313 with drafts and future-dated posts |
| `just build` | production build into `public/` |
| `just draft <slug>` | scaffold a post from `archetypes/posts.md` |
| `just note <medium> <slug>` | scaffold a note (`film`, `tv`, `book`, `music`, or `note`) from `archetypes/notes.md` |
| `just glyphs` | redraw the glyph sprite from `tools/glyphs/draw.py` |
| `just cover [--force] [slug…]` | fetch film/TV art from TMDB into `assets/covers/` (key from `TMDB_API_KEY`, else 1Password's `Private/Themoviedb` "API Key" via `op`); no slug fetches every film or tv note missing art |
| `just chroma` | regenerate both syntax-highlighting stylesheets |
| `just tear` | retrace the hero's torn-paper clip path from `tools/tearout/success_not_guaranteed.png` |
| `just walks` | regenerate per-post drunkard's-walk art (run after adding a post) |
| `just og` | regenerate the OpenGraph cards and favicon PNGs (run after adding a post, after `just walks`) |

## Deploy

Pushing `master` to the `github` remote deploys via Cloudflare Pages' native git integration. There is no build workflow for this; `.github/workflows/deploy.yml` only fires a nightly deploy hook so future-dated posts publish on schedule (`buildFuture = false`).

The `blot` remote is the dead Blot repo. Never push to it.

## Voice

First person, conversational, grounded. Explain with plain analogies, be honest about uncertainty, and do not over-embellish or hype. **No em-dashes**, and no ` -- ` dash-asides. Rephrase into commas, parentheses, or separate sentences.

## Writing in TinyDesk

Posts and notes can be written in TinyDesk (Mauricio's Markdown app) with `content/` opened as a folder. TinyDesk stores its drafting marks as HTML comments: alternative takes (`<!--td:v id-->…<!--/td:v-->`), ghosted text (`<!--td:ghost-->…<!--/td:ghost-->`), and a shelf of cut snippets plus the takes' data below `<!-- tinydesk:overflow -->`.

`_partials/prose.html` is the page body everywhere it's shown (pages, plain-note cards, the feed, the reading time): it drops ghosts and the shelf, the same text TinyDesk leaves out of its own word count, and unwraps takes. It strips them from the Markdown before rendering, because a paragraph that opens with a mark would otherwise parse as a raw HTML block and lose its Markdown. Pages without marks get `.Content` untouched. Use the partial, not `.Content`, anywhere new that shows a page's text.

## Math

Hugo renders math with **KaTeX at build time** via goldmark passthrough (`hugo.toml`) and `layouts/_markup/render-passthrough.html`.

- Write **single backslashes**: `\frac`, `\sum`, `\pi`. The old Blot setup ran markdown through pandoc, which ate LaTeX commands and needed every backslash doubled. That is gone, and doubling them now would break the formula.
- **Block only.** The config sets `inline = []`, so `$$...$$` must sit on its own lines. There is no inline math.
- Add `math: true` to the post's frontmatter. It gates the KaTeX stylesheet in `head.html`; without it the formula renders unstyled.

## Design

`assets/css/main.css` is the whole design. Every color is a `:root` custom property, and dark mode is a `prefers-color-scheme` block that redeclares those tokens. There is no theme toggle and no theme JS. Add colors as tokens, not literals, or dark mode silently misses them.

The look is the "studio" direction from the September 2026 mockups: one centered column on paper (`#fbfbf7`) or near-black (`#141517`), an ink-blue accent (`#1f3fb4`, lifted to periwinkle `#8ea6ff` in the dark), a faint blue halo behind the masthead, and Inter Tight for everything that is not prose. The two modes differ in *treatment* as well as color, and those differences are tokens too, so the dark block stays the single switch:

- **On paper the blue is a marker.** It underlines links 2px thick and floods a link on hover (`--link-hover-bg`), turning the text paper-white (`--on-accent`).
- **In the dark the blue is ink.** Underlines thin to 1px, and hover recolors the text instead of flooding it. The pager has its own `--pager-*` set for the same reason.
- The accent was lime until November 2026. Dark blue can't do the two jobs lime did with one value (a flood needs light text on it, and dark blue vanishes on near-black), which is why `--accent` and `--on-accent` are redeclared in the dark block.

Safari 26 ignores `theme-color` and tints its toolbar from a fixed element at the page's top edge, so `baseof.html` opens with an 8px `.tint` strip in `--tint` (the ink blue in both modes). It has to be a real element at least about 6px tall; pseudo-elements and thinner strips are ignored.

Prose sits one step below the ink (`--prose`), while titles, links and code chips use `--fg` and h2+ and `strong` use `--fg-strong`, which is white in the dark and ink on paper.

There is no visited-link color. The previous design had one; this one has a single link treatment, and chrome links (masthead, nav, footer, meta, post rows) opt out of the underline with `text-decoration: none` plus a hover that resets `background`.

Type is `MonoLisaText` for prose, `MonoLisaCode` for code and the meta line, and `InterTight` for the masthead, titles, headings, list titles and the pill button. Everything is self-hosted from `static/fonts/`; nothing loads from a third-party host. Inter Tight is the Google Fonts variable file (SIL OFL, license alongside it), instanced to weights 500–800 and subset to Latin plus Greek with fonttools so "Computing π in Go" keeps its pi.

The home hero is a wanted ad torn out of a newspaper (`layouts/_partials/tearout.html`). The scrap is `.tearout` itself, painted in `--tear` and clipped by an SVG `clipPath` in `tearout-clip.html`, which `just tear` (`tools/tearout/trace.py`) traces from the original tear-out PNG kept alongside it, in bounding-box units. Do not hand-edit the path; rerun the trace. The clip cuts the whole object, so the tear takes the ad's top-left corner with it, exactly as in that image, and the ad's 3px rule box sits inside with roughly the image's margins. The whole thing tilts 1.2 degrees. Because the clip stretches to the ad, a taller-than-wide ad (phones) makes the top-left lump run deeper; the 720px breakpoint pads the first line clear of it. The copy comes from `content/_index.md` and the h1 is the site title in tracked caps behind a marker square. Its paragraph uses native `text-align: justify` on purpose; the wide word gaps are part of the classified look, and it sits outside `.container` so justif never touches it.

Above the ad sits a newspaper folio (`.folio` in `home.html`): the tagline left, CLASSIFIEDS in the middle, and the date right, between a hairline and a double rule. The date is the build date, kept current by the nightly deploy. Hugo's `now` is in the build machine's zone (UTC on Cloudflare), so the template moves it into the site's `timeZone` by borrowing the location from a zoneless `time.AsTime`; `time.Format` alone does not convert.

### Notes and the stream

The home page is a masonry grid of cards mixing posts and notes, newest first, 12 to a page. Post cards lead with their walk art. A note's `medium` picks the object its card shows: `film` is a frame of 35mm film, `tv` a portable set with rabbit ears, `book` a paperback with a spine crease and page edge, `music` a sleeve with the record half out. Plain notes (`medium: note`, title optional) have no object; the card is a scrap of the hero's newsprint, clipped to the same `#tear` path, carrying the whole note.

`medium`, not `kind`: Hugo reserves `kind` in front matter and fails the build on it.

Object art follows the Love, Death & Robots title cards: a flat field in one of seven `--swatch-*` colors printed with one to three glyphs (`glyphs: [rocket, eye, skull]`, `color: red`). With no glyphs the medium's own glyph is used; with no color one is picked from a hash of the title. Unknown media, colors and glyph names fail the build. The glyphs are drawn with shapely booleans in `tools/glyphs/draw.py`, so a cut-out is a real hole; add one there and rerun `just glyphs` rather than editing the sprite. `uv run tools/glyphs/draw.py --sheet <file.html>` writes a contact sheet.

A note with art in `assets/covers/<slug>.*` shows that instead of its glyphs, cropped to the object's shape and resized to 180 and 360px wide. `just cover` (`tools/covers/fetch.py`) fetches it from TMDB: posters for films, a backdrop still for TV (it fills the CRT better). It searches by title and year, pins the match as `tmdb: <id>` in the note, and fetches a pinned id directly, so a wrong match is fixed by editing the id and rerunning with `--force`. Note pages with a `tmdb` id and art carry the credit TMDB's terms require. Books and records aren't on TMDB; drop their art in by hand, then touch the note or restart `just serve`, since the dev server doesn't notice a new file it only finds through `resources.GetMatch`. The script writes atomically for the same reason: a half-written note gets rendered with its front matter as body and stays that way.

Objects are sized in em, so one `font-size` scales the whole thing (6px on a card, 12px on the note's page). The swatches hold in both modes; the dark plastics (`--film`, `--tv-body`, `--vinyl`) are lifted in the dark block so they don't sink into the card.

Masonry is `assets/js/stream.js`, inlined right after the grid so it runs before first paint: each card spans as many 1px rows as it is tall, which keeps reading order left to right. Browsers with `display: grid-lanes` skip it.

### Layout notes

- `body` is a flex column so the footer pins to the bottom of short pages. `.main` is the 680px reading column; the home page adds `.main-wide` for 900px.
- The halo is a `radial-gradient` on `body`, sized in px vertically on purpose. A percentage would scale with document height, so a long post would get a glow reaching halfway down the page.
- Breakpoints: 900px tightens the post-list date column, 720px is the phone layout (title above date and tag in each row, wrapped nav, the hero folio restacked with the section on top and place and date beneath).

### OpenGraph cards and favicon are generated

`just og` runs `tools/ogcard/render.py`: it builds the site again with `tools/ogcard/og.toml` merged in, which adds an `og` output format so the home page and every post also render as a 1200x630 card page, serves that build locally, and screenshots each card with headless Google Chrome into `static/og-card.png` (site) and `static/og/<slug>.png` (posts). The PNGs are committed. `head.html` uses a post's own card when its file exists and falls back to the site card. Run it after adding a post, once `just walks` has made the post's walk art, since the post card shows that art behind the tear-out.

The card pages load `assets/css/og.css` after a copy of `main.css` with its dark block stripped (`_partials/og-css.html`), because headless Chrome follows the Mac's color scheme and has no switch for it; the build fails loudly if that block's shape changes. Chrome writes the screenshot and then lingers, so the script kills it once the file lands.

The favicon is `static/favicon.svg` (the marker square in paper on an ink-blue ground). `just og` also renders `favicon.png` and `apple-touch-icon.png` from it.

### Syntax highlighting is generated

Never hand-edit `chroma.css` or `chroma-dark.css`. Run `just chroma`.

Each sheet is scoped to its own `prefers-color-scheme` query rather than layered light-then-dark. That is load-bearing: the two Chroma styles **do not emit the same selector set**. `github` emits `.bp`, `.na`, `.nb`, `.p` and `github-dark` does not, so an unscoped light sheet leaks near-black punctuation into every dark code block. The recipe also strips only the wrapper's own background, because the token backgrounds on `.err`, `.hl`, `.gd` and `.gi` are meaningful.

## justif (the sharp edge)

Prose is justified client-side by **justif**, vendored at `static/js/justif/`, driven by `static/js/justif/init.js`.

**Never re-enable justif's `auto.js`.** It runs render-blocking, before the self-hosted fonts arrive, so it measures against fallback metrics. `init.js` waits for `document.fonts.ready` instead. **Never enable `hangingPunctuation`** either; it corrupts line measurement on this site, producing huge word gaps in paragraphs containing links.

Three things must move together, and nothing warns you if they drift:

1. The justify selector in `main.css` (`.container p:not(.light), .container li, .container blockquote`)
2. The identical selector in `init.js`
3. The font stack and `16px` size hardcoded in `init.js`

Changing the body font family, the body font size, or that selector without updating `init.js` makes justif silently measure the wrong thing. Headings are not justified, so heading sizes and `letter-spacing` are safe. Do not put `letter-spacing` on justified prose.

### The load flicker is known, and hiding the prose makes it worse

Because justif runs after the fonts load, the browser paints its own naive justification first and the lines visibly re-break when justif lands. This was measured at roughly 40ms locally.

Hiding the prose until justif finishes has been tried and reverted. It cannot work from the external stylesheet: the CSS bundle is a separate request, so the text paints unjustified before the hiding rule arrives, then blanks when it does, then reveals. Measured on production that was three visual states instead of two, and clearly worse.

Inlining the rule in `head.html` fixes the ordering but not the real problem. The wait is on a font load of unbounded duration, so any reveal timer either fires early on a slow connection, giving blank then unjustified then justified, or is generous enough to blank the page for seconds. You cannot guarantee both no blank period and no unjustified paint.

The font preloads in `head.html` are the part worth keeping. They shorten the window by getting `document.fonts.ready` to resolve sooner, which is the only lever that helps without a downside.

### Regression test

After touching anything above, load `/computing-π-in-go/` and check the paragraph containing the bigfft link. Healthy justification puts max `word-spacing` in the low single digits of px:

```js
Math.max(...[...document.querySelectorAll('.justif-seg')]
  .map(s => parseFloat(s.style.wordSpacing) || 0))
```

The known failure mode produces gaps around 72px.

## Verifying visual work

`just serve`, then drive Chrome DevTools MCP. `emulate` takes `colorScheme: "dark" | "light"` and a `viewport` string, which is the only sane way to check both schemes and the 720 / 900px breakpoints. If the MCP browser profile is locked by another session, headless Chrome through puppeteer-core with its own `userDataDir` and `emulateMediaFeatures` does the same job.

Hover is where the two modes diverge most (blue flood with paper text on paper, periwinkle text in the dark), so check a prose link, a post row, the pager and the Subscribe pill in both schemes.
