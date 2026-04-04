"""
Flask Blueprint for rendering AQW Character Pages with Ruffle.
Proxies the Flash SWF embed from account.aq.com/CharPage in a clean 720p window.
Handles CORS issues by proxying game.aq.com SWF assets locally.
"""

import re
import html
from flask import Blueprint, request, Response, redirect, url_for, render_template_string
import requests

charpage = Blueprint("charpage", __name__)

# ── Upstream origins ──────────────────────────────────────────────────────────
AQ_ACCOUNT = "https://account.aq.com"
AQ_GAME = "https://game.aq.com"

# Shared session for connection pooling
session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
})

# ── HTML template ─────────────────────────────────────────────────────────────
PAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=1280">
    <title>{{ char_name }} – AQW Character Viewer</title>
    <style>
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
        html, body {
            width: 100%; height: 100%;
            overflow: hidden;
            background: #FEF1C5;
        }
        .viewer {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100vw;
            height: 100vh;
            background: #FEF1C5;
            overflow: hidden;
            line-height: 0;
        }
        .viewer-inner {
            transform-origin: center center;
        }
        .viewer object, .viewer embed, .viewer ruffle-object {
            display: block;
        }
        #overlay{position:fixed;top:0;left:0;width:100%;height:100%;z-index:50}
        #popup{
            display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
            background:rgba(30,30,30,0.92);color:#fff;padding:40px 60px;border-radius:20px;
            font-size:2em;box-shadow:0 8px 32px rgba(0,0,0,0.4);z-index:100;
            text-align:center;pointer-events:none;opacity:0;transition:opacity 0.25s ease;
        }
        #popup.show{display:block;opacity:1;pointer-events:auto}
        #popup.hide{opacity:0}
        #popup a,#popup a:visited,#popup a:active,#popup a:hover{text-decoration:none;color:inherit;-webkit-tap-highlight-color:transparent;outline:none}
    </style>
</head>
<body>
    <div class="viewer">
        <div class="viewer-inner" id="viewer-inner">
        {{ embed_html | safe }}
        </div>
    </div>
    <div id="overlay"></div>
    <div id="popup"><a href="/"><img src="/assets/Twilly.png" alt="Moglin"
        style="max-width:200px;display:block;margin:0 auto 16px"><span>Moglin</span></a></div>
    <script>
    (function(){
        var hideTimer;
        document.getElementById("overlay").addEventListener("click",function(){
            var p=document.getElementById("popup");
            clearTimeout(hideTimer);
            p.classList.remove("hide");
            p.classList.add("show");
            hideTimer=setTimeout(function(){
                p.classList.add("hide");
                setTimeout(function(){p.classList.remove("show","hide");},300);
            },2000);
        });
    })();
    </script>
    <script>
    (function(){
        function scaleViewer(){
            var inner=document.getElementById("viewer-inner");
            var el=inner.querySelector("object,embed,ruffle-object");
            if(!el)return;
            var ew=parseInt(el.getAttribute("width"))||715;
            var eh=parseInt(el.getAttribute("height"))||455;
            var sx=window.innerWidth/ew;
            var sy=window.innerHeight/eh;
            var s=Math.min(sx,sy);
            inner.style.transform="scale("+s+")";
        }
        window.addEventListener("resize",scaleViewer);
        scaleViewer();
        setTimeout(scaleViewer,1000);
    })();
    </script>

    <!--
      Fetch interceptor — MUST run BEFORE Ruffle loads.
      The characterB.swf ActionScript constructs child-SWF URLs using just
      the hostname (dropping the port), so requests go to http://localhost/…
      instead of http://localhost:5000/….  We patch window.fetch and
      XMLHttpRequest to rewrite those URLs back to the correct origin.
    -->
    <script>
    (function() {
        // Derive the correct origin from the page we're on (e.g. "http://localhost:5000")
        var REAL_ORIGIN = location.protocol + "//" + location.host;  // includes port
        // The broken origin the SWF will produce (hostname without port)
        var BAD_ORIGIN  = location.protocol + "//" + location.hostname; // no port

        // Only patch if the page is served on a non-default port
        if (location.port && location.port !== "80" && location.port !== "443") {

            // ── Patch window.fetch ──────────────────────────────────────
            var _origFetch = window.fetch;
            window.fetch = function(input, init) {
                var url;
                if (input instanceof Request) {
                    url = input.url;
                } else {
                    url = String(input);
                }

                // Rewrite http://localhost/game/… → http://localhost:5000/game/…
                if (url.indexOf(BAD_ORIGIN + "/game/") === 0) {
                    url = REAL_ORIGIN + url.slice(BAD_ORIGIN.length);
                    if (input instanceof Request) {
                        input = new Request(url, input);
                    } else {
                        input = url;
                    }
                }
                return _origFetch.call(this, input, init);
            };

            // ── Patch XMLHttpRequest.open ───────────────────────────────
            var _origOpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function(method, url) {
                if (typeof url === "string" && url.indexOf(BAD_ORIGIN + "/game/") === 0) {
                    url = REAL_ORIGIN + url.slice(BAD_ORIGIN.length);
                }
                return _origOpen.apply(this, [method, url].concat(
                    Array.prototype.slice.call(arguments, 2)
                ));
            };

            console.log("[proxy] fetch interceptor active — rewriting " +
                        BAD_ORIGIN + " → " + REAL_ORIGIN);
        }
    })();
    </script>

    <!-- Ruffle polyfill: auto-replaces the <object>/<embed> -->
    <script src="https://unpkg.com/@ruffle-rs/ruffle"></script>
    <script>
        window.RufflePlayer = window.RufflePlayer || {};
        window.RufflePlayer.config = {
            autoplay: "on",
            unmuteOverlay: "hidden",
            backgroundColor: "#FEF1C5",
            letterbox: "off",
            warnOnUnsupportedContent: false,
        };
    </script>
</body>
</html>"""

# ── Error page ────────────────────────────────────────────────────────────────
ERROR_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Character Not Found</title>
<style>
  body { background:#0b0c10; color:#c5c6c7; font-family:sans-serif;
         display:flex; align-items:center; justify-content:center;
         height:100vh; flex-direction:column; }
  h1 { color:#fc6666; margin-bottom:12px; }
  a  { color:#66fcf1; }
</style></head><body>
<h1>Character "{{ name }}" not found</h1>
<p>Double-check the name and <a href="/">try again</a>.</p>
</body></html>"""


# ═══════════════════════════════════════════════════════════════════════════════
#  Global CORS – every response gets these headers so Ruffle WASM + SWFs work
# ═══════════════════════════════════════════════════════════════════════════════

@charpage.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    return response


@charpage.route("/game/<path:subpath>", methods=["OPTIONS"])
@charpage.route("/account/<path:subpath>", methods=["OPTIONS"])
@charpage.route("/charpage", methods=["OPTIONS"])
@charpage.route("/charpage/<path:path>", methods=["OPTIONS"])
def preflight(**kwargs):
    """Handle CORS preflight for charpage routes."""
    return Response(status=204)


# ═══════════════════════════════════════════════════════════════════════════════
#  Routes
# ═══════════════════════════════════════════════════════════════════════════════

@charpage.route("/charpage")
def charpage_index():
    """Landing page redirects to a default character"""
    return redirect(url_for("charpage.char_page", id="Linda Wilds"))


@charpage.route("/charpage/char")
def char_page():
    """
    Main route: fetch the AQ character page, extract the <object> embed,
    rewrite SWF URLs to go through our proxy, and render in a 720p shell.
    """
    char_name = request.args.get("id", "").strip()
    if not char_name:
        return redirect(url_for("index"))

    # Fetch the real character page
    try:
        resp = session.get(
            f"{AQ_ACCOUNT}/CharPage",
            params={"id": char_name},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        return render_template_string(ERROR_TEMPLATE, name=char_name), 502

    page_html = resp.text

    # Detect "character not found" (page returns 200 but shows error)
    if "Character not found" in page_html or "There was an error processing your request" in page_html:
        return render_template_string(ERROR_TEMPLATE, name=char_name), 404

    # ── Extract the <object>…</object> block ──────────────────────────────
    embed_html = _extract_embed(page_html)
    if not embed_html:
        return render_template_string(ERROR_TEMPLATE, name=char_name), 404

    # ── Rewrite SWF URLs to route through our local proxy ─────────────────
    embed_html = _rewrite_swf_urls(embed_html, request.host_url.rstrip("/"))

    # ── Scale the embed to fit 720p ───────────────────────────────────────
    embed_html = _scale_embed(embed_html)

    return render_template_string(
        PAGE_TEMPLATE,
        char_name=html.escape(char_name),
        embed_html=embed_html,
    )


# ── SWF / asset proxy ────────────────────────────────────────────────────────

@charpage.route("/game/<path:subpath>")
def proxy_game(subpath):
    """Proxy requests to game.aq.com/game/… (SWF files, badges, etc.)."""
    upstream = f"{AQ_GAME}/game/{subpath}"
    return _proxy(upstream)


@charpage.route("/account/<path:subpath>")
def proxy_account(subpath):
    """Proxy requests to account.aq.com/… (images, CSS)."""
    upstream = f"{AQ_ACCOUNT}/{subpath}"
    return _proxy(upstream)


# ═══════════════════════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _proxy(upstream_url: str) -> Response:
    """Generic reverse-proxy: streams the upstream response back to the client."""
    qs = request.query_string.decode()
    if qs:
        upstream_url += f"?{qs}"

    try:
        upstream = session.get(upstream_url, stream=True, timeout=30)
    except requests.RequestException:
        return Response("Upstream unreachable", status=502)

    # Build hop-by-hop–safe headers
    excluded = {"transfer-encoding", "connection", "keep-alive",
                "content-encoding", "content-length"}
    headers = {
        k: v for k, v in upstream.headers.items()
        if k.lower() not in excluded
    }

    return Response(
        upstream.iter_content(chunk_size=65536),
        status=upstream.status_code,
        headers=headers,
    )


def _extract_embed(page_html: str) -> str | None:
    """Pull out the <object>…</object> Flash embed from the full page HTML."""
    match = re.search(
        r"(<object\b[^>]*>.*?</object>)",
        page_html,
        re.DOTALL | re.IGNORECASE,
    )
    return match.group(1) if match else None


def _rewrite_swf_urls(embed_html: str, base: str = "") -> str:
    """
    Rewrite absolute game.aq.com / account.aq.com URLs to our local proxy
    using ABSOLUTE URLs (including host + port) so that SWF child-loads
    resolve to the correct origin instead of defaulting to port 80.
    """
    local_game = f"{base}/game/"
    local_account = f"{base}/account/"

    # game.aq.com  → http://localhost:5000/game/
    embed_html = embed_html.replace("https://game.aq.com/game/", local_game)
    embed_html = embed_html.replace("http://game.aq.com/game/", local_game)
    embed_html = embed_html.replace("//game.aq.com/game/", local_game)

    # account.aq.com  → http://localhost:5000/account/
    embed_html = embed_html.replace("https://account.aq.com/", local_account)
    embed_html = embed_html.replace("http://account.aq.com/", local_account)
    embed_html = embed_html.replace("//account.aq.com/", local_account)
    return embed_html


def _scale_embed(embed_html: str) -> str:
    """Keep original dimensions — CSS transform handles viewport scaling."""
    return embed_html


# ═══════════════════════════════════════════════════════════════════════════════
