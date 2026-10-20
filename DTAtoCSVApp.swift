import AppKit

final class DropView: NSView {
    weak var controller: AppDelegate?
    private var highlighted = false

    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        registerForDraggedTypes([.fileURL])
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        registerForDraggedTypes([.fileURL])
    }

    override func mouseDown(with event: NSEvent) {
        controller?.chooseFiles(nil)
    }

    override func draggingEntered(_ sender: NSDraggingInfo) -> NSDragOperation {
        highlighted = true
        needsDisplay = true
        return .copy
    }

    override func draggingExited(_ sender: NSDraggingInfo?) {
        highlighted = false
        needsDisplay = true
    }

    override func prepareForDragOperation(_ sender: NSDraggingInfo) -> Bool {
        true
    }

    override func performDragOperation(_ sender: NSDraggingInfo) -> Bool {
        highlighted = false
        needsDisplay = true
        let items = sender.draggingPasteboard.readObjects(
            forClasses: [NSURL.self],
            options: [.urlReadingFileURLsOnly: true]
        ) as? [URL] ?? []
        controller?.convert(items)
        return !items.isEmpty
    }

    override func draw(_ dirtyRect: NSRect) {
        NSColor.windowBackgroundColor.setFill()
        bounds.fill()

        let panel = bounds.insetBy(dx: 24, dy: 20)
        let path = NSBezierPath(roundedRect: panel, xRadius: 10, yRadius: 10)
        (highlighted ? NSColor.selectedControlColor.withAlphaComponent(0.16) : NSColor.controlBackgroundColor).setFill()
        path.fill()

        (highlighted ? NSColor.selectedControlColor : NSColor.separatorColor).setStroke()
        path.lineWidth = 2
        path.stroke()

        drawCentered("Drop .dta files or folders here", y: bounds.midY + 18, size: 18, weight: .semibold)
        drawCentered("or click this area to choose files", y: bounds.midY - 12, size: 13, weight: .regular, color: .secondaryLabelColor)
    }

    private func drawCentered(_ text: String, y: CGFloat, size: CGFloat, weight: NSFont.Weight, color: NSColor = .labelColor) {
        let attributes: [NSAttributedString.Key: Any] = [
            .font: NSFont.systemFont(ofSize: size, weight: weight),
            .foregroundColor: color
        ]
        let value = text as NSString
        let textSize = value.size(withAttributes: attributes)
        value.draw(at: NSPoint(x: bounds.midX - textSize.width / 2, y: y), withAttributes: attributes)
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    private let window = NSWindow(
        contentRect: NSRect(x: 0, y: 0, width: 560, height: 360),
        styleMask: [.titled, .closable, .miniaturizable],
        backing: .buffered,
        defer: false
    )
    private let dropView = DropView()
    private let progress = NSProgressIndicator()
    private let status = NSTextField(labelWithString: "Ready")
    private var outputBuffer = ""
    private var task: Process?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        buildWindow()
        NSApp.activate(ignoringOtherApps: true)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }

    func application(_ application: NSApplication, open urls: [URL]) {
        convert(urls)
    }

    @objc func chooseFiles(_ sender: Any?) {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = true
        panel.prompt = "Convert"
        panel.beginSheetModal(for: window) { [weak self] response in
            guard response == .OK else { return }
            self?.convert(panel.urls)
        }
    }

    func convert(_ urls: [URL]) {
        guard task == nil else { return }
        let count = countDTAFiles(urls)
        guard count > 0 else {
            status.stringValue = "No .dta files found."
            return
        }

        status.stringValue = "Preparing \(count) file\(count == 1 ? "" : "s")..."
        progress.minValue = 0
        progress.maxValue = Double(max(count, 1))
        progress.doubleValue = 0
        progress.isIndeterminate = count == 1
        if progress.isIndeterminate {
            progress.startAnimation(nil)
        }

        let process = Process()
        process.executableURL = Bundle.main.resourceURL?.appendingPathComponent("DTAtoCSVCore")
        process.arguments = urls.map(\.path)
        var env = ProcessInfo.processInfo.environment
        env["DTA_TO_CSV_NO_UI"] = "1"
        process.environment = env

        let outPipe = Pipe()
        let errPipe = Pipe()
        process.standardOutput = outPipe
        process.standardError = errPipe
        outPipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard !data.isEmpty, let text = String(data: data, encoding: .utf8) else { return }
            DispatchQueue.main.async { self?.consume(text) }
        }

        process.terminationHandler = { [weak self] finished in
            DispatchQueue.main.async {
                self?.task = nil
                self?.progress.stopAnimation(nil)
                self?.progress.isIndeterminate = false
                if finished.terminationStatus == 0 {
                    self?.progress.doubleValue = self?.progress.maxValue ?? 1
                    self?.status.stringValue = "Done. CSV folder opened."
                } else {
                    let error = String(data: errPipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
                    self?.status.stringValue = error.isEmpty ? "Failed." : "Failed: \(error.prefix(120))"
                }
            }
        }

        do {
            task = process
            try process.run()
        } catch {
            task = nil
            progress.stopAnimation(nil)
            status.stringValue = "Failed to start converter."
        }
    }

    private func buildWindow() {
        window.title = "DTA → CSV"
        window.center()

        guard let content = window.contentView else { return }
        dropView.controller = self
        dropView.translatesAutoresizingMaskIntoConstraints = false
        progress.translatesAutoresizingMaskIntoConstraints = false
        status.translatesAutoresizingMaskIntoConstraints = false
        status.lineBreakMode = .byTruncatingMiddle

        let button = NSButton(title: "Choose Files...", target: self, action: #selector(chooseFiles(_:)))
        button.bezelStyle = .rounded
        button.translatesAutoresizingMaskIntoConstraints = false

        content.addSubview(dropView)
        content.addSubview(progress)
        content.addSubview(status)
        content.addSubview(button)

        NSLayoutConstraint.activate([
            dropView.leadingAnchor.constraint(equalTo: content.leadingAnchor),
            dropView.trailingAnchor.constraint(equalTo: content.trailingAnchor),
            dropView.topAnchor.constraint(equalTo: content.topAnchor),
            dropView.heightAnchor.constraint(equalToConstant: 245),

            progress.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 28),
            progress.trailingAnchor.constraint(equalTo: content.trailingAnchor, constant: -28),
            progress.topAnchor.constraint(equalTo: dropView.bottomAnchor, constant: 16),

            status.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 28),
            status.trailingAnchor.constraint(equalTo: button.leadingAnchor, constant: -16),
            status.centerYAnchor.constraint(equalTo: button.centerYAnchor),

            button.trailingAnchor.constraint(equalTo: content.trailingAnchor, constant: -28),
            button.topAnchor.constraint(equalTo: progress.bottomAnchor, constant: 24)
        ])

        window.makeKeyAndOrderFront(nil)
    }

    private func consume(_ text: String) {
        outputBuffer += text
        while let newline = outputBuffer.firstIndex(of: "\n") {
            let line = String(outputBuffer[..<newline])
            outputBuffer.removeSubrange(...newline)
            handle(line)
        }
    }

    private func handle(_ line: String) {
        let parts = line.split(separator: "\t", omittingEmptySubsequences: false).map(String.init)
        guard parts.count >= 4 else { return }
        let kind = parts[0]
        let index = Int(parts[1]) ?? 0
        let total = Int(parts[2]) ?? 0
        let label = parts[3]

        if kind == "PROGRESS" {
            status.stringValue = "Converting \(index)/\(total): \(label)"
            if !progress.isIndeterminate {
                progress.doubleValue = Double(max(index - 1, 0))
            }
        } else if kind == "DONE" {
            status.stringValue = "Converted \(index)/\(total)"
            if !progress.isIndeterminate {
                progress.doubleValue = Double(index)
            }
        }
    }

    private func countDTAFiles(_ urls: [URL]) -> Int {
        var count = 0
        let manager = FileManager.default
        for url in urls {
            var isDirectory: ObjCBool = false
            guard manager.fileExists(atPath: url.path, isDirectory: &isDirectory) else { continue }
            if isDirectory.boolValue {
                if let items = manager.enumerator(at: url, includingPropertiesForKeys: nil) {
                    for case let item as URL in items {
                        if item.pathExtension.lowercased() == "dta" { count += 1 }
                    }
                }
            } else if url.pathExtension.lowercased() == "dta" {
                count += 1
            }
        }
        return count
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
