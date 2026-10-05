// Prüft assets/site.js mit der echten Seitenkonfiguration – ohne Browser, ohne Abhängigkeiten.
//   node _src/tests/test_channel.mjs
// Abgedeckt: Kanal-Erkennung (channel_cases.json), Kampagnen-Link je Kanal, app_store_click genau
// einmal je Klick samt Pflichtfeldern, cta_position, Weiterleitung alter ?lang-Links mit UTM.
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const SITE_JS = readFileSync(path.join(ROOT, 'assets/site.js'), 'utf8');
const CASES = JSON.parse(readFileSync(path.join(HERE, 'channel_cases.json'), 'utf8'));

function configOf(file) {
  const html = readFileSync(path.join(ROOT, file), 'utf8');
  const m = html.match(/<script id="fa-config" type="application\/json">([\s\S]*?)<\/script>/);
  if (!m) throw new Error(`fa-config fehlt in ${file}`);
  return m[1];
}

function fakeLink(attrs, inside = 'main') {
  return {
    attrs: { ...attrs },
    hasAttribute(n) { return n in this.attrs; },
    getAttribute(n) { return n in this.attrs ? this.attrs[n] : null; },
    setAttribute(n, v) { this.attrs[n] = String(v); },
    closest(sel) { return sel === 'a' ? this : (sel === inside ? {} : null); },
  };
}

/** Führt site.js einmal aus, wie ein Browser beim Seitenaufruf. */
function load({ url, referrer = '', file = 'index.html', links = [], clock = { now: 1_000_000 } }) {
  const u = new URL(url);
  const replaced = [];
  const listeners = {};
  const sandbox = {
    document: {
      referrer, readyState: 'loading', documentElement: { lang: '' },
      getElementById: (id) => (id === 'fa-config' ? { textContent: configOf(file) } : null),
      querySelectorAll: (sel) => (sel === 'a[data-cta]' ? links : []),
      addEventListener: (type, fn) => { (listeners[type] ||= []).push(fn); },
    },
    location: { href: u.href, search: u.search, hostname: u.hostname, pathname: u.pathname, hash: u.hash,
      replace: (to) => replaced.push(to) },
    navigator: { languages: ['en-US'], language: 'en-US' },
    localStorage: { getItem: () => null, setItem: () => {} },
    console: { info: () => {}, log: () => {}, warn: () => {} },
    URL, URLSearchParams, setTimeout: () => 0,
    Date: { now: () => clock.now },
    addEventListener: () => {},
  };
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(SITE_JS, sandbox);
  const fire = (type, target, button = 0) => (listeners[type] || []).forEach((fn) => fn({ type, button, target }));
  return { FA: sandbox.FA, replaced, fire, clock };
}

let failed = 0, passed = 0;
function check(name, ok, detail = '') {
  if (ok) { passed++; } else { failed++; console.error(`✗ ${name}${detail ? ' – ' + detail : ''}`); }
}

// 1) Kanal-Erkennung
const { FA } = load({ url: 'https://footyagent.app/' });
for (const c of CASES) {
  const got = FA.getAcquisitionChannel(c.url, c.referrer, 'footyagent.app');
  check(`Kanal: ${c.name}`, got === c.expect, `erwartet ${c.expect}, bekommen ${got}`);
}

// 2) Kampagnen-Link je Kanal (aus der echten Konfiguration)
const cfg = JSON.parse(configOf('index.html')).appStore;
for (const ch of ['chatgpt', 'ai_other', 'google_organic', 'direct', 'unknown', 'reddit']) {
  const want = cfg.campaigns[ch] || cfg.campaigns.default;
  const got = FA.appStoreUrl(ch);
  check(`Kampagne ${ch} → ct=${want}`, got.includes(`ct=${want}`) && got.includes(`pt=${cfg.providerToken}`) && got.includes('id6790972595'), got);
}

// 3) app_store_click: genau einmal je Klick, korrekte Felder
{
  const hero = fakeLink({ 'data-cta': 'hero', href: 'x' });
  const header = fakeLink({ 'data-cta': 'header', href: 'x' }, 'header');
  const run = load({ url: 'https://footyagent.app/?utm_source=chatgpt.com&utm_medium=referral&fa_debug=1', referrer: '', links: [hero, header] });
  const clicks = () => run.FA.events.filter((e) => e.event === 'app_store_click');
  check('Knopf-Link auf Kanal-Kampagne umgestellt', hero.getAttribute('href').includes(`ct=${cfg.campaigns.chatgpt || cfg.campaigns.default}`), hero.getAttribute('href'));

  run.fire('click', hero);
  check('Ein Klick = ein Ereignis', clicks().length === 1, `bekommen ${clicks().length}`);
  run.fire('click', hero);                         // Doppelklick (gleiche Millisekunde)
  run.fire('auxclick', hero, 1);                   // Mittelklick direkt danach
  check('Doppelklick/Mittelklick innerhalb 800 ms zählt nicht doppelt', clicks().length === 1, `bekommen ${clicks().length}`);
  run.fire('auxclick', hero, 2);                   // Rechtsklick
  check('Rechtsklick zählt nicht', clicks().length === 1);
  run.clock.now += 1200;
  run.fire('click', hero);
  check('Erneuter Klick nach 1,2 s zählt', clicks().length === 2, `bekommen ${clicks().length}`);
  run.fire('click', header);
  check('Anderer Knopf zählt sofort', clicks().length === 3);

  const p = clicks()[0].properties;
  const need = ['page', 'landing_page', 'acquisition_channel', 'referrer', 'utm_source', 'utm_medium', 'utm_campaign',
    'language', 'cta_position', 'destination'];
  for (const k of need) check(`Pflichtfeld ${k} vorhanden`, k in p);
  check('acquisition_channel = chatgpt', p.acquisition_channel === 'chatgpt', p.acquisition_channel);
  check('cta_position = hero', p.cta_position === 'hero', p.cta_position);
  check('cta_position = header', clicks()[2].properties.cta_position === 'header');
  check('landing_page = Einstiegsseite', p.landing_page === '/', String(p.landing_page));
  check('utm_source übernommen', p.utm_source === 'chatgpt.com');
  check('language = en', p.language === 'en', p.language);
  check('destination = Kampagnen-Link', p.destination.startsWith('https://apps.apple.com/') && p.destination.includes('ct='), p.destination);
}

// 4) Folgeseite: interner Referrer → kein falscher Einstieg
{
  const btn = fakeLink({ 'data-cta': 'feature_page', href: 'x' });
  const run = load({ url: 'https://footyagent.app/faq/?fa_debug=1', referrer: 'https://footyagent.app/', file: 'faq/index.html', links: [btn] });
  run.fire('click', btn);
  const p = run.FA.events.find((e) => e.event === 'app_store_click').properties;
  check('Folgeseite: Kanal internal', p.acquisition_channel === 'internal', p.acquisition_channel);
  check('Folgeseite: landing_page leer (Sitzungs-Einstieg kommt aus PostHog)', p.landing_page === null);
  check('Folgeseite: is_entry_page false', p.is_entry_page === false);
}

// 5) Sprachwechsel und externe Links
{
  const lang = fakeLink({ 'data-setlang': 'de', href: '/de/' }, 'header');
  const ext = fakeLink({ href: 'https://www.tiktok.com/@footyagent.app' }, 'footer');
  const run = load({ url: 'https://footyagent.app/?fa_debug=1' });
  run.fire('click', lang);
  run.fire('click', ext);
  const names = run.FA.events.map((e) => e.event);
  check('language_changed gemeldet', names.includes('language_changed'), names.join(','));
  const out = run.FA.events.find((e) => e.event === 'outbound_link_clicked');
  check('outbound_link_clicked mit link_location footer', out && out.properties.link_location === 'footer');
  check('Ohne fa_debug keine Ereignisliste', load({ url: 'https://footyagent.app/' }).FA.events.length === 0);
}

// 6) Alte ?lang-Links: sofort weiter, UTM bleibt, nichts gemessen
{
  const run = load({ url: 'https://footyagent.app/?lang=de&utm_source=reddit&fa_debug=1#faq' });
  check('?lang=de leitet auf /de/ weiter', run.replaced.length === 1 && run.replaced[0].startsWith('/de/'), run.replaced.join(' '));
  check('UTM bleibt bei Weiterleitung erhalten', /utm_source=reddit/.test(run.replaced[0] || ''), run.replaced[0]);
  check('Anker bleibt erhalten', (run.replaced[0] || '').endsWith('#faq'));
  check('Keine Messung vor der Weiterleitung', run.FA.channel === undefined);
  const same = load({ url: 'https://footyagent.app/?lang=en' });
  check('?lang=en auf englischer Seite: keine Weiterleitung', same.replaced.length === 0);
}

console.log(`${passed} bestanden, ${failed} fehlgeschlagen`);
process.exit(failed ? 1 : 0);
