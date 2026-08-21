/* TelemetryDeck Website — lokal, kein CDN, keine Cookies, keine localStorage-IDs.
   App-ID nur in diesem Skript; nicht ins Chat kopieren. */
(function () {
  var ENDPUNKT = 'https://nom.telemetrydeck.com/v2/w/';
  var APP_ID = 'B5DB1118-B4E8-44C5-B4AF-D6808810B80A';

  function sprache() {
    var wert = document.documentElement.getAttribute('data-lang');
    return wert === 'en' ? 'en' : 'de';
  }

  function nutzlast(typ) {
    var lang = sprache();
    var body = {
      appID: APP_ID,
      type: typ,
      url: location.href,
      referrer: document.referrer,
      telemetryClientVersion: 'WebSDK 1.1.0',
      path: location.pathname,
      sprache: lang,
      lang: lang
    };
    if (
      /^localhost$|^127(\.\d+){0,2}\.\d+$|^\[::1?]$/.test(location.hostname) ||
      location.protocol === 'file:'
    ) {
      body.isTestMode = true;
    }
    return body;
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

  sende('pageView', false);

  var store = document.querySelector('a.knopf.wenn-live');
  if (store) {
    store.addEventListener('click', function () {
      sende('store_click', true);
    });
  }
})();
