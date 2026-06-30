#!/usr/bin/env python3
"""
Generate privacy-policy pages for Coralia Digital apps, hosted on GitHub Pages.

Each app gets  <repo>/<slug>/privacy.html  ->  https://katinkia.github.io/<slug>/privacy.html
That URL is what you paste into App Store Connect (App Privacy > Privacy Policy URL).

Driven by tools/apps.tsv. Re-running is safe and idempotent: it overwrites the
generated pages and the root index from the registry, so the registry is the
single source of truth.

Usage:
    python3 tools/gen_privacy.py                 # regenerate every app in apps.tsv
    python3 tools/gen_privacy.py <slug> [...]    # regenerate only these slugs
    python3 tools/gen_privacy.py --add slug "App Name" account,subscription,notifications
                                                 # append a new app then regenerate

Data flags (comma-separated, any of):
    account        app signs users in / stores data on a server (Supabase, Sign in with Apple)
    subscription   app sells a subscription or IAP (RevenueCat / StoreKit)
    notifications  app schedules local notifications / reminders
A local-only app with no purchases uses an empty flag set (write "-" or "local").
"""
import sys, os, csv, datetime, html as _html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "tools", "apps.tsv")
CONTACT = "coraliadigital@icloud.com"
STUDIO = "Coralia Digital"
EFFECTIVE = datetime.date.today().strftime("%-d %B %Y")

CSS = "/assets/legal.css"
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">')


def flag(flags, name):
    return name in flags


def data_sections(app, flags):
    out = []
    if flag(flags, "account"):
        out.append("<h3>Account data</h3><p>When you create an account or sign in with Apple, we receive your identifier and, if you share them, your name and email. We use this only to create and identify your account and sync your data across devices &mdash; never for marketing. Apple may relay or hide your real email; we work with whatever Apple provides.</p>")
        out.append("<h3>Your in-app content &amp; progress</h3><p>The data you create in %s (your entries, settings, results and progress) is stored on our servers, linked to your account, so it stays in sync across your devices.</p>" % app)
    else:
        out.append("<h3>On-device data only</h3><p>%s stores your content, settings and progress locally on your device using the operating system's standard storage. We do not have an account system and this data is never sent to us or to any server we control.</p>" % app)
    if flag(flags, "subscription"):
        out.append("<h3>Subscription data</h3><p>If you buy a subscription or in-app purchase, Apple and RevenueCat process the transaction and tell us whether your purchase is active. We never receive your card details.</p>")
    if flag(flags, "notifications"):
        out.append("<h3>Notifications</h3><p>If you enable reminders, the notifications are scheduled locally on your device. We do not run a push server and do not collect a device push token for this.</p>")
    return "".join(out)


def thirdparty_rows(flags):
    rows = []
    if flag(flags, "account"):
        rows.append(("Apple (Sign in with Apple, StoreKit)", "Authentication &amp; payments", "apple.com/legal/privacy"))
        rows.append(("Supabase", "Account &amp; content storage", "supabase.com/privacy"))
    elif flag(flags, "subscription"):
        rows.append(("Apple (StoreKit)", "Payments", "apple.com/legal/privacy"))
    if flag(flags, "subscription"):
        rows.append(("RevenueCat", "Subscription management", "revenuecat.com/privacy"))
    return rows


def page(slug, app, flags):
    app = _html.escape(app, quote=False)
    rows = thirdparty_rows(flags)
    if rows:
        tp = ("<h2>Third-party services</h2><table><thead><tr><th>Service</th><th>Purpose</th>"
              "<th>Their privacy policy</th></tr></thead><tbody>"
              + "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % r for r in rows)
              + "</tbody></table>")
    else:
        tp = ("<h2>Third-party services</h2><p>%s does not use any third-party analytics, "
              "advertising or data-collection SDKs.</p>" % app)

    if flag(flags, "account"):
        intro = ("<div class=\"callout\"><p>%s lets you sign in to sync your data across devices. "
                 "You stay in control: you can delete your account, and all the data attached to it, "
                 "from inside the app at any time.</p></div>" % app)
        choices = ("<p>You can delete your account at any time from within the app, which removes your "
                   "data from our servers. You can also email <a href=\"mailto:%s\">%s</a> with any "
                   "privacy request.</p>" % (CONTACT, CONTACT))
    else:
        intro = ("<div class=\"callout\"><p>%s works fully on your device. There is no account and no "
                 "sign-in, and your data never leaves your device through us.</p></div>" % app)
        choices = ("<p>Because your data lives on your device, deleting the app removes it. You can also "
                   "email <a href=\"mailto:%s\">%s</a> with any privacy question.</p>" % (CONTACT, CONTACT))

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{app} Privacy Policy &mdash; {studio}</title>
<meta name="description" content="Privacy policy for {app}.">
{fonts}
<link rel="stylesheet" href="{css}">
</head>
<body>
<nav><div class="wrap">
  <a class="brand" href="/index.html"><span class="dot"></span>{studio}</a>
  <ul class="navlinks">
    <li><a href="/index.html">Apps</a></li>
    <li><a href="mailto:{contact}">Contact</a></li>
  </ul>
</div></nav>
<section class="page"><div class="wrap">
  <p class="eyebrow">{app}</p>
  <h1>Privacy Policy</h1>
  <p class="meta">Effective {effective} &middot; {app} by {studio}</p>
  {intro}
  <h2>Who we are</h2>
  <p>{app} (&ldquo;the app&rdquo;) is published by {studio}, an independent app studio. &ldquo;We&rdquo; refers to the developer who publishes the app on the Apple App Store. Questions? Email <a href="mailto:{contact}">{contact}</a>.</p>
  <h2>What data we handle and why</h2>
  {sections}
  <h2>What we do <em>not</em> collect</h2>
  <ul><li>Location data</li><li>Contacts</li><li>Microphone audio</li><li>Health or fitness data</li><li>Browsing history</li><li>Advertising identifiers (IDFA)</li><li>Any data used for advertising or cross-app tracking</li></ul>
  <p>We do not sell your data to anyone, and we do not use it for advertising or cross-app tracking.</p>
  {thirdparty}
  <h2>Children</h2>
  <p>{app} is not directed at children under 13 and we do not knowingly collect personal information from them.</p>
  <h2>Your choices</h2>
  {choices}
  <h2>Changes to this policy</h2>
  <p>If we change this policy we will update the effective date above and post the new version on this page.</p>
  <p style="margin-top:2rem"><a class="back" href="/index.html">&larr; All {studio} apps</a></p>
</div></section>
<footer><div class="wrap">
  <p>&copy; {year} {studio}.</p>
  <p><a href="mailto:{contact}">{contact}</a> &nbsp;&middot;&nbsp; <a href="/index.html">All apps</a></p>
</div></footer>
</body>
</html>
""".format(app=app, studio=STUDIO, fonts=FONTS, css=CSS, contact=CONTACT,
           effective=EFFECTIVE, intro=intro, sections=data_sections(app, flags),
           thirdparty=tp, choices=choices, year=datetime.date.today().year)


def load_registry():
    apps = []
    with open(REGISTRY, newline="") as f:
        for row in csv.reader(f, delimiter="\t"):
            if not row or row[0].startswith("#"):
                continue
            slug = row[0].strip()
            name = row[1].strip() if len(row) > 1 else slug
            raw = row[2].strip().lower() if len(row) > 2 else ""
            flags = set() if raw in ("", "-", "local", "none") else {f.strip() for f in raw.split(",") if f.strip()}
            apps.append((slug, name, flags))
    return apps


def write_index(apps):
    items = "\n".join(
        '<li><a href="/%s/privacy.html">%s</a> &mdash; Privacy</li>' % (slug, _html.escape(name, quote=False))
        for slug, name, _ in apps)
    html = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{studio}</title>
<style>body{{font-family:-apple-system,system-ui,sans-serif;max-width:680px;margin:10vh auto;padding:0 1.5rem;color:#0d1126;line-height:1.7}}a{{color:#c2573a}}h1{{font-weight:600}}ul{{padding-left:1.1rem}}li{{margin:.3rem 0}}</style>
</head><body>
<h1>{studio}</h1>
<p>Independent app studio. App privacy &amp; legal pages:</p>
<ul>
<li><a href="/oddword/index.html">Oddword</a> &mdash; <a href="/oddword/privacy.html">Privacy</a> &middot; <a href="/oddword/support.html">Support</a></li>
{items}
</ul>
<p><a href="mailto:{contact}">{contact}</a></p>
</body></html>
""".format(studio=STUDIO, items=items, contact=CONTACT)
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(html)


def add_app(slug, name, flags):
    with open(REGISTRY, "a") as f:
        f.write("%s\t%s\t%s\n" % (slug, name, flags))


def main():
    args = sys.argv[1:]
    if args and args[0] == "--add":
        add_app(args[1], args[2], args[3] if len(args) > 3 else "-")
        args = []  # then regenerate everything
    apps = load_registry()
    only = set(args)
    for slug, name, flags in apps:
        if only and slug not in only:
            continue
        d = os.path.join(ROOT, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "privacy.html"), "w") as f:
            f.write(page(slug, name, flags))
        print("wrote %s/privacy.html  ->  https://katinkia.github.io/%s/privacy.html" % (slug, slug))
    write_index(apps)
    print("wrote index.html (%d apps listed)" % len(apps))


if __name__ == "__main__":
    main()
