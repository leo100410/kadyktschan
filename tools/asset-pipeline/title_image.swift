// Title picture for the main menu (user 2026-11-08): the user's own screenshot of the town at dusk, the black bar on
// top and the FPS read-out removed, larch and birch taiga painted into the fog.
// Run: swift tools/asset-pipeline/title_image.swift <project root>
// In:  assets/ui/title_source.jpg   Out: Content/Kadykchan/Data/UI/Title.png (staged with the Data folder)

import AppKit

let root = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : FileManager.default.currentDirectoryPath
let src = NSBitmapImageRep(data: try! Data(contentsOf: URL(fileURLWithPath: root + "/assets/ui/title_source.jpg")))!
var seed: UInt64 = 2003
func rnd() -> CGFloat { seed = seed &* 6364136223846793005 &+ 1442695040888963407; return CGFloat((seed >> 33) % 100000) / 100000.0 }
func rr(_ a: CGFloat, _ b: CGFloat) -> CGFloat { a + (b - a) * rnd() }

let W = 1280, H = 720
let top = 62                          // source rows dropped from the top: the black bar (~30 px) and empty sky
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: W, pixelsHigh: H, bitsPerSample: 8, samplesPerPixel: 4,
                           hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
let ctx = NSGraphicsContext.current!.cgContext
let srcH = CGFloat(src.pixelsHigh)
// source pixel rows top..top+H (AppKit y runs up: the source is drawn shifted down by its unused bottom rows)
ctx.draw(src.cgImage!, in: CGRect(x: 0, y: -(srcH - CGFloat(top) - CGFloat(H)), width: CGFloat(src.pixelsWide), height: srcH))

// FPS read-out (source x 1190..1250, y 183..215 from the top): cover it with the sky just left of it
let fy = CGFloat(H) - CGFloat(215 - top)
if let patch = src.cgImage!.cropping(to: CGRect(x: 1110, y: 180, width: 75, height: 40)) {
    ctx.draw(patch, in: CGRect(x: 1185, y: fy - 3, width: 75, height: 40))
    ctx.draw(patch, in: CGRect(x: 1215, y: fy - 3, width: 60, height: 40))
}

/// Fog colour at a height of the picture (sampled from the haze band of the source), mixed in by distance.
func fog(_ y: CGFloat) -> NSColor { NSColor(calibratedRed: 0.27, green: 0.28, blue: 0.29, alpha: 1) }

/// A larch: thin trunk, short drooping branch tiers getting wider down the stem, sparse crown.
func larch(_ x: CGFloat, _ base: CGFloat, _ h: CGFloat, _ dark: CGFloat, _ haze: CGFloat) {
    let col = NSColor(calibratedRed: 0.05 + haze * 0.22, green: 0.06 + haze * 0.22, blue: 0.05 + haze * 0.24, alpha: 0.96)
    col.setStroke(); col.setFill()
    let trunk = NSBezierPath(); trunk.move(to: NSPoint(x: x, y: base)); trunk.line(to: NSPoint(x: x + rr(-1, 1), y: base + h))
    trunk.lineWidth = max(1, h * 0.018); trunk.stroke()
    let tiers = Int(h / 5) + 6
    for t in 0..<tiers {
        let f = CGFloat(t) / CGFloat(tiers)
        let y = base + h * (0.18 + 0.8 * f)
        let reach = h * 0.2 * (1 - f) * rr(0.6, 1.2) + 1
        for side in [-1.0, 1.0] as [CGFloat] {
            if rnd() < 0.2 { continue }
            let p = NSBezierPath(); p.move(to: NSPoint(x: x, y: y))
            p.curve(to: NSPoint(x: x + side * reach, y: y - reach * 0.35), controlPoint1: NSPoint(x: x + side * reach * 0.4, y: y + reach * 0.1), controlPoint2: NSPoint(x: x + side * reach * 0.8, y: y - reach * 0.1))
            p.lineWidth = max(0.8, h * 0.012 * (1 - f) + 0.6); p.stroke()
            for _ in 0..<3 {                                                     // needle tufts along the branch
                let u = rr(0.3, 1.0)
                let r = max(1, h * 0.022 * (1 - f * 0.5))
                NSBezierPath(ovalIn: NSRect(x: x + side * reach * u - r, y: y - reach * 0.3 * u - r * 0.6, width: r * 2, height: r * 1.3)).fill()
            }
        }
    }
}

/// A birch or willow clump: a few pale stems and soft dark leaf masses.
func clump(_ x: CGFloat, _ base: CGFloat, _ h: CGFloat, _ haze: CGFloat) {
    for _ in 0..<3 {
        let sx = x + rr(-h * 0.15, h * 0.15)
        NSColor(calibratedWhite: 0.12 + haze * 0.15, alpha: 0.8).setStroke()
        let p = NSBezierPath(); p.move(to: NSPoint(x: sx, y: base)); p.line(to: NSPoint(x: sx + rr(-h * 0.08, h * 0.08), y: base + h * rr(0.6, 0.9)))
        p.lineWidth = max(1, h * 0.025); p.stroke()
    }
    for _ in 0..<Int(10 + h / 4) {
        let r = h * rr(0.1, 0.2)
        NSColor(calibratedRed: 0.035 + haze * 0.2, green: 0.045 + haze * 0.2, blue: 0.035 + haze * 0.22, alpha: rr(0.75, 0.95)).setFill()
        NSBezierPath(ovalIn: NSRect(x: x + rr(-h * 0.35, h * 0.35) - r, y: base + h * rr(0.35, 0.95) - r, width: r * 2, height: r * 1.6)).fill()
    }
}

// keep the blocks readable: no trees painted over the four building faces (picture coordinates, y up)
let blocks: [CGRect] = [CGRect(x: 110, y: 90, width: 160, height: 230), CGRect(x: 370, y: 230, width: 250, height: 140),
                        CGRect(x: 590, y: 120, width: 170, height: 150), CGRect(x: 950, y: 280, width: 280, height: 90)]
func free(_ x: CGFloat, _ y: CGFloat, _ h: CGFloat) -> Bool { !blocks.contains { $0.insetBy(dx: -10, dy: 0).contains(CGPoint(x: x, y: y + h * 0.5)) } }

// the taiga is already there in the haze; frame the view with dark larches at both edges and scrub in front, the way
// the hills look from the slope (only silhouettes: in this light nothing in the foreground has colour)
for _ in 0..<26 {
    let left = rnd() < 0.5
    let x = left ? rr(-30, 150) : rr(1120, 1310)
    larch(x, rr(-40, 40), rr(170, 330), 0, 0.0)
}
for _ in 0..<14 {                                                               // smaller ones further in, hazier
    let x = rnd() < 0.5 ? rr(150, 260) : rr(1010, 1130)
    larch(x, rr(40, 120), rr(60, 120), 0, 0.12)
}
// low scrub along the bottom edge: a ragged band of twigs and leaf specks, no rounded blobs
var hgt: CGFloat = 30
for xi in stride(from: 0, to: W, by: 2) {
    hgt = min(70, max(8, hgt + rr(-6, 6)))
    let x = CGFloat(xi)
    NSColor(calibratedRed: 0.03, green: 0.035, blue: 0.03, alpha: 0.95).setFill()
    NSRect(x: x, y: 0, width: 2, height: hgt * 0.55).fill()
    for _ in 0..<2 {
        let p = NSBezierPath(); p.move(to: NSPoint(x: x, y: hgt * 0.4))
        p.line(to: NSPoint(x: x + rr(-8, 8), y: hgt * rr(0.7, 1.15)))
        p.lineWidth = rr(0.6, 1.4); NSColor(calibratedRed: 0.04, green: 0.045, blue: 0.04, alpha: 0.9).setStroke(); p.stroke()
    }
    if rnd() < 0.6 {
        let r = rr(1.5, 3.5)
        NSColor(calibratedRed: 0.04, green: 0.05, blue: 0.035, alpha: 0.9).setFill()
        NSBezierPath(ovalIn: NSRect(x: x + rr(-6, 6), y: hgt * rr(0.5, 1.05), width: r * 2, height: r)).fill()
    }
}
NSGraphicsContext.restoreGraphicsState()

let dir = root + "/Content/Kadykchan/Data/UI"
try! FileManager.default.createDirectory(atPath: dir, withIntermediateDirectories: true)
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: dir + "/Title.png"))
print("title: \(dir)/Title.png")
