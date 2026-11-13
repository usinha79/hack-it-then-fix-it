# CSRF lab: a web page drives your local agent

1. Start RedRange: `python -m redrange.app` (http://localhost:5000).
2. Serve the attacker page from a *different* origin:
   `python -m http.server 8070 --bind 127.0.0.1 --directory attacks/csrf`
3. Open http://127.0.0.1:8070/coupon.html, then reload RedRange. Check "Tool calls" and "Left the building".
4. Restart with `RANGE_FIX=origin` and repeat. The chat API now only accepts JSON requests that carry the
   RedRange page's own cookie, so the form post is refused with 403.

Lab only: everything runs on 127.0.0.1 with fake data. See SAFETY.md.
