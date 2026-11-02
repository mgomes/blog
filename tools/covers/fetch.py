# /// script
# requires-python = ">=3.11"
# dependencies = ["truststore"]
# ///
"""Fetch cover art for film and TV notes from TMDB into assets/covers/.

`just cover <slug>` fetches one note's art; `just cover` alone fetches every
film or tv note that has none yet. Films get their poster, which fills the frame of
film; shows get a backdrop, since a landscape still suits the TV's screen
better than a portrait poster (falling back to the poster when there is no
backdrop). Hugo resizes whatever lands in assets/covers/<slug>.* for the
card and the page, so art dropped there by hand works too, for books and
records included.

The match is searched by title and year, then pinned by writing its id into
the note as `tmdb: <id>`. If the search picked the wrong thing, correct that
id and rerun with --force; a pinned id is fetched directly.

Needs TMDB_API_KEY in the environment, either the v3 API key or the v4 read
access token, both at https://www.themoviedb.org/settings/api. `just cover`
fills it from the 1Password item Private/Themoviedb when it is unset.
"""

import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

import truststore

ROOT = pathlib.Path(__file__).resolve().parents[2]
NOTES = ROOT / "content" / "notes"
COVERS = ROOT / "assets" / "covers"
API = "https://api.themoviedb.org/3"
IMAGES = "https://image.tmdb.org/t/p/w780"
KINDS = {"film": "movie", "tv": "tv"}


class Miss(Exception):
    """A note whose art could not be fetched."""


def front_matter(text):
    """The scalar keys of a note's YAML front matter, quotes stripped."""
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"([A-Za-z_]+):\s*(.*)$", line)
        if kv:
            out[kv.group(1)] = kv.group(2).strip().strip("'\"")
    return out


def write(path, data):
    """Replace path in one step, so a watching `hugo server` never reads a
    half-written note and renders its front matter as the body."""
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def pin(path, text, tmdb_id):
    """Write tmdb: <id> into the front matter, replacing any earlier one."""
    head, sep, body = text.partition("\n---\n")
    head = re.sub(r"\ntmdb:.*", "", head)
    write(path, f"{head}\ntmdb: {tmdb_id}{sep}{body}".encode())


def get(url, key, params=None):
    params = dict(params or {})
    headers = {"Accept": "application/json"}
    # A read access token is a JWT; a v3 key is 32 hex characters.
    if key.startswith("eyJ"):
        headers["Authorization"] = f"Bearer {key}"
    else:
        params["api_key"] = key
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as r:
        return json.load(r)


def search(kind, title, year, key):
    year_param = "primary_release_year" if kind == "movie" else "first_air_date_year"
    tries = [{"query": title, year_param: year}] if year else []
    tries.append({"query": title})
    for params in tries:
        results = get(f"{API}/search/{kind}", key, params).get("results", [])
        if results:
            return results[0]
    return None


def fetch(slug, key, force=False):
    path = NOTES / f"{slug}.md"
    if not path.exists():
        raise Miss(f"no such note at {path.relative_to(ROOT)}")
    text = path.read_text()
    fm = front_matter(text)
    kind = KINDS.get(fm.get("medium", ""))
    if not kind:
        raise Miss(f"medium {fm.get('medium')!r} is not on TMDB (film and tv only); drop art in assets/covers/ by hand")
    if not force and any(COVERS.glob(f"{slug}.*")):
        return f"{slug}: already has a cover (use --force to refetch)"

    if fm.get("tmdb"):
        item = get(f"{API}/{kind}/{fm['tmdb']}", key)
    else:
        item = search(kind, fm.get("title", slug), fm.get("year"), key)
        if not item:
            raise Miss(f"nothing on TMDB for {fm.get('title')!r}; set tmdb: <id> in the note and rerun")

    art = (item.get("backdrop_path") if kind == "tv" else None) or item.get("poster_path")
    if not art:
        raise Miss(f"TMDB {kind} {item['id']} has no artwork")

    # Download first, so a failed refetch leaves the current cover in place.
    with urllib.request.urlopen(f"{IMAGES}{art}", timeout=30) as r:
        data = r.read()
    COVERS.mkdir(parents=True, exist_ok=True)
    out = COVERS / f"{slug}{pathlib.PurePosixPath(art).suffix or '.jpg'}"
    write(out, data)
    for old in COVERS.glob(f"{slug}.*"):
        if old != out:
            old.unlink()
    if str(item["id"]) != fm.get("tmdb"):
        pin(path, text, item["id"])
    else:
        # hugo server doesn't notice a new file in assets/ that a template
        # only finds by GetMatch; touching the note makes it re-render.
        os.utime(path)

    name = item.get("title") or item.get("name")
    date = item.get("release_date") or item.get("first_air_date") or ""
    return f"{slug}: {name} ({date[:4]}) tmdb {kind} {item['id']} -> {out.relative_to(ROOT)}"


def main():
    args = sys.argv[1:]
    force = "--force" in args
    slugs = [a for a in args if a != "--force"]
    key = os.environ.get("TMDB_API_KEY", "").strip()
    if not key:
        sys.exit("Set TMDB_API_KEY to a TMDB API key or read access token "
                 "(https://www.themoviedb.org/settings/api).")
    truststore.inject_into_ssl()

    if not slugs:
        slugs = sorted(p.stem for p in NOTES.glob("*.md")
                       if p.name != "_index.md" and front_matter(p.read_text()).get("medium") in KINDS)
        if not force:
            slugs = [s for s in slugs if not any(COVERS.glob(f"{s}.*"))]
        if not slugs:
            print("Every film and tv note already has a cover.")
            return

    failed = False
    for slug in slugs:
        try:
            print(fetch(slug, key, force))
        except Miss as e:
            print(f"{slug}: {e}", file=sys.stderr)
            failed = True
        except urllib.error.HTTPError as e:
            print(f"{slug}: TMDB answered {e.code} {e.reason}", file=sys.stderr)
            failed = True
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
