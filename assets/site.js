/* FootyAgent – Website-Skript (keine Abhängigkeiten, ~15 KB, gzip ~5 KB).
 *
 *  1. Akquise-Kanal: getAcquisitionChannel() normalisiert UTM-Parameter und Referrer
 *     (UTM hat Vorrang). Nichts wird im Browser gespeichert.
 *  2. App-Store-Knöpfe (a[data-cta]): Kampagnen-Link je Kanal setzen, Klick als
 *     »app_store_click« melden – genau einmal je Klick, egal wie viele Knöpfe die Seite hat.
 *  3. Weitere Ereignisse: language_changed, faq_opened, outbound_link_clicked.
 *  4. PostHog (EU, cookieless) wird NUR geladen, wenn die Seite einen Schlüssel trägt
 *     (product.json → analytics.posthogKey). Ohne Schlüssel geht keine einzige Anfrage raus.
 *  5. Sprachhinweis: bietet die andere Sprachfassung an, wenn die Browsersprache passt.
 *
 *  Konfiguration: <script id="fa-config" type="application/json"> (vom Generator _src/build.py).
 *  Testmodus: ?fa_debug=1 → Ereignisse in der Konsole und in window.FA.events.
 */
(function () {
  'use strict';

  var CFG = {};
  try { CFG = JSON.parse((document.getElementById('fa-config') || {}).textContent || '{}'); } catch (e) { CFG = {}; }
  var PAGE = CFG.page || {};
  var ANALYTICS = CFG.analytics || {};
  var APPSTORE = CFG.appStore || {};
  var DEBUG = /[?&]fa_debug=1(&|$)/.test(location.search);
  var URL_PARAMS = new URLSearchParams(location.search);
  var FA = window.FA = window.FA || {};
  FA.events = FA.events || [];

  // ---------------------------------------------------------------- Sprache (Speicher + alte Links)
  var LANG_KEY = 'fa_lang';   // seit August in Gebrauch: gemerkte Sprachwahl (vom Nutzer ausgelöst)
  function remember(lang) { try { localStorage.setItem(LANG_KEY, lang); } catch (e) {} }
  function remembered() { try { return localStorage.getItem(LANG_KEY); } catch (e) { return null; } }

  // Alte Links mit ?lang=de|en (bis Oktober 2026 schaltete die Startseite so um): sofort weiterleiten,
  // bevor irgendetwas gemessen wird. UTM-Parameter und Anker wandern mit, damit die Herkunft erhalten bleibt.
  var legacy = URL_PARAMS.get('lang');
  if (legacy && PAGE.alternates && PAGE.alternates[legacy] && legacy !== PAGE.lang) {
    remember(legacy);
    URL_PARAMS.delete('lang');
    var rest = URL_PARAMS.toString();
    location.replace(PAGE.alternates[legacy] + (rest ? '?' + rest : '') + location.hash);
    return;
  }

  // ---------------------------------------------------------------- Akquise-Kanal
  // Ergebnisse: chatgpt, ai_other, google_organic, bing_organic, other_search, reddit,
  // youtube, tiktok, instagram, x, other_social, paid, other_referral, direct, internal, unknown
  var AI_CHATGPT = ['chatgpt.com', 'chat.openai.com', 'openai.com'];
  var AI_OTHER = ['perplexity.ai', 'claude.ai', 'gemini.google.com', 'bard.google.com',
    'copilot.microsoft.com', 'copilot.cloud.microsoft', 'm365.cloud.microsoft', 'you.com', 'phind.com',
    'deepseek.com', 'chat.deepseek.com', 'grok.com', 'x.ai', 'meta.ai', 'mistral.ai', 'chat.mistral.ai',
    'poe.com', 'duck.ai', 'felo.ai', 'chat.qwen.ai', 'kimi.com', 'kimi.ai', 'manus.im', 'character.ai'];
  var UTM_AI_CHATGPT = ['chatgpt.com', 'chatgpt', 'chat.openai.com', 'openai'];
  var UTM_AI_OTHER = ['perplexity', 'perplexity.ai', 'claude', 'claude.ai', 'anthropic', 'gemini',
    'gemini.google.com', 'copilot', 'copilot.microsoft.com', 'bing_chat', 'you.com', 'phind', 'deepseek',
    'grok', 'meta.ai', 'mistral', 'poe', 'duck.ai'];
  var SOCIAL = [
    ['reddit', ['reddit.com', 'redd.it']],
    ['youtube', ['youtube.com', 'youtu.be']],
    ['tiktok', ['tiktok.com']],
    ['instagram', ['instagram.com']],
    ['x', ['x.com', 'twitter.com', 't.co']],
    ['other_social', ['facebook.com', 'fb.me', 'threads.net', 'threads.com', 'bsky.app', 'linkedin.com',
      'lnkd.in', 'discord.com', 'discord.gg', 't.me', 'telegram.org', 'whatsapp.com', 'mastodon.social']]
  ];
  var OTHER_SEARCH = ['duckduckgo.com', 'search.yahoo.com', 'yahoo.com', 'ecosia.org', 'search.brave.com',
    'yandex.ru', 'yandex.com', 'baidu.com', 'startpage.com', 'qwant.com', 'naver.com', 'seznam.cz'];
  var PAID_MEDIUM = ['cpc', 'ppc', 'paid', 'paidsocial', 'paid_social', 'paid-social', 'display', 'ads', 'cpm'];

  function hostOf(url) {
    try { return new URL(url).hostname.toLowerCase().replace(/^www\./, ''); } catch (e) { return ''; }
  }
  function matches(host, list) {
    for (var i = 0; i < list.length; i++) {
      if (host === list[i] || host.slice(-(list[i].length + 1)) === '.' + list[i]) return true;
    }
    return false;
  }
  function isGoogle(host) { return /(^|\.)google\.[a-z]{2,3}(\.[a-z]{2})?$/.test(host); }

  function fromHost(host) {
    if (matches(host, AI_CHATGPT)) return 'chatgpt';
    if (matches(host, AI_OTHER)) return 'ai_other';
    if (isGoogle(host)) return 'google_organic';
    if (matches(host, ['bing.com'])) return 'bing_organic';
    if (matches(host, OTHER_SEARCH)) return 'other_search';
    for (var i = 0; i < SOCIAL.length; i++) if (matches(host, SOCIAL[i][1])) return SOCIAL[i][0];
    return 'other_referral';
  }

  function fromUtm(source, medium) {
    var s = (source || '').toLowerCase().replace(/^www\./, '');
    var m = (medium || '').toLowerCase();
    if (PAID_MEDIUM.indexOf(m) >= 0) return 'paid';
    if (UTM_AI_CHATGPT.indexOf(s) >= 0) return 'chatgpt';
    if (UTM_AI_OTHER.indexOf(s) >= 0) return 'ai_other';
    if (s === 'google') return 'google_organic';
    if (s === 'bing') return 'bing_organic';
    if (s === 'twitter') return 'x';
    if (s.indexOf('.') > 0) return fromHost(s);           // z. B. utm_source=reddit.com
    for (var i = 0; i < SOCIAL.length; i++) if (SOCIAL[i][0] === s) return s;
    return 'other_referral';
  }

  /** Reine Funktion (testbar): Kanal aus Seiten-URL und Referrer. UTM schlägt Referrer. */
  function getAcquisitionChannel(pageUrl, referrer, ownHost) {
    var params;
    try { params = new URL(pageUrl).searchParams; } catch (e) { params = new URLSearchParams(''); }
    var utmSource = params.get('utm_source');
    if (utmSource) return fromUtm(utmSource, params.get('utm_medium'));
    if (!referrer) return 'direct';
    var host = hostOf(referrer);
    if (!host) return 'unknown';
    var own = (ownHost || '').toLowerCase().replace(/^www\./, '');
    if (own && host === own) return 'internal';
    return fromHost(host);
  }
  FA.getAcquisitionChannel = getAcquisitionChannel;

  var CHANNEL = getAcquisitionChannel(location.href, document.referrer, location.hostname);
  var IS_ENTRY = CHANNEL !== 'internal';
  FA.channel = CHANNEL;

  // ---------------------------------------------------------------- Analytics
  var queue = [];
  var phReady = false;

  function baseProps() {
    return {
      acquisition_channel: CHANNEL,
      is_entry_page: IS_ENTRY,
      page_language: PAGE.lang || document.documentElement.lang || '',
      page_type: PAGE.type || '',
      site_build: CFG.build || ''
    };
  }
  function merge(a, b) { var o = {}, k; for (k in a) o[k] = a[k]; for (k in b) o[k] = b[k]; return o; }

  /** Zentrale Meldefunktion – alle Ereignisse laufen hier durch. */
  function track(name, props, options) {
    var p = merge(baseProps(), props || {});
    if (DEBUG) { FA.events.push({ event: name, properties: p }); console.info('[FA]', name, p); }
    if (!ANALYTICS.key) return;
    if (phReady && window.posthog) window.posthog.capture(name, p, options || {});
    else queue.push([name, p, options || {}]);
  }
  FA.track = track;

  function loadPostHog() {
    if (!ANALYTICS.key || window.posthog && window.posthog.__loaded) return;
    // Offizieller PostHog-Einbaucode (posthog.com/docs/libraries/js), unverändert.
    /* eslint-disable */
    !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],Object.defineProperty(u,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}}),Object.defineProperty(u.people,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(){return u.toString(1)+".people (stub)"}}),o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagResult isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
    /* eslint-enable */
    window.posthog.init(ANALYTICS.key, {
      api_host: ANALYTICS.host,
      ui_host: ANALYTICS.uiHost,
      defaults: ANALYTICS.defaults,
      cookieless_mode: ANALYTICS.cookieless || 'always', // keine Cookies, kein local/sessionStorage
      person_profiles: 'identified_only',                // es wird nie identify() aufgerufen
      capture_pageview: true,
      capture_pageleave: true,                           // Verweildauer, Absprung, Scrolltiefe
      autocapture: false,                                // nur bewusst definierte Ereignisse
      capture_dead_clicks: false,
      rageclick: false,
      disable_session_recording: true,
      disable_surveys: true,
      advanced_disable_flags: true,                      // keine Feature-Flag-Abfragen
      before_send: function (event) {                   // Seitenkontext an JEDES Ereignis
        if (event && event.properties) {
          var b = baseProps();
          for (var k in b) if (!(k in event.properties)) event.properties[k] = b[k];
        }
        return event;
      },
      loaded: function (ph) { if (DEBUG) ph.debug(); }
    });
    phReady = true;
    for (var i = 0; i < queue.length; i++) window.posthog.capture(queue[i][0], queue[i][1], queue[i][2]);
    queue = [];
  }

  function whenIdle(fn) {
    var run = function () { ('requestIdleCallback' in window) ? requestIdleCallback(fn, { timeout: 1500 }) : setTimeout(fn, 200); };
    if (document.readyState === 'complete') run(); else window.addEventListener('load', run);
  }
  whenIdle(loadPostHog);

  // ---------------------------------------------------------------- App-Store-Knöpfe
  function campaignFor(channel) {
    var c = APPSTORE.campaigns || {};
    return c[channel] || c['default'] || 'website';
  }
  function appStoreUrl(channel) {
    var base = APPSTORE.baseUrl || 'https://apps.apple.com/app/apple-store/id6790972595';
    var ct = campaignFor(channel);
    return base + '?pt=' + encodeURIComponent(APPSTORE.providerToken || '') +
      '&ct=' + encodeURIComponent(ct) + '&mt=8';
  }
  FA.appStoreUrl = appStoreUrl;

  var ctaLinks = document.querySelectorAll('a[data-cta]');
  var targetUrl = appStoreUrl(CHANNEL);
  for (var i = 0; i < ctaLinks.length; i++) ctaLinks[i].setAttribute('href', targetUrl);

  var lastTracked = { el: null, t: 0 };
  function onCta(ev, link) {
    var now = Date.now();
    if (lastTracked.el === link && now - lastTracked.t < 800) return;   // Doppelauslösung (click + auxclick)
    lastTracked = { el: link, t: now };
    track('app_store_click', {
      page: location.pathname,
      landing_page: IS_ENTRY ? location.pathname : null,   // bei Folgeseiten: $entry_pathname der Sitzung
      referrer: document.referrer || null,
      utm_source: URL_PARAMS.get('utm_source'),
      utm_medium: URL_PARAMS.get('utm_medium'),
      utm_campaign: URL_PARAMS.get('utm_campaign'),
      language: PAGE.lang || '',
      cta_position: link.getAttribute('data-cta') || 'unknown',
      destination: link.getAttribute('href'),
      campaign_token: campaignFor(CHANNEL)
    }, { transport: 'sendBeacon', send_instantly: true });
  }

  // ---------------------------------------------------------------- Sprachhinweis
  function suggestLanguage() {
    var alt = PAGE.alternates || {};
    var other = PAGE.lang === 'de' ? 'en' : 'de';
    if (!alt[other]) return;
    var pref = remembered();
    if (pref === PAGE.lang) return;                      // bewusst diese Sprache gewählt
    var browser = ((navigator.languages && navigator.languages[0]) || navigator.language || '').toLowerCase();
    var wants = pref || (browser.indexOf('de') === 0 ? 'de' : (browser ? 'en' : ''));
    if (wants !== other) return;
    var bar = document.getElementById('sprachhinweis');
    if (!bar) return;
    bar.hidden = false;
    var close = bar.querySelector('button');
    if (close) close.addEventListener('click', function () { bar.hidden = true; remember(PAGE.lang); });
  }

  // ---------------------------------------------------------------- Klicks (ein Listener für alles)
  function handle(ev) {
    if (ev.type === 'auxclick' && ev.button !== 1) return;
    var a = ev.target && ev.target.closest ? ev.target.closest('a') : null;
    if (!a) return;
    if (a.hasAttribute('data-cta')) { onCta(ev, a); return; }
    if (a.hasAttribute('data-setlang')) {
      var to = a.getAttribute('data-setlang');
      remember(to);
      track('language_changed', { from: PAGE.lang, to: to, page: location.pathname }, { transport: 'sendBeacon', send_instantly: true });
      return;
    }
    var href = a.getAttribute('href') || '';
    if (/^https?:\/\//i.test(href) && hostOf(href) !== location.hostname.replace(/^www\./, '')) {
      track('outbound_link_clicked', {
        destination: href, destination_host: hostOf(href), page: location.pathname,
        link_location: a.closest('footer') ? 'footer' : (a.closest('header') ? 'header' : 'body')
      }, { transport: 'sendBeacon', send_instantly: true });
    }
  }
  document.addEventListener('click', handle);
  document.addEventListener('auxclick', handle);

  // FAQ: <details data-faq="id"> – nur das Öffnen zählt
  var faqs = document.querySelectorAll('details[data-faq]');
  for (var f = 0; f < faqs.length; f++) {
    faqs[f].addEventListener('toggle', function (ev) {
      var d = ev.currentTarget;
      if (d.open) track('faq_opened', { question_id: d.getAttribute('data-faq'), page: location.pathname });
    });
  }

  suggestLanguage();
})();
