# Fairway Fantasy League

Fantasy golf league site: snake draft, weekly lineups (best 4 of 6 count), FAAB waivers, trades,
playoffs, MVP race, history — with **live ESPN scores that refresh every 30 seconds** in the browser.

## How it runs
- **Site:** GitHub Pages serves `index.html` from this repository.
- **Sign-in + data:** Firebase (Google sign-in + Firestore). `config.js` holds the public web config;
  `firestore.rules` controls who can change what. The first person to sign in becomes the commissioner.
- **Live scores / field / tee times:** pulled from ESPN's public scoreboard by each open browser and saved
  to the league about once a minute.
- **World rankings:** `.github/workflows/owgr.yml` refreshes `owgr.json` nightly.

## One-time Firebase setup
1. Create a Firebase project, enable **Authentication → Google**, add `<username>.github.io` to authorized domains.
2. Create a **Firestore** database (production mode) and paste `firestore.rules` into **Firestore → Rules → Publish**.
3. Register a web app and paste its config into `config.js` as `window.FIREBASE_CONFIG = {...}`.
4. Sign in on the site (you become commissioner), then **LM Tools → Import league data** with the export file.
