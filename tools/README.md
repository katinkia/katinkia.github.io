# Privacy-page generator

Hosts a live privacy-policy URL for every Coralia Digital app on this GitHub Pages site:
`https://katinkia.github.io/<slug>/privacy.html` — the URL you paste into App Store Connect.

`apps.tsv` is the source of truth. Each row is `slug <TAB> Display Name <TAB> data-flags`.
Data flags (comma-separated): `account`, `subscription`, `notifications`, or `-` for a
local-only app with no purchases. Flags must match what the app actually does — they decide
which sections (accounts, subscriptions, reminders, third-party services) appear in the policy.

## Add a new app
```sh
python3 tools/gen_privacy.py --add <slug> "Display Name" account,subscription,notifications
git add -A && git commit -m "privacy: <slug>" && git push
```

## Regenerate
```sh
python3 tools/gen_privacy.py            # all apps + index.html
python3 tools/gen_privacy.py <slug>     # one app
```

After pushing, GitHub Pages goes live in ~1 minute. Open the URL in a browser before
submitting to App Store Connect. Contact email on every policy is `coraliadigital@icloud.com`.
Shared styling lives in `/assets/legal.css`.
