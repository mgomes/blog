# Blog

Mauricio's personal blog at mauriciogomes.com. A **Hugo** static site (v0.164, standard build; extended is not required), deployed to **Cloudflare Pages**.

It used to run on Blot. Nothing about that setup applies any more. If you find advice about `posts/` at the repo root, plain-key-line frontmatter, or pandoc, it is stale.

## Layout

- `content/posts/` — published posts, one markdown file each, YAML frontmatter
- `content/now.md`, `content/_index.md` — standalone pages
- `layouts/` — flat Hugo layout names (`home.html`, `page.html`, `section.html`, `term.html`); partials in `layouts/_partials/`
- `assets/css/` — `main.css` is the entire design; `chroma.css` / `chroma-dark.css` are generated
- `static/` — fonts, KaTeX, the vendored justif bundle, images under `_Images/`

Drafts are `draft: true` in frontmatter, not a separate directory. `just serve` shows them.

Posts with non-ASCII titles keep an ASCII filename and override the path with `url:` in frontmatter. See `content/posts/computing-pi-in-go.md`, which serves from `/computing-π-in-go/`.

## Commands

| | |
|---|---|
| `just` / `just serve` | dev server on :1313 with drafts and future-dated posts |
| `just build` | production build into `public/` |
| `just draft <slug>` | scaffold a post from `archetypes/posts.md` |
| `just chroma` | regenerate both syntax-highlighting stylesheets |

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

Type is MonoLisa throughout: `MonoLisaText` for prose, `MonoLisaCode` for code, self-hosted and subset by `unicode-range`.

### Syntax highlighting is generated

Never hand-edit `chroma.css` or `chroma-dark.css`. Run `just chroma`.

Each sheet is scoped to its own `prefers-color-scheme` query rather than layered light-then-dark. That is load-bearing: the two Chroma styles **do not emit the same selector set**. `github` emits `.bp`, `.na`, `.nb`, `.p` and `github-dark` does not, so an unscoped light sheet leaks near-black punctuation into every dark code block. The recipe also strips only the wrapper's own background, because the token backgrounds on `.err`, `.hl`, `.gd` and `.gi` are meaningful.

### `:visited` is heavily constrained

Browsers restrict `:visited` styling for privacy, and two limits shape the link treatment:

- **Only color properties apply.** `color`, `background-color`, `border-*-color`, `outline-color`, and `text-decoration-color` work. **`box-shadow` does not.** The highlighter is built from `text-decoration` for exactly this reason; an earlier border-plus-inset-shadow version could only ever recolor half of itself.
- **Alpha is forced to 1.** An `rgba()` at 50% renders fully opaque on a visited link. That is why the `--mark*` tokens are opaque pre-composites against `--bg` rather than translucent colors. If you retune them, composite by hand or the visited state will come out roughly twice as heavy as the unvisited one.

Hover recolors the ink *and* the background together. Setting only the background leaves the resting-colored marker band sitting on top of the flood as a stripe.

## justif (the sharp edge)

Prose is justified client-side by **justif**, vendored at `static/js/justif/`, driven by `static/js/justif/init.js`.

**Never re-enable justif's `auto.js`.** It runs render-blocking, before the self-hosted fonts arrive, so it measures against fallback metrics. `init.js` waits for `document.fonts.ready` instead. **Never enable `hangingPunctuation`** either; it corrupts line measurement on this site, producing huge word gaps in paragraphs containing links.

Three things must move together, and nothing warns you if they drift:

1. The justify selector in `main.css` (`.container p:not(.light), .container li, .container blockquote`)
2. The identical selector in `init.js`
3. The font stack and `16px` size hardcoded in `init.js`

Changing the body font family, the body font size, or that selector without updating `init.js` makes justif silently measure the wrong thing. Headings are not justified, so heading sizes and `letter-spacing` are safe. Do not put `letter-spacing` on justified prose.

Because justif runs after fonts load, the prose is hidden until it finishes, otherwise the browser's own justification paints first and every line visibly re-breaks. The `justif-pending` class is added by an inline script in `head.html` and cleared by `init.js`. It has two backstops: the class is only ever added by script, so no-JS renders normally, and a timer in `head.html` plus a `finally` in `init.js` clear it if justif never completes. Keep both.

### Regression test

After touching anything above, load `/computing-π-in-go/` and check the paragraph containing the bigfft link. Healthy justification puts max `word-spacing` in the low single digits of px:

```js
Math.max(...[...document.querySelectorAll('.justif-seg')]
  .map(s => parseFloat(s.style.wordSpacing) || 0))
```

The known failure mode produces gaps around 72px.

## Verifying visual work

`just serve`, then drive Chrome DevTools MCP. `emulate` takes `colorScheme: "dark" | "light"` and a `viewport` string, which is the only sane way to check both schemes and the 600 / 1060 / 1200px breakpoints.

`getComputedStyle` **lies about `:visited`** by design, always reporting the unvisited style. Verify visited links by screenshot, and remember the browser needs real history for the URL, so localhost and production have separate visit state.
