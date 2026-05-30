# Blog

Mauricio's personal blog, published with **Blot** (the folder becomes the site; dotfiles like this one are ignored by Blot). Published posts live in `posts/`, works-in-progress in `drafts/` (unpublished). Frontmatter is plain key lines at the top (`Date:`, `Tags:`, optional `Summary:`), then `# Title` and `##` sections.

## Voice

First person, conversational, grounded. Explain with plain analogies, be honest about uncertainty, and do not over-embellish or hype. **No em-dashes**, and no ` -- ` dash-asides — rephrase into commas, parentheses, or separate sentences.

## Math (the important gotcha)

Blot renders math with **KaTeX, server-side**. The delimiter is `$$...$$` (both inline mid-sentence and display on its own lines). There is no single-`$` support.

Blot runs Markdown through **pandoc with `raw_tex` on** (and `tex_math_dollars` off). Pandoc parses LaTeX commands like `\frac`, `\sum`, `\sqrt`, `\log`, `\infty` as raw TeX and **drops them** before KaTeX runs, so `$$\frac{1}{\pi}...$$` renders as just the leftover non-command text (e.g. `= 12 _{k=0}^{}`).

**Fix: double every backslash** in math so pandoc emits a literal `\`. Write `\\frac`, `\\sum`, `\\pi`, `\\sqrt`, etc. KaTeX then receives the correct single-backslash commands. Plain expressions with no backslash (like `O(n^2)`) are fine as-is; for prose, plain `O(n log n)` / `√10005` sidesteps the issue entirely.

To debug a broken formula: `curl` the draft preview URL (`mauriciogomes.com/draft/view/...`) and inspect the KaTeX `annotation` attribute — it shows the exact TeX KaTeX received, which reveals what pandoc stripped.
