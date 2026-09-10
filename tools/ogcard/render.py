#!/usr/bin/env python3
"""Render the OpenGraph cards and the favicon PNGs with headless Chrome.

`just og` runs this. It builds the site once more with og.toml merged in,
which adds an "og" output format so the home page and every post also render
as a 1200x630 card page, serves that build on a local port, and screenshots
each card into static/ (the home card is og-card.png, posts go under og/).
The favicon PNGs come from static/favicon.svg the same way.

Drafts and future-dated posts are included so a card is ready by the time a
post publishes. Only the standard library and Google Chrome are needed.
"""

import concurrent.futures
import functools
import http.server
import json
import pathlib
import subprocess
import sys
import tempfile
import threading

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHROME = pathlib.Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
STATIC = ROOT / "static"
CARD = (1200, 630)
WORKERS = 4

# Two icon pages: the touch icon fills its square with the ground color (iOS
# rounds the corners itself), the favicon keeps the SVG's corners over
# transparency. The ground color repeats favicon.svg's on purpose; it is the
# only place outside that file that knows it.
ICONS = {
    "apple-touch-icon.png": (180, False, '<body style="margin:0;background:#141517">'
                             '<img src="/favicon.svg" style="display:block;width:180px;height:180px"></body>'),
    "favicon.png": (64, True, '<body style="margin:0"><img src="/favicon.svg" style="display:block;width:64px;height:64px"></body>'),
}


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def build(dest):
    subprocess.run(
        ["hugo", "--quiet", "-D", "-F", "--config", "hugo.toml,tools/ogcard/og.toml", "--destination", str(dest)],
        cwd=ROOT, check=True,
    )


def serve(root):
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def shoot(url, out, size, profile, transparent=False):
    """Screenshot url into out. Chrome on macOS writes the file and then
    lingers, so the process is killed as soon as it reports the write."""
    out.parent.mkdir(parents=True, exist_ok=True)
    args = [
        str(CHROME), "--headless", "--disable-gpu", "--hide-scrollbars",
        "--no-first-run", "--no-default-browser-check", "--force-light-mode",
        f"--user-data-dir={profile}", f"--window-size={size},{size if isinstance(size, int) else size}",
    ]
    w, h = (size, size) if isinstance(size, int) else size
    args[-1] = f"--window-size={w},{h}"
    if transparent:
        args.append("--default-background-color=00000000")
    args += ["--virtual-time-budget=5000", f"--screenshot={out}", url]
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    watchdog = threading.Timer(90, proc.kill)
    watchdog.start()
    written = False
    try:
        for line in proc.stderr:
            if "written to file" in line:
                written = True
                break
    finally:
        watchdog.cancel()
        proc.kill()
        proc.wait()
    if not written:
        raise RuntimeError(f"Chrome did not render {url}")


def main():
    if not CHROME.exists():
        sys.exit(f"Google Chrome not found at {CHROME}")
    with tempfile.TemporaryDirectory(prefix="ogcard-") as tmp:
        tmp = pathlib.Path(tmp)
        dest = tmp / "site"
        build(dest)
        for name, (_, _, body) in ICONS.items():
            (dest / f"icon-{name}.html").write_text(f"<!DOCTYPE html><html><head><meta charset=utf-8></head>{body}</html>")
        server = serve(dest)
        base = f"http://127.0.0.1:{server.server_address[1]}"
        cards = json.loads((dest / "og-manifest.json").read_text())

        jobs = [(base + c["url"], STATIC / f"{c['name']}.png", CARD, False) for c in cards]
        jobs += [(f"{base}/icon-{name}.html", STATIC / name, px, alpha) for name, (px, alpha, _) in ICONS.items()]
        with concurrent.futures.ThreadPoolExecutor(WORKERS) as pool:
            futures = {
                pool.submit(shoot, url, out, size, tmp / f"profile-{i}", alpha): out
                for i, (url, out, size, alpha) in enumerate(jobs)
            }
            for future in concurrent.futures.as_completed(futures):
                future.result()
                print(futures[future].relative_to(ROOT))
        server.shutdown()


if __name__ == "__main__":
    main()
