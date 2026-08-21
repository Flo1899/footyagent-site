/* TelemetryDeck Website — lokal, kein CDN, keine Cookies, keine persistenten IDs.
   Signale gehen in die iOS-App als website.* (Website-Apps indexieren nicht). */
(function () {
  var ENDPUNKT = 'https://nom.telemetrydeck.com/v2/';
  var APP_ID = '1E2AD82F-4537-416F-B603-5596DC45B0A8';
  var clientUser = Math.random().toString(36).slice(2) + Date.now().toString(36);
  var sessionID = clientUser;

  function sprache() {
    var wert = document.documentElement.getAttribute('data-lang');
    return wert === 'en' ? 'en' : 'de';
  }

  function nutzlast(typ) {
    var lang = sprache();
    var signal = {
      appID: APP_ID,
      clientUser: clientUser,
      sessionID: sessionID,
      type: typ,
      telemetryClientVersion: 'WebSDK-local',
      payload: {
        path: location.pathname,
        sprache: lang,
        url: location.href,
        referrer: document.referrer || ''
      }
    };
    if (
      /^localhost$|^127(\.\d+){0,2}\.\d+$|^\[::1?]$/.test(location.hostname) ||
      location.protocol === 'file:'
    ) {
      signal.isTestMode = true;
    }
    return [signal];
  }

  function sende(typ, beimVerlassen) {
    var json = JSON.stringify(nutzlast(typ));
    if (beimVerlassen) {
      if (navigator.sendBeacon) {
        try {
          var blob = new Blob([json], { type: 'application/json' });
          if (navigator.sendBeacon(ENDPUNKT, blob)) return;
        } catch (e) {}
      }
      fetch(ENDPUNKT, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: json,
        keepalive: true
      }).catch(function () {});
      return;
    }
    fetch(ENDPUNKT, {
      method: 'POST',
      mode: 'cors',
      headers: { 'Content-Type': 'application/json' },
      body: json
    }).catch(function () {});
  }

  sende('website.pageView', false);

  var store = document.querySelector('a.knopf.wenn-live');
  if (store) {
    store.addEventListener('click', function () {
      sende('website.store_click', true);
    });
  }
})();
