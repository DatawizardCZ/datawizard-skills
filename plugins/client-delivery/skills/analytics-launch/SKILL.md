---
name: analytics-launch
description: Checklist pro napojení měření na web klienta před spuštěním Google Ads (GTM, GA4, Consent Mode v2, konverze form_submit a click_phone, propojení Ads s GA4, Search Console) a pro agenturní strukturu účtů (Ads MCC, GA4 Account, GTM Account). Použij při zakládání trackingu pro klienta, věšení klienta pod MCC nebo propojování Ads a GA4.
---

# Analytics Launch Checklist (obecná šablona)

Znovupoužitelný checklist pro napojení měření na nový web **před** spuštěním Google Ads. Stack-agnostický, s poznámkami pro Astro.

**Cíl:** každý lead z reklamy měřitelný a přiřaditelný ke kampani, ještě než se pustí první koruna.

---

## Fáze -1 · Agenturní struktura (jednorázově, ne per klient)

Zastřešující účty pod jedním agenturním Google účtem (owner). Zakládá se **jednou**, pak se pod ně věší klienti. Kolegům dáváš přístup centrálně tady, ne per klientský účet.

- [ ] **Google Ads Manager Account (MCC)**: [ads.google.com](https://ads.google.com) → „Vytvořit účet správce“. Sjednocující účet pro klienty, pod něj linkuješ klientské Ads účty. Poznamenat **Manager Customer ID**.
- [ ] **GA4 Account** (ne property!): jeden agenturní Account, v něm per klient jedna **property**. Struktura: `Account (agentura) → Property (klient A), Property (klient B)…`.
- [ ] **GTM Account**: jeden agenturní Account, v něm per klient jeden **kontejner**. Struktura: `Account (agentura) → Container (klient A), Container (klient B)…`.
- [ ] Přidat kolegy jako uživatele na úrovni **Manager / Account** (ne per klient), přístup se dědí dolů.

> **MCC ≠ GA4 Account ≠ GTM Account.** Tři různé „manager“ vrstvy, každá ve své službě, všechny pod stejným agenturním Google účtem. Konkrétní účty a ID agentury drž v interních poznámkách mimo git.

---

## Fáze 0 · Kód webu (dřív než účty)

Připrav web tak, aby stačilo vyplnit jedno env ID a všechno naskočí:

- [ ] **GTM loader v layoutu**, aktivovaný env proměnnou (`PUBLIC_GTM_ID`). Prázdné ID = žádný tracking (čisté do launche).
- [ ] **Consent Mode v2 defaults** (`analytics_storage`, `ad_storage`, `ad_user_data`, `ad_personalization` = `denied`) inline v `<head>`, **před** GTM loaderem. V EU povinné.
- [ ] **Cookie banner** posílá `gtag('consent','update', {...granted})` na souhlas. Vlastní implementace je čistší než SaaS; Consent Mode řešíme v kódu, GTM Consent Init trigger proto netřeba.
- [ ] **`form_submit` dataLayer push** po úspěšném odeslání formuláře (jen na reálný success). Parametry: `form_location`, zdroj, kategorie/produkt a `user_data` (email+telefon) pro budoucí Enhanced Conversions.
- [ ] **`click_phone`**: telefony jako `<a href="tel:...">`. Žádný kód navíc, řeší GTM trigger na Click URL `tel:`.
- [ ] **JSON-LD** Organization + LocalBusiness (SEO + GBP).
- [ ] **Sitemap** (`@astrojs/sitemap` + `site:` v configu → `/sitemap-index.xml`) pro Search Console.

> Astro: loader + consent do `src/layouts/BaseLayout.astro`, push do form komponenty.

---

## Fáze 1 · Klientské účty (pod agenturní strukturou z Fáze -1)

- [ ] **Google Ads účet klienta**: založit **z MCC** (Účty → +) nebo založit zvlášť a nalinkovat pod MCC. Expertní režim, přeskočit tvorbu kampaně. Země, časové pásmo, měna. Výsledek: **Customer ID** `123-456-7890`.
- [ ] **GA4 property**: v agenturním GA4 Accountu → Create property. URL, časové pásmo, měna. Výsledek: **Measurement ID** `G-XXXXXXXXXX` + account ID (pro Ads import).
- [ ] **GTM kontejner** typu Web v agenturním GTM Accountu. Výsledek: **Container ID** `GTM-XXXXXXX`.

> IDčka a přístupy ukládej do projektové složky mimo repo. Nikdy ne do gitu.

---

## Fáze 2 · Nasazení + konverze

- [ ] Vyplnit `PUBLIC_GTM_ID` v hosting env (Netlify), re-deploy.
- [ ] Ověřit `gtm.js?id=...` HTTP 200 na homepage **i podstránkách**.
- [ ] Ověřit Consent Mode v Tag Assistant: `default (denied)` před GTM, `update (granted)` po souhlasu.
- [ ] **GA4 Configuration tag** (Značka Google, All Pages) jako base pro GA4 i Ads.
- [ ] GTM triggery + GA4 Event tagy pro `form_submit` a `click_phone` (+ `dlv -` proměnné na parametry).
- [ ] Test v Preview → **Publikovat** → JSON export kontejneru jako backup.
- [ ] Ověřit eventy v **GA4 DebugView**.

---

## Fáze 3 · Propojení Ads ↔ GA4 (pokrývá 75–85 % atribuce)

- [ ] GA4 → propojit s Google Ads (Customer ID), auto-tagging ON.
- [ ] Označit `form_submit` + `click_phone` jako **klíčové události**.
- [ ] Google Ads → Importovat konverze z GA4 → obě jako **primární**.

---

## Fáze 4 · Volitelné / vyžaduje klienta

- [ ] **Call tracking** (forwarding number, 30 s min.): klient musí odsouhlasit přesměrovací číslo na displeji. IP klienta do exclusion listu.
- [ ] **Enhanced Conversions for Leads**: odložit, až kampaň běží měsíc a víc (posledních ~15–25 % atribuce). `user_data` push už je základ.
- [ ] **Google Business Profile**: ověřený GBP → location asset v Ads.

---

## Fáze 5 · Search Console (organika, nezávislé na Ads)

- [ ] Ověřit doménu v GSC (typ „Doména“, DNS TXT pokrývá subdomény; nebo `google-site-verification` meta tag).
- [ ] Submitnout sitemapu (`/sitemap-index.xml`).
- [ ] Propojit GSC ↔ GA4 (organic dotazy v GA4).
- [ ] Po pár dnech: Coverage/Pages + Core Web Vitals.

---

## Fáze 6 · Finální ověření funnelu

- [ ] `?gclid=test` v URL → landing page.
- [ ] Odeslat formulář → potvrzení → `form_submit` v DebugView.
- [ ] Klik na telefon → `click_phone` v DebugView.
- [ ] Google Ads → Konverze: zápis (až 24 h).
- [ ] Backup GTM kontejneru.

---

## Pravidla / lekce

- **Consent Mode v kódu, ne v GTM šabloně.** Defaults musí běžet dřív než GTM, inline skript to zaručí čistěji než GTM Consent Init trigger.
- **`form_submit` jen na reálný success**, ne na chybu odeslání, jinak nafouknutá konverze.
- **Ads onboarding blokuje UI**, dokud nemáš první kampaň. Obchází se klikáním X přes „Vytvořte první kampaň“.
- **Enhanced Conversions je optimalizace, ne blocker.** Nespouštět kampaň kvůli ní. Krok „import z GA4“ řeší většinu atribuce.
- **IDčka nikdy do repa**, vždy do projektové složky mimo git.
- **Přesun účtů mezi MCC hlídej:** po přesunu se může rozbít link Ads ↔ GA4 a import konverzí. Re-linkovat + re-import konverzí.
