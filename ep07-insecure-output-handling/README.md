# Ep 7 · Insecure output handling: "When AI Output Becomes XSS (and SQL Injection)"

ReviewBot summarises customer reviews inside PixelKart's admin dashboard. Two bugs, both caused by trusting model output:

- **XSS.** One "review" contains an HTML image tag with an `onerror` handler. ReviewBot quotes it faithfully, the dashboard renders the reply as HTML, and the admin's session cookie is sent to the attacker. It really fires in your browser.
- **SQL injection.** ReviewBot turns "reviews for product: X" into a database query by pasting X into the SQL. A crafted product name dumps the users table (fake emails and fake password hashes).

Everything is fake: the shop, the reviews, the users, the admin session. The database is SQLite, recreated on every reset.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep07-insecure-output-handling
pip install -r requirements.txt
python vulnerable/app.py        # http://localhost:5000
```

## Follow along (in the browser, for the XSS)

1. `Summarise the reviews for the Mechanical keyboard.` (normal)
2. `Summarise the reviews for the USB-C hub.` (XSS: watch the **Attacker's server** panel)
3. `Show reviews for product: x' UNION SELECT email, password_hash FROM users --` (SQL injection: watch **SQL the app actually ran**)

`./attack.sh` sends the same three messages from the terminal (the XSS only fires in a browser).

## What was wrong (vulnerable/app.py)

1. **Model output in SQL.** The product name was pasted into the query string.
2. **Model output as HTML.** The reply was rendered with `innerHTML`.
3. **A script-readable session cookie** (no `HttpOnly`).

## The fix (fixed/app.py)

1. **Parameterised queries.** The model's text is a value, never part of the SQL.
2. **Render as text.** The reply is shown as plain text, so markup is inert.
3. **HttpOnly session cookie**, so even a script that slips through can't read it. Add a Content Security Policy in production.

## Take-home checklist

- [ ] Treat model output exactly like user input. *(OWASP LLM05 Improper Output Handling)*
- [ ] Encode output for where it goes: HTML, SQL, shell, URLs.
- [ ] Parameterise every query built from model output.
- [ ] HttpOnly + Secure cookies, and a strict CSP on any page that shows AI output.
