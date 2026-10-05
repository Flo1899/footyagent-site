// Rendert eine Seite per WebKit (Safari-Engine) in ein PNG – für das Link-Vorschaubild und für Seitenbilder.
// Aufruf: swift _src/og/render.swift <url> <ausgabe.png> [breite=1200] [höhe=630 | full]
//   Link-Vorschaubild: swift _src/og/render.swift http://127.0.0.1:8765/_src/og/og.html /tmp/og.png
//   ganze Seite:       swift _src/og/render.swift http://127.0.0.1:8765/ /tmp/start.png 1280 full
import AppKit
import WebKit

let args = CommandLine.arguments
guard args.count >= 3, let url = URL(string: args[1]) else { print("Aufruf: render.swift <url> <ausgabe.png> [breite] [höhe|full]"); exit(2) }
let ausgabe = URL(fileURLWithPath: args[2])
let breite = args.count > 3 ? Double(args[3]) ?? 1200 : 1200
let ganz = args.count > 4 && args[4] == "full"
let hoehe = args.count > 4 && !ganz ? Double(args[4]) ?? 630 : (ganz ? 900 : 630)

let app = NSApplication.shared
let fenster = NSWindow(contentRect: NSRect(x: -10000, y: 0, width: breite, height: hoehe),   // unsichtbar außerhalb
                       styleMask: [.borderless], backing: .buffered, defer: false)
let web = WKWebView(frame: NSRect(x: 0, y: 0, width: breite, height: hoehe))
fenster.contentView = web
fenster.orderBack(nil)

func foto(_ w: WKWebView, _ h: Double) {
    let cfg = WKSnapshotConfiguration()
    cfg.rect = NSRect(x: 0, y: 0, width: breite, height: h)
    w.takeSnapshot(with: cfg) { bild, fehler in
        guard let bild, let tiff = bild.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
              let png = rep.representation(using: .png, properties: [:]) else {
            print("Fehler: \(String(describing: fehler))"); exit(1)
        }
        do { try png.write(to: ausgabe); print("ok \(rep.pixelsWide)x\(rep.pixelsHigh)"); exit(0) }
        catch { print("Schreibfehler: \(error)"); exit(1) }
    }
}

final class Fertig: NSObject, WKNavigationDelegate {
    func webView(_ w: WKWebView, didFinish _: WKNavigation!) {
        guard ganz else {
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { foto(w, hoehe) }   // Bilder fertig laden lassen
            return
        }
        w.evaluateJavaScript("document.documentElement.scrollHeight") { wert, _ in
            let h = (wert as? Double) ?? hoehe
            fenster.setContentSize(NSSize(width: breite, height: h))
            w.frame = NSRect(x: 0, y: 0, width: breite, height: h)
            DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) { foto(w, h) }        // Lazy-Bilder nachladen lassen
        }
    }
    func webView(_ w: WKWebView, didFail _: WKNavigation!, withError e: Error) { print("Ladefehler: \(e)"); exit(1) }
}

let d = Fertig()
web.navigationDelegate = d
web.load(URLRequest(url: url))
DispatchQueue.main.asyncAfter(deadline: .now() + 40) { print("Zeitüberschreitung"); exit(1) }
app.run()
