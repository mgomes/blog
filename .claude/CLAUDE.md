# Blog

Mauricio's personal blog at mauriciogomes.com. A **Hugo** static site (v0.164, standard build; extended is not required), deployed to **Cloudflare Pages**.

It used to run on Blot. Nothing about that setup applies any more. If you find advice about `posts/` at the repo root, plain-key-line frontmatter, or pandoc, it is stale.

## Layout

- `content/posts/` — published posts, one markdown file each, YAML frontmatter
- `content/about.md`, `content/now.md`, `content/subscribe.md` — standalone pages
- `content/_index.md` — home hero copy: the `tagline` param and the wanted-ad body (the `**WANTED:**` label is part of the markdown)
- `layouts/` — flat Hugo layout names (`home.html`, `page.html`, `section.html`, `term.html`); partials in `layouts/_partials/`; `layouts/_shortcodes/youtube.html` overrides Hugo's built-in so embeds sit in the framed `.embed` box
- `assets/css/` — `main.css` is the entire design; `chroma.css` / `chroma-dark.css` are generated
- `static/` — fonts (MonoLisa and Inter Tight, self-hosted), KaTeX, the vendored justif bundle, `avatar-portrait.png` for the masthead, images under `_Images/`

Drafts are `draft: true` in frontmatter, not a separate directory. `just serve` shows them.

Posts with non-ASCII titles keep an ASCII filename and override the path with `url:` in frontmatter. See `content/posts/computing-pi-in-go.md`, which serves from `/computing-π-in-go/`.

## Commands

| | |
|---|---|
| `just` / `just serve` | dev server on :1313 with drafts and future-dated posts |
| `just build` | production build into `public/` |
| `just draft <slug>` | scaffold a post from `archetypes/posts.md` |
| `just chroma` | regenerate both syntax-highlighting stylesheets |
| `just walks` | regenerate per-post drunkard's-walk art (run after adding a post) |

## Deploy

Pushing `master` to the `github` remote deploys via Cloudflare Pages' native git integration. There is no build workflow for this; `.github/workflows/deploy.yml` only fires a nightly deploy hook so future-dated posts publish on schedule (`buildFuture = false`).

The `blot` remote is the dead Blot repo. Never push to it.

## Voice

First person, conversational, grounded. Explain with plain analogies, be honest about uncertainty, and do not over-embellish or hype. **No em-dashes**, and no ` -- ` dash-asides. Rephrase into commas, parentheses, or separate sentences.

## Math

Hugo renders math with **KaTeX at build time** via goldmark passthrough (`hugo.toml`) and `layouts/_markup/render-passthrough.html`.

- Write **single backslashes**: `\frac`, `\sum`, `\pi`. The old Blot setup ran markdown through pandoc, which ate LaTeX commands and needed every backslash doubled. That is gone, and doubling them now would break the formula.
- **Block only.** The config sets `inline = []`, so `$$...$$` must sit on its own lines. There is no inline math.
- Add `math: true` to the post's frontmatter. It gates the KaTeX stylesheet in `head.html`; without it the formula renders unstyled.

## Design

`assets/css/main.css` is the whole design. Every color is a `:root` custom property, and dark mode is a `prefers-color-scheme` block that redeclares those tokens. There is no theme toggle and no theme JS. Add colors as tokens, not literals, or dark mode silently misses them.

The look is the "studio" direction from the September 2026 mockups: one centered column on paper (`#fbfbf7`) or near-black (`#141517`), a lime accent (`#d4ff2b`), a faint lime halo behind the masthead, and Inter Tight for everything that is not prose. The two modes differ in *treatment* as well as color, and those differences are tokens too, so the dark block stays the single switch:

- **On paper the lime is a highlighter.** It underlines links 2px thick and floods a link on hover (`--link-hover-bg`).
- **In the dark the lime is ink.** Underlines thin to 1px, and hover recolors the text instead of flooding it. The pager has its own `--pager-*` set for the same reason.
- The marker square (`.marker`) gets an ink outline on paper (`--marker-ring`) and none in the dark, so both modes share one mark.

Prose sits one step below the ink (`--prose`), while titles, links and code chips use `--fg` and h2+ and `strong` use `--fg-strong`, which is white in the dark and ink on paper.

There is no visited-link color. The previous design had one; this one has a single link treatment, and chrome links (masthead, nav, footer, meta, post rows) opt out of the underline with `text-decoration: none` plus a hover that resets `background`.

Type is `MonoLisaText` for prose, `MonoLisaCode` for code and the meta line, and `InterTight` for the masthead, titles, headings, list titles and the pill button. Everything is self-hosted from `static/fonts/`; nothing loads from a third-party host. Inter Tight is the Google Fonts variable file (SIL OFL, license alongside it), instanced to weights 500–800 and subset to Latin plus Greek with fonttools so "Computing π in Go" keeps its pi.

The home hero is a wanted ad torn out of a newspaper: a ragged scrap of newsprint (`.tearout-paper`, a `clip-path` polygon in `--tear`) with the ad's 3px rule box on top, both tilted the same 1.2 degrees. The copy comes from `content/_index.md` and the h1 is the site title in tracked caps behind a marker square. Its paragraph uses native `text-align: justify` on purpose; the wide word gaps are part of the classified look, and it sits outside `.container` so justif never touches it.

### Layout notes

- `body` is a flex column so the footer pins to the bottom of short pages. `.main` is the 680px reading column; the home page adds `.main-wide` for 900px.
- The halo is a `radial-gradient` on `body`, sized in px vertically on purpose. A percentage would scale with document height, so a long post would get a glow reaching halfway down the page.
- Breakpoints: 900px tightens the post-list date column, 720px is the phone layout (title above date and tag in each row, wrapped nav, the hero meta line in block flow so its marker square stops wrapping onto a line of its own).

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

Hover is where the two modes diverge most (lime flood on paper, lime text in the dark), so check a prose link, a post row, the pager and the Subscribe pill in both schemes.
