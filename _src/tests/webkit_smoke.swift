// Safari-Engine-Test (WebKit, nur macOS): lädt jede Seite wie Safari und prüft im echten DOM:
// keine JS-Fehler, Kanal-Erkennung, Kampagnen-Links, app_store_click genau einmal, FAQ-Ereignis.
//   python3 -m http.server 8765 &          (im Repo-Ordner)
//   swift _src/tests/webkit_smoke.swift http://127.0.0.1:8765
import AppKit
import WebKit

let base = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "http://127.0.0.1:8765"
let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
let sitemap = (try? String(contentsOf: root.appendingPathComponent("sitemap.xml"), encoding: .utf8)) ?? ""
var paths = sitemap.components(separatedBy: "<loc>").dropFirst()
    .compactMap { $0.components(separatedBy: "</loc>").first?.replacingOccurrences(of: "https://footyagent.app", with: "") }
paths.append("/404.html")

// Fehler schon ab Seitenstart einsammeln
let fehlerFalle = """
window.__fehler = [];
window.addEventListener('error', e => window.__fehler.push(String(e.message)));
const ce = console.error; console.error = function () { window.__fehler.push([...arguments].join(' ')); ce.apply(console, arguments); };
"""
// Nach dem Laden: Knöpfe prüfen, zweimal klicken (Navigation unterbinden), FAQ öffnen
let pruefung = """
(() => {
  const r = { fa: typeof window.FA === 'object', channel: window.FA && FA.channel };
  const ctas = [...document.querySelectorAll('a[data-cta]')];
  r.ctas = ctas.length;
  r.hrefsAI = ctas.length > 0 && ctas.every(a => a.href.includes('ct=website_ai') && a.href.includes('pt=129172457'));
  window.addEventListener('click', e => e.preventDefault());
  if (ctas[0]) { ctas[0].click(); ctas[0].click(); }          // Doppelklick = 1 Ereignis
  if (ctas.length > 1) ctas[ctas.length - 1].click();          // anderer Knopf = sofort eins mehr
  const clicks = (window.FA ? FA.events : []).filter(e => e.event === 'app_store_click');
  r.clicks = clicks.length;
  r.pos = clicks.map(e => e.properties.cta_position).join(',');
  r.fields = clicks[0] ? ['page','landing_page','acquisition_channel','referrer','utm_source','utm_medium','utm_campaign','language','cta_position','destination'].every(k => k in clicks[0].properties) : null;
  const d = document.querySelector('details[data-faq]');
  r.faq = !!d; if (d) d.open = true;
  r.h1 = document.querySelectorAll('h1').length;
  r.lang = document.documentElement.lang;
  return JSON.stringify(r);
})()
"""
let nachFaq = "JSON.stringify({faqEvents: (window.FA ? FA.events : []).filter(e => e.event === 'faq_opened').length, fehler: window.__fehler})"

final class Lauf: NSObject, WKNavigationDelegate {
    let web: WKWebView
    var rest: [String]
    var fehlerGesamt = 0
    var weiter: (() -> Void)?

    init(paths: [String]) {
        let cfg = WKWebViewConfiguration()
        cfg.userContentController.addUserScript(WKUserScript(source: fehlerFalle, injectionTime: .atDocumentStart, forMainFrameOnly: true))
        web = WKWebView(frame: NSRect(x: 0, y: 0, width: 390, height: 844), configuration: cfg)
        web.customUserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
        rest = paths
        super.init()
        web.navigationDelegate = self
    }

    func naechste() {
        guard let p = rest.first else {
            print(fehlerGesamt == 0 ? "\nWebKit: alle Seiten OK" : "\nWebKit: \(fehlerGesamt) Fehler")
            exit(fehlerGesamt == 0 ? 0 : 1)
        }
        let sep = p.contains("?") ? "&" : "?"
        web.load(URLRequest(url: URL(string: base + p + sep + "utm_source=chatgpt.com&fa_debug=1")!))
    }

    func webView(_ w: WKWebView, decidePolicyFor a: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        decisionHandler(a.request.url?.host == URL(string: base)?.host ? .allow : .cancel)   // nie zum App Store
    }

    func webView(_ w: WKWebView, didFinish _: WKNavigation!) {
        let p = rest.removeFirst()
        w.evaluateJavaScript(pruefung) { r1, e1 in
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {      // toggle-Ereignis kommt asynchron
                w.evaluateJavaScript(nachFaq) { r2, e2 in
                    let a = (try? JSONSerialization.jsonObject(with: Data(((r1 as? String) ?? "{}").utf8))) as? [String: Any] ?? [:]
                    let b = (try? JSONSerialization.jsonObject(with: Data(((r2 as? String) ?? "{}").utf8))) as? [String: Any] ?? [:]
                    var probleme: [String] = []
                    if let e = e1 ?? e2 { probleme.append("JS: \(e.localizedDescription)") }
                    let ohneSkript = p == "/datenschutz/"                       // von Hand gepflegt, ohne Messung
                    if !ohneSkript && a["fa"] as? Bool != true { probleme.append("site.js nicht aktiv") }
                    if !ohneSkript && a["channel"] as? String != "chatgpt" { probleme.append("Kanal \(a["channel"] ?? "nil")") }
                    if let f = b["fehler"] as? [String], !f.isEmpty { probleme.append("Konsole: \(f.joined(separator: " | "))") }
                    if a["h1"] as? Int != 1 { probleme.append("\(a["h1"] ?? 0) × h1") }
                    let ctas = a["ctas"] as? Int ?? 0
                    if !ohneSkript {
                        if ctas == 0 { probleme.append("kein CTA") }
                        if a["hrefsAI"] as? Bool != true { probleme.append("CTA ohne website_ai-Kampagne") }
                        let soll = ctas > 1 ? 2 : 1
                        if a["clicks"] as? Int != soll { probleme.append("app_store_click × \(a["clicks"] ?? 0) statt \(soll)") }
                        if a["fields"] as? Bool != true { probleme.append("Pflichtfelder fehlen") }
                    }
                    if a["faq"] as? Bool == true && b["faqEvents"] as? Int != 1 { probleme.append("faq_opened × \(b["faqEvents"] ?? 0)") }
                    self.fehlerGesamt += probleme.count
                    let pos = (a["pos"] as? String).map { $0.isEmpty ? "" : " [\($0)]" } ?? ""
                    print(probleme.isEmpty ? "✓ \(p)\(pos)" : "✗ \(p): \(probleme.joined(separator: "; "))")
                    self.naechste()
                }
            }
        }
    }

    func webView(_ w: WKWebView, didFail _: WKNavigation!, withError e: Error) { print("✗ Laden: \(e)"); exit(1) }
    func webView(_ w: WKWebView, didFailProvisionalNavigation _: WKNavigation!, withError e: Error) { print("✗ Laden: \(e)"); exit(1) }
}

let app = NSApplication.shared
let lauf = Lauf(paths: Array(paths))
lauf.naechste()
DispatchQueue.main.asyncAfter(deadline: .now() + 120) { print("Zeitüberschreitung"); exit(1) }
app.run()
