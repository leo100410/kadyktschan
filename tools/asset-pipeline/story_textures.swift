// Story props as real pictures (user 2026-11-08: "mache da einen echten Kalender hin ... ein richtiges Bild ... bei den
// Schlüsseln auch"): calendars, the brigade photo, letters, notes, log books, the adit plan, the key board labels.
// Drawn with AppKit (Cyrillic fonts of macOS), written to assets/textures/T_Pic_<Name>_D.png.
// Run: swift tools/asset-pipeline/story_textures.swift <project root>
// Every person, text and date is FIKTION (design/narrative/story-places.md); photos are drawn, not real people.

import AppKit
import CoreImage

let root = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : FileManager.default.currentDirectoryPath
let out = root + "/assets/textures/"
var seed: UInt64 = 1979
func rnd() -> CGFloat { seed = seed &* 6364136223846793005 &+ 1442695040888963407; return CGFloat((seed >> 33) % 100000) / 100000.0 }
func rr(_ a: CGFloat, _ b: CGFloat) -> CGFloat { a + (b - a) * rnd() }

func font(_ name: String, _ size: CGFloat) -> NSFont { NSFont(name: name, size: size) ?? NSFont.systemFont(ofSize: size) }
let ink = NSColor(calibratedRed: 0.13, green: 0.16, blue: 0.42, alpha: 0.92)        // ballpoint blue
let pencil = NSColor(calibratedWhite: 0.25, alpha: 0.85)
let redInk = NSColor(calibratedRed: 0.72, green: 0.1, blue: 0.08, alpha: 0.9)
let print_ = NSColor(calibratedWhite: 0.1, alpha: 0.95)

/// Canvas of w x h pixels; y runs up (AppKit). Saved as PNG.
func canvas(_ w: Int, _ h: Int, _ name: String, _ draw: (CGFloat, CGFloat) -> Void) {
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8, samplesPerPixel: 4,
                               hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
    draw(CGFloat(w), CGFloat(h))
    NSGraphicsContext.restoreGraphicsState()
    try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: out + "T_Pic_\(name)_D.png"))
    print("T_Pic_\(name)_D.png")
}

/// Aged paper: base tone, fibres, foxing spots, a darker edge.
func paper(_ w: CGFloat, _ h: CGFloat, _ base: NSColor, stains: Int = 12) {
    base.setFill(); NSRect(x: 0, y: 0, width: w, height: h).fill()
    for _ in 0..<Int(w * h / 900) {
        NSColor(calibratedWhite: rnd() < 0.5 ? 0.0 : 1.0, alpha: rr(0.02, 0.06)).setFill()
        NSRect(x: rr(0, w), y: rr(0, h), width: rr(1, 3), height: rr(1, 3)).fill()
    }
    for _ in 0..<stains {
        let r = rr(6, 40)
        NSColor(calibratedRed: 0.55, green: 0.4, blue: 0.2, alpha: rr(0.04, 0.12)).setFill()
        NSBezierPath(ovalIn: NSRect(x: rr(0, w), y: rr(0, h), width: r, height: r * rr(0.6, 1.2))).fill()
    }
    let edge = NSBezierPath(rect: NSRect(x: 0, y: 0, width: w, height: h))
    edge.lineWidth = w * 0.03
    NSColor(calibratedRed: 0.45, green: 0.35, blue: 0.2, alpha: 0.18).setStroke(); edge.stroke()
}

/// Text at (x, y) = top-left of the first line; hand = slight per-line tilt and wobble like handwriting.
@discardableResult
func text(_ s: String, _ x: CGFloat, _ y: CGFloat, _ f: NSFont, _ c: NSColor, hand: Bool = false, lineGap: CGFloat = 1.25) -> CGFloat {
    var yy = y
    for line in s.components(separatedBy: "\n") {
        let attr: [NSAttributedString.Key: Any] = [.font: f, .foregroundColor: c]
        NSGraphicsContext.saveGraphicsState()
        let t = NSAffineTransform()
        t.translateX(by: x + (hand ? rr(-4, 4) : 0), yBy: yy - f.pointSize)
        if hand { t.rotate(byDegrees: rr(-1.6, 1.2)) }
        t.concat()
        (line as NSString).draw(at: .zero, withAttributes: attr)
        NSGraphicsContext.restoreGraphicsState()
        yy -= f.pointSize * lineGap
    }
    return yy
}

func line(_ x0: CGFloat, _ y0: CGFloat, _ x1: CGFloat, _ y1: CGFloat, _ c: NSColor, _ wd: CGFloat) {
    let p = NSBezierPath(); p.move(to: NSPoint(x: x0, y: y0)); p.line(to: NSPoint(x: x1, y: y1))
    p.lineWidth = wd; p.lineCapStyle = .round; c.setStroke(); p.stroke()
}

/// Hand-drawn loop around a point (circled calendar day).
func circleMark(_ cx: CGFloat, _ cy: CGFloat, _ r: CGFloat, _ c: NSColor) {
    let p = NSBezierPath()
    for k in 0...40 {
        let a = CGFloat(k) / 36 * 2 * .pi + 0.3
        let rad = r * (1 + 0.08 * sin(CGFloat(k) * 1.7))
        let pt = NSPoint(x: cx + cos(a) * rad * 1.25, y: cy + sin(a) * rad)
        k == 0 ? p.move(to: pt) : p.line(to: pt)
    }
    p.lineWidth = 3.5; c.setStroke(); p.stroke()
}

/// One month as a Soviet calendar grid (weeks start on Monday, Sunday in red); returns the cell centres by day.
func month(_ title: String, x: CGFloat, top: CGFloat, w: CGFloat, firstWeekday: Int, days: Int, size: CGFloat) -> [Int: NSPoint] {
    text(title, x, top, font("PTSans-Bold", size * 1.15), print_)
    let names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    let cw = w / 7, rowH = size * 1.55
    var cells: [Int: NSPoint] = [:]
    for (k, n) in names.enumerated() {
        text(n, x + CGFloat(k) * cw + cw * 0.2, top - size * 1.6, font("PTSans-Regular", size * 0.7), k == 6 ? redInk : pencil)
    }
    for d in 1...days {
        let slot = firstWeekday + d - 1
        let col = slot % 7, row = slot / 7
        let px = x + CGFloat(col) * cw + cw * 0.18, py = top - size * 2.6 - CGFloat(row) * rowH
        text(String(d), px, py, font("PTSans-Bold", size), col == 6 ? redInk : print_)
        cells[d] = NSPoint(x: px + size * 0.45, y: py - size * 0.55)
    }
    return cells
}

/// A person for the drawn photos: jacket, collar, face with shading, optional miner's helmet with lamp.
func person(_ cx0: CGFloat, _ base0: CGFloat, _ s0: CGFloat, helmet: Bool, tone: CGFloat) {
    // every man a little different: height, build, a slight lean, moustache, stripes on the work jacket
    let s = s0 * rr(0.92, 1.08), base = base0 + rr(-6, 6), cx = cx0 + rr(-8, 8)
    let wide = rr(0.9, 1.15)
    let jacket = NSColor(calibratedWhite: 0.16 + tone * 0.12, alpha: 1)
    NSGraphicsContext.saveGraphicsState()
    let lean = NSAffineTransform(); lean.translateX(by: cx, yBy: base); lean.rotate(byDegrees: rr(-3, 3)); lean.scaleX(by: wide, yBy: 1); lean.translateX(by: -cx, yBy: -base); lean.concat()
    defer { NSGraphicsContext.restoreGraphicsState() }
    let body = NSBezierPath()
    body.move(to: NSPoint(x: cx - s * 0.62, y: base)); body.line(to: NSPoint(x: cx - s * 0.5, y: base + s * 1.15))
    body.curve(to: NSPoint(x: cx + s * 0.5, y: base + s * 1.15), controlPoint1: NSPoint(x: cx - s * 0.3, y: base + s * 1.32), controlPoint2: NSPoint(x: cx + s * 0.3, y: base + s * 1.32))
    body.line(to: NSPoint(x: cx + s * 0.62, y: base)); body.close()
    jacket.setFill(); body.fill()
    if rnd() < 0.5 {                                                                           // reflective stripes
        NSColor(calibratedWhite: 0.7, alpha: 0.8).setFill()
        NSRect(x: cx - s * 0.58, y: base + s * 0.45, width: s * 1.16, height: s * 0.06).fill()
    }
    NSColor(calibratedWhite: 0.08, alpha: 0.6).setFill()                                      // lapels / opening
    NSRect(x: cx - s * 0.03, y: base, width: s * 0.06, height: s * 1.05).fill()
    NSColor(calibratedWhite: 0.55, alpha: 1).setFill()                                       // collar
    NSBezierPath(ovalIn: NSRect(x: cx - s * 0.16, y: base + s * 1.08, width: s * 0.32, height: s * 0.2)).fill()
    let face = NSRect(x: cx - s * 0.2, y: base + s * 1.18, width: s * 0.4, height: s * 0.5)
    NSColor(calibratedWhite: 0.62 + tone * 0.1, alpha: 1).setFill(); NSBezierPath(ovalIn: face).fill()
    NSColor(calibratedWhite: 0.0, alpha: 0.28).setFill()                                      // shadow side of the face
    NSBezierPath(ovalIn: NSRect(x: cx, y: base + s * 1.2, width: s * 0.2, height: s * 0.44)).fill()
    NSColor(calibratedWhite: 0.6 + tone * 0.1, alpha: 1).setFill()                          // ears
    for ex in [-0.23, 0.18] as [CGFloat] { NSBezierPath(ovalIn: NSRect(x: cx + s * ex, y: base + s * 1.38, width: s * 0.06, height: s * 0.12)).fill() }
    NSColor(calibratedWhite: 0.1, alpha: 0.55).setFill()                                      // brows, eye shadows, nose shadow
    for ex in [-0.1, 0.04] as [CGFloat] {
        NSBezierPath(ovalIn: NSRect(x: cx + s * ex, y: base + s * 1.46, width: s * 0.07, height: s * 0.04)).fill()
        NSRect(x: cx + s * ex - s * 0.01, y: base + s * 1.52, width: s * 0.09, height: s * 0.02).fill()
    }
    NSRect(x: cx + s * 0.005, y: base + s * 1.36, width: s * 0.025, height: s * 0.09).fill()
    if rnd() < 0.55 {
        NSBezierPath(ovalIn: NSRect(x: cx - s * 0.08, y: base + s * 1.29, width: s * 0.16, height: s * 0.05)).fill()   // moustache
    } else {
        NSRect(x: cx - s * 0.05, y: base + s * 1.3, width: s * 0.1, height: s * 0.014).fill()
    }
    if helmet {
        NSColor(calibratedWhite: 0.78, alpha: 1).setFill()
        let dome = NSBezierPath(); dome.appendArc(withCenter: NSPoint(x: cx, y: base + s * 1.6), radius: s * 0.27, startAngle: 0, endAngle: 180); dome.close(); dome.fill()
        NSRect(x: cx - s * 0.32, y: base + s * 1.57, width: s * 0.64, height: s * 0.05).fill()
        NSColor(calibratedWhite: 0.95, alpha: 1).setFill()
        NSBezierPath(ovalIn: NSRect(x: cx - s * 0.07, y: base + s * 1.67, width: s * 0.14, height: s * 0.1)).fill()
    } else {
        NSColor(calibratedWhite: 0.12, alpha: 1).setFill()
        NSBezierPath(ovalIn: NSRect(x: cx - s * 0.21, y: base + s * 1.5, width: s * 0.42, height: s * 0.24)).fill()
    }
}

/// Photographic softness: blur what is drawn so far (the drawn people read as a photo, not as shapes).
func soften(_ radius: Double) {
    guard let ctx = NSGraphicsContext.current?.cgContext, let img = ctx.makeImage() else { return }
    let ci = CIImage(cgImage: img)
    let f = CIFilter(name: "CIGaussianBlur")!
    f.setValue(ci.clampedToExtent(), forKey: kCIInputImageKey)
    f.setValue(radius, forKey: kCIInputRadiusKey)
    let out = f.outputImage!.cropped(to: ci.extent)
    if let cg = CIContext().createCGImage(out, from: ci.extent) {
        ctx.draw(cg, in: CGRect(x: 0, y: 0, width: img.width, height: img.height))
    }
}

/// Old print: sepia tone over the grey drawing, grain, scratches, vignette, white border.
func agePhoto(_ w: CGFloat, _ h: CGFloat, border: CGFloat, sepia: Bool = true) {
    if sepia {
        NSColor(calibratedRed: 0.62, green: 0.45, blue: 0.25, alpha: 0.38).setFill()
        NSRect(x: 0, y: 0, width: w, height: h).fill(using: .multiply)
    }
    for _ in 0..<Int(w * h / 60) {
        NSColor(calibratedWhite: rnd() < 0.5 ? 0 : 1, alpha: rr(0.03, 0.09)).setFill()
        NSRect(x: rr(0, w), y: rr(0, h), width: 1.5, height: 1.5).fill()
    }
    for _ in 0..<7 { line(rr(0, w), rr(0, h), rr(0, w), rr(0, h), NSColor(calibratedWhite: 1, alpha: 0.18), 1) }
    let g = NSGradient(starting: NSColor(calibratedWhite: 0, alpha: 0), ending: NSColor(calibratedWhite: 0, alpha: 0.45))!
    g.draw(in: NSBezierPath(rect: NSRect(x: 0, y: 0, width: w, height: h)), relativeCenterPosition: .zero)
    NSColor(calibratedRed: 0.9, green: 0.87, blue: 0.78, alpha: 1).setFill()
    for r in [NSRect(x: 0, y: 0, width: w, height: border), NSRect(x: 0, y: h - border, width: w, height: border),
              NSRect(x: 0, y: 0, width: border, height: h), NSRect(x: w - border, y: 0, width: border, height: h)] { r.fill() }
}

let paperTone = NSColor(calibratedRed: 0.86, green: 0.82, blue: 0.70, alpha: 1)
let bookTone = NSColor(calibratedRed: 0.88, green: 0.85, blue: 0.75, alpha: 1)

// --- Antonina's calendar, Jan-Mar 2004: "уголь" (coal) on Petja's days, then "Пети нет" from 28 March
canvas(768, 1024, "CalendarAntonina") { w, h in
    paper(w, h, NSColor(calibratedRed: 0.93, green: 0.91, blue: 0.84, alpha: 1))
    NSColor(calibratedRed: 0.62, green: 0.12, blue: 0.1, alpha: 1).setFill(); NSRect(x: 0, y: h - 110, width: w, height: 110).fill()
    text("2004", w / 2 - 80, h - 18, font("PTSans-Bold", 72), NSColor(calibratedWhite: 0.97, alpha: 1))
    let months: [(String, Int, Int)] = [("ЯНВАРЬ", 3, 31), ("ФЕВРАЛЬ", 6, 29), ("МАРТ", 0, 31)]
    var top = h - 140
    for (k, (name, first, days)) in months.enumerated() {
        let cells = month(name, x: 40, top: top, w: w - 80, firstWeekday: first, days: days, size: 23)
        let coal = k == 0 ? [3, 6, 10, 13, 17, 20, 24, 27, 31] : (k == 1 ? [3, 7, 10, 14, 17, 21, 24, 28] : [2, 6, 9, 13, 16, 20, 23, 27])
        for d in coal { if let c = cells[d] { text("уголь", c.x - 22, c.y - 6, font("Georgia-Italic", 13), redInk, hand: true) } }
        if k == 2 {
            for d in [28, 29, 30, 31] { if let c = cells[d] { text("Пети нет", c.x - 34, c.y - 4, font("Georgia-Italic", 14), ink, hand: true) } }
        }
        top -= 270
    }
    text("Петя не пришёл. Вода замёрзла.\nВ печке последние дрова.", 50, 70, font("Georgia-Italic", 24), ink, hand: true)
}

// --- Gorbunov kitchen calendar, October 2003: picture on top, the 10th circled, "автобус 7:40 - Валя и Лида"
canvas(768, 1024, "CalendarGorbunov") { w, h in
    paper(w, h, NSColor(calibratedRed: 0.94, green: 0.92, blue: 0.86, alpha: 1))
    // the month's picture: autumn hills over the town (colour print, faded)
    NSColor(calibratedRed: 0.55, green: 0.66, blue: 0.75, alpha: 1).setFill(); NSRect(x: 40, y: h - 470, width: w - 80, height: 430).fill()
    for (k, col) in [NSColor(calibratedRed: 0.62, green: 0.52, blue: 0.3, alpha: 1), NSColor(calibratedRed: 0.42, green: 0.45, blue: 0.25, alpha: 1)].enumerated() {
        let p = NSBezierPath(); p.move(to: NSPoint(x: 40, y: h - 470))
        for i in 0...20 { p.line(to: NSPoint(x: 40 + CGFloat(i) * (w - 80) / 20, y: h - 300 - CGFloat(k) * 70 + 40 * sin(CGFloat(i) * 0.6 + CGFloat(k)))) }
        p.line(to: NSPoint(x: w - 40, y: h - 470)); p.close(); col.setFill(); p.fill()
    }
    for i in 0..<5 { NSColor(calibratedWhite: 0.85, alpha: 1).setFill(); NSRect(x: 120 + CGFloat(i) * 110, y: h - 450, width: 70, height: 60 + CGFloat(i % 2) * 25).fill() }
    text("Колыма. Осень.", 60, h - 60, font("PTSerif-Italic", 26), NSColor(calibratedWhite: 1, alpha: 0.9))
    let cells = month("ОКТЯБРЬ 2003", x: 50, top: h - 500, w: w - 100, firstWeekday: 2, days: 31, size: 30)
    for d in 1...9 { if let c = cells[d] { line(c.x - 18, c.y - 14, c.x + 22, c.y + 18, pencil, 2.5) } }
    if let c = cells[10] {
        circleMark(c.x, c.y, 26, redInk)
        line(c.x, c.y - 30, 330, 150, redInk, 2.5)
        text("автобус 7:40 — Валя и Лида", 60, 140, font("Georgia-Italic", 30), redInk, hand: true)
    }
}

// --- Brigade photo: twelve men in helmets before the adit portal, Pjotr circled in pen on the print
canvas(1024, 768, "Brigade") { w, h in
    NSColor(calibratedWhite: 0.62, alpha: 1).setFill(); NSRect(x: 0, y: 0, width: w, height: h).fill()
    NSColor(calibratedWhite: 0.48, alpha: 1).setFill()                                       // hillside
    let hill = NSBezierPath(); hill.move(to: NSPoint(x: 0, y: h * 0.55)); hill.curve(to: NSPoint(x: w, y: h * 0.7), controlPoint1: NSPoint(x: w * 0.3, y: h * 0.8), controlPoint2: NSPoint(x: w * 0.7, y: h * 0.62))
    hill.line(to: NSPoint(x: w, y: 0)); hill.line(to: NSPoint(x: 0, y: 0)); hill.close(); hill.fill()
    NSColor(calibratedWhite: 0.72, alpha: 1).setFill(); NSRect(x: w * 0.32, y: h * 0.3, width: w * 0.36, height: h * 0.36).fill()   // portal
    NSColor(calibratedWhite: 0.08, alpha: 1).setFill()
    let mouth = NSBezierPath(); mouth.appendArc(withCenter: NSPoint(x: w * 0.5, y: h * 0.44), radius: w * 0.09, startAngle: 0, endAngle: 180); mouth.line(to: NSPoint(x: w * 0.41, y: h * 0.3)); mouth.line(to: NSPoint(x: w * 0.59, y: h * 0.3)); mouth.close(); mouth.fill()
    text("ШТОЛЬНЯ №3", w * 0.41, h * 0.64, font("PTSans-Bold", 28), NSColor(calibratedWhite: 0.25, alpha: 1))
    let s: CGFloat = 92
    for k in 0..<6 { person(w * 0.14 + CGFloat(k) * w * 0.145, h * 0.26, s, helmet: true, tone: rr(0, 1)) }     // back row
    for k in 0..<6 { person(w * 0.08 + CGFloat(k) * w * 0.165, h * 0.06, s * 1.1, helmet: k != 2, tone: rr(0, 1)) }  // front row
    soften(2.2)
    agePhoto(w, h, border: 28)
    circleMark(w * 0.08 + 2 * w * 0.165, h * 0.06 + s * 1.1 * 1.45, 40, ink)
    line(w * 0.08 + 2 * w * 0.165 + 40, h * 0.06 + s * 1.1 * 1.75, w * 0.08 + 2 * w * 0.165 + 70, h * 0.06 + s * 1.1 * 2.4, ink, 3)
    text("Петя", w * 0.08 + 2 * w * 0.165 + 60, h * 0.06 + s * 1.1 * 2.75, font("Georgia-Italic", 32), ink, hand: true)
    text("Бригада Орлова. Штольня №3, июль 1999", 60, 26, font("Georgia-Italic", 20), ink, hand: true)
}

// --- Key board labels: six hooks, each with a paper label; the fifth is the adit gate
canvas(1024, 384, "KeyBoard") { w, h in
    NSColor(calibratedRed: 0.42, green: 0.27, blue: 0.15, alpha: 1).setFill(); NSRect(x: 0, y: 0, width: w, height: h).fill()
    for _ in 0..<160 { line(0, rr(0, h), w, rr(0, h), NSColor(calibratedRed: 0.25, green: 0.15, blue: 0.08, alpha: rr(0.1, 0.3)), rr(1, 3)) }
    let labels = ["подвал", "сарай", "гараж", "контора", "штольня 3\nворота", "почта"]
    for (k, l) in labels.enumerated() {
        let x = 30 + CGFloat(k) * (w - 60) / 6
        paperTone.setFill(); NSRect(x: x, y: 40, width: (w - 60) / 6 - 18, height: 110).fill()
        text(l, x + 10, 128, font("Georgia-Italic", k == 4 ? 21 : 26), k == 4 ? redInk : ink, hand: true, lineGap: 1.1)
        NSColor(calibratedWhite: 0.0, alpha: 0.35).setFill()                                  // where the hook is screwed in
        NSBezierPath(ovalIn: NSRect(x: x + 60, y: 250, width: 22, height: 22)).fill()
    }
    NSColor(calibratedWhite: 0.0, alpha: 0.25).setFill()                                      // clean outline of the missing key
    NSBezierPath(roundedRect: NSRect(x: 30 + 4 * (w - 60) / 6 + 52, y: 158, width: 40, height: 90), xRadius: 14, yRadius: 14).fill()
}

// --- Antonina's note to Petja
canvas(512, 384, "NoteAntonina") { w, h in
    paper(w, h, NSColor(calibratedRed: 0.9, green: 0.88, blue: 0.8, alpha: 1), stains: 5)
    for k in 0..<9 { line(0, h - 50 - CGFloat(k) * 38, w, h - 50 - CGFloat(k) * 38, NSColor(calibratedRed: 0.4, green: 0.5, blue: 0.75, alpha: 0.35), 1.2) }
    text("Петя, спасибо за уголь.\nХрани тебя Бог.\nЕсли увидишь Орлова —\nпусть заберёт меня отсюда.\n                       А. Ф.", 30, h - 26, font("Georgia-Italic", 30), ink, hand: true, lineGap: 1.27)
}

// --- torn shift-book page: the last shift, the board left in the drift, the brigade's addresses
canvas(768, 1024, "ShiftPage") { w, h in
    paper(w, h, bookTone)
    for k in 0..<26 { line(30, h - 120 - CGFloat(k) * 34, w - 20, h - 120 - CGFloat(k) * 34, NSColor(calibratedRed: 0.4, green: 0.5, blue: 0.7, alpha: 0.3), 1) }
    line(110, 0, 110, h, NSColor(calibratedRed: 0.8, green: 0.3, blue: 0.3, alpha: 0.4), 1.5)
    text("ЖУРНАЛ СМЕН   ·   ШТОЛЬНЯ №3", 40, h - 40, font("CourierNewPS-BoldMT", 30), print_)
    text("15.11.2001  Последняя смена.\nШтольня закрыта приказом.\nДоска почёта осталась в штреке, 42 м.\nВорота опечатать. Ключ у меня.\n                         — Орлов", 125, h - 108, font("Georgia-Italic", 27), ink, hand: true)
    var y = text("Адреса бригады:", 125, h - 420, font("Georgia-Italic", 27), ink, hand: true)
    for (k, a) in ["Сухов В. — Мира 2, кв. 7", "Горбунов П. — дом без номера\n      у Ленина, кв. 1", "Ли С. — Ленина 9, кв. 12", "Каримов Р. — уехал в Магадан"].enumerated() {
        let yy = text(a, 125, y, font("Georgia-Italic", 26), ink, hand: true)
        if k == 1 { line(125, yy + 30, 520, yy + 34, redInk, 3) }
        y = yy
    }
    NSColor(calibratedRed: 0.2, green: 0.15, blue: 0.1, alpha: 1).setFill()                   // torn left edge
    let tear = NSBezierPath(); tear.move(to: NSPoint(x: 0, y: 0))
    for k in 0...40 { tear.line(to: NSPoint(x: rr(0, 16), y: CGFloat(k) * h / 40)) }
    tear.line(to: NSPoint(x: 0, y: h)); tear.close(); tear.fill()
}

// --- Pjotr's letter to Walja, never sent
canvas(768, 1024, "LetterGorbunov") { w, h in
    paper(w, h, NSColor(calibratedRed: 0.92, green: 0.9, blue: 0.84, alpha: 1))
    for k in 0..<28 { line(0, h - 70 - CGFloat(k) * 34, w, h - 70 - CGFloat(k) * 34, NSColor(calibratedRed: 0.35, green: 0.45, blue: 0.7, alpha: 0.3), 1) }
    text("Валя, родная!\n\nЯ не могу уехать. В нашем доме\nостались старики — Антонина,\nСухов, бабка с третьего.\nЕсли котёл встанет, они замёрзнут.\nАдминистрация отрезала свет,\nа я держу котёл на дровах.\n\nВесной приеду. Поцелуй Лиду.\nСкажи ей — папа не упрямый,\nпапа дежурный.\n\n                          Твой Петя\n                          ноябрь 2003", 40, h - 44, font("Georgia-Italic", 28), ink, hand: true, lineGap: 1.21)
}

// --- the administration's order: heating off on 1 November 2003, everyone out
canvas(768, 1024, "Order") { w, h in
    paper(w, h, NSColor(calibratedRed: 0.9, green: 0.89, blue: 0.85, alpha: 1), stains: 6)
    text("АДМИНИСТРАЦИЯ\nСУСУМАНСКОГО РАЙОНА", 60, h - 50, font("CourierNewPS-BoldMT", 30), print_)
    text("ПРЕДПИСАНИЕ", w / 2 - 130, h - 190, font("CourierNewPS-BoldMT", 40), print_)
    text("Жителям пос. Кадыкчан\n\nВ связи с ликвидацией посёлка\nтеплоснабжение и электроснабжение\nбудут прекращены 01.11.2003.\n\nВсем жителям надлежит выехать\nдо 31.10.2003. Транспорт до\nг. Магадан предоставляется.\n\nОставшиеся проживают\nпод свою ответственность.", 60, h - 280, font("CourierNewPSMT", 27), print_)
    circleMark(w - 190, 170, 80, NSColor(calibratedRed: 0.3, green: 0.2, blue: 0.55, alpha: 0.7))
    text("ПЕЧАТЬ", w - 255, 190, font("PTSans-Bold", 24), NSColor(calibratedRed: 0.3, green: 0.2, blue: 0.55, alpha: 0.6))
    text("Не поеду. П.Г.", 60, 120, font("Georgia-Italic", 34), ink, hand: true)
}

// --- Stollen 3 plan on Orlow's wall: drifts in red, the old ventilation raise marked
canvas(1024, 768, "AditPlan") { w, h in
    paper(w, h, NSColor(calibratedRed: 0.86, green: 0.87, blue: 0.84, alpha: 1), stains: 8)
    for k in 0..<33 { line(CGFloat(k) * 32, 0, CGFloat(k) * 32, h, NSColor(calibratedRed: 0.3, green: 0.45, blue: 0.6, alpha: 0.18), 1) }
    for k in 0..<25 { line(0, CGFloat(k) * 32, w, CGFloat(k) * 32, NSColor(calibratedRed: 0.3, green: 0.45, blue: 0.6, alpha: 0.18), 1) }
    text("ШТОЛЬНЯ №3  ·  ПЛАН ГОРНЫХ ВЫРАБОТОК  ·  М 1:500", 40, h - 30, font("PTSans-Bold", 24), print_)
    line(80, 380, 620, 380, redInk, 10)                                                       // main drift
    line(620, 380, 900, 520, redInk, 7); line(620, 380, 880, 220, redInk, 7); line(400, 380, 420, 640, redInk, 6)
    text("портал", 60, 350, font("PTSans-Regular", 22), print_)
    text("штрек 1", 700, 560, font("PTSans-Regular", 22), print_); text("штрек 2", 760, 210, font("PTSans-Regular", 22), print_)
    line(440, 380, 470, 600, NSColor(calibratedRed: 0.1, green: 0.3, blue: 0.6, alpha: 0.9), 4)   // ventilation raise to the surface
    text("вент. ходок → выход на склон", 470, 650, font("PTSans-Bold", 22), NSColor(calibratedRed: 0.1, green: 0.3, blue: 0.6, alpha: 1))
    text("доска почёта  42 м", 300, 330, font("Georgia-Italic", 22), ink, hand: true)
}

// --- Pjotr's boiler log: winter 2003/04, the fight to keep boiler 2 alive, the last entry
canvas(1024, 768, "KesselLog") { w, h in
    paper(w, h, bookTone)
    NSColor(calibratedWhite: 0, alpha: 0.18).setFill(); NSRect(x: w / 2 - 6, y: 0, width: 12, height: h).fill()   // spine
    for k in 0..<20 { line(20, h - 60 - CGFloat(k) * 34, w - 20, h - 60 - CGFloat(k) * 34, NSColor(calibratedRed: 0.4, green: 0.5, blue: 0.7, alpha: 0.28), 1) }
    text("КОТЁЛ №2   давл.  t°   уголь", 30, h - 22, font("CourierNewPS-BoldMT", 20), print_)
    text("12.01  3,8  71  уголь кончается\n19.01  3,5  68  Антонине 2 ведра\n02.02  3,1  60  жгу доски из школы\n14.02  ЛЭП обрезали. только дрова\n27.02  -52 на улице. держу.\n15.03  Сухова увезли в Сусуман\n27.03  Антонине последнее ведро", 30, h - 64, font("Georgia-Italic", 22), ink, hand: true, lineGap: 1.55)
    text("30.03.2004\nКотёл 2 погашен.\nАнтонину забрал вертолёт МЧС.\nГреть больше некого.\n\nИду в третью штольню\nза доской почёта.\nРебята поедут со мной.\n\nШура, жди звонка по полевому.", w / 2 + 30, h - 64, font("Georgia-Italic", 24), ink, hand: true, lineGap: 1.4)
}

// --- the radio amateur's log: the field-telephone calls from the adit, the collapse, silence
canvas(1024, 768, "RadioLog") { w, h in
    paper(w, h, bookTone)
    NSColor(calibratedWhite: 0, alpha: 0.18).setFill(); NSRect(x: w / 2 - 6, y: 0, width: 12, height: h).fill()
    text("АППАРАТНЫЙ ЖУРНАЛ  UA0IKS", 30, h - 22, font("CourierNewPS-BoldMT", 20), print_)
    text("02.04  21:00  Петя на полевом.\n       Протянул кабель до штольни.\n03.04  09:15  Вошёл. Ворота открыл\n       ключом Орлова.\n03.04  11:40  Доска у него.\n       Идёт назад.\n03.04  11:52  Грохот. Связь пропала.", 30, h - 64, font("Georgia-Italic", 22), ink, hand: true, lineGap: 1.5)
    text("03.04  12:30  тишина\n03.04  16:00  тишина\n04.04  08:00  тишина\n\nЗвонил в Сусуман.\nСказали: весной спасатели.\n\nЛента №41 — всё записано.\nОтдам Орлову.", w / 2 + 30, h - 64, font("Georgia-Italic", 24), redInk, hand: true, lineGap: 1.45)
}

// --- Pjotr's note at the ventilation raise: he got out
canvas(512, 512, "NoteMine") { w, h in
    paper(w, h, NSColor(calibratedRed: 0.8, green: 0.76, blue: 0.64, alpha: 1), stains: 18)
    NSColor(calibratedWhite: 0.1, alpha: 0.25).setFill()                                      // coal dust fingerprints
    for _ in 0..<5 { NSBezierPath(ovalIn: NSRect(x: rr(0, w), y: rr(0, h), width: 40, height: 52)).fill() }
    text("Завалило за мной.\nВыхожу через вент. ходок.\nДоска со мной.\nРебята едут домой.\n\nШура, Орлов — я живой.\nВаля, Лида — иду.\n\n        П. Г.  04.04.2004", 24, h - 30, font("Georgia-Italic", 27), pencil, hand: true, lineGap: 1.3)
}

// --- Lida's drawing: the house, the sun, papa, mama and her
canvas(512, 512, "DrawingLida") { w, h in
    NSColor(calibratedRed: 0.96, green: 0.95, blue: 0.9, alpha: 1).setFill(); NSRect(x: 0, y: 0, width: w, height: h).fill()
    NSColor(calibratedRed: 0.95, green: 0.75, blue: 0.1, alpha: 1).setFill(); NSBezierPath(ovalIn: NSRect(x: 380, y: 380, width: 90, height: 90)).fill()
    for k in 0..<10 { let a = CGFloat(k) * .pi / 5; line(425 + cos(a) * 55, 425 + sin(a) * 55, 425 + cos(a) * 85, 425 + sin(a) * 85, NSColor(calibratedRed: 0.95, green: 0.7, blue: 0.1, alpha: 1), 6) }
    NSColor(calibratedRed: 0.85, green: 0.6, blue: 0.65, alpha: 1).setFill(); NSRect(x: 40, y: 120, width: 170, height: 220).fill()   // the block
    for r in 0..<4 { for c in 0..<3 { NSColor(calibratedRed: 0.3, green: 0.5, blue: 0.85, alpha: 1).setFill(); NSRect(x: 55 + CGFloat(c) * 52, y: 140 + CGFloat(r) * 50, width: 30, height: 30).fill() } }
    for (k, x) in [260, 330, 395].enumerated() {
        let s: CGFloat = k == 2 ? 0.7 : 1.0, c = [NSColor.brown, NSColor.systemPink, NSColor.systemRed][k]
        line(CGFloat(x), 120, CGFloat(x), 120 + 110 * s, c, 7); line(CGFloat(x) - 30 * s, 190 * s + 40, CGFloat(x) + 30 * s, 190 * s + 40, c, 6)
        line(CGFloat(x), 120, CGFloat(x) - 22, 70, c, 6); line(CGFloat(x), 120, CGFloat(x) + 22, 70, c, 6)
        c.setFill(); NSBezierPath(ovalIn: NSRect(x: CGFloat(x) - 24 * s, y: 120 + 110 * s, width: 48 * s, height: 48 * s)).fill()
    }
    NSColor(calibratedRed: 0.2, green: 0.6, blue: 0.25, alpha: 1).setFill(); NSRect(x: 0, y: 0, width: w, height: 70).fill()
    text("ПАПА  МАМА  Я", 230, 60, font("PTSans-Bold", 30), NSColor(calibratedRed: 0.2, green: 0.2, blue: 0.6, alpha: 1))
    text("Лида 7 лет", 40, 470, font("PTSans-Bold", 34), NSColor(calibratedRed: 0.8, green: 0.2, blue: 0.2, alpha: 1))
}

// --- family photo (Gorbunovs) and Antonina's husband (portrait with a black ribbon over the corner)
canvas(512, 384, "FamilyPhoto") { w, h in
    NSColor(calibratedWhite: 0.6, alpha: 1).setFill(); NSRect(x: 0, y: 0, width: w, height: h).fill()
    NSColor(calibratedWhite: 0.42, alpha: 1).setFill(); NSRect(x: 0, y: 0, width: w, height: h * 0.4).fill()
    person(w * 0.3, 20, 120, helmet: false, tone: 0.4); person(w * 0.62, 20, 110, helmet: false, tone: 0.8); person(w * 0.46, 10, 70, helmet: false, tone: 1)
    soften(1.8)
    agePhoto(w, h, border: 16, sepia: false)
}
canvas(384, 512, "Husband") { w, h in
    NSColor(calibratedWhite: 0.55, alpha: 1).setFill(); NSRect(x: 0, y: 0, width: w, height: h).fill()
    person(w / 2, 0, 230, helmet: false, tone: 0.5)
    soften(2.5)
    agePhoto(w, h, border: 18)
    NSColor(calibratedWhite: 0.02, alpha: 1).setFill()
    let rib = NSBezierPath(); rib.move(to: NSPoint(x: w - 120, y: h)); rib.line(to: NSPoint(x: w - 70, y: h)); rib.line(to: NSPoint(x: w, y: h - 70)); rib.line(to: NSPoint(x: w, y: h - 120)); rib.close(); rib.fill()
}
