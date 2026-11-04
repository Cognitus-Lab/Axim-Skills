// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "AximSkills",
    platforms: [.macOS(.v15)],
    products: [
        .executable(name: "terminal-mac", targets: ["TerminalMac"])
    ],
    targets: [
        .target(
            name: "TerminalMacCore",
            path: "plugins/terminal-mac/Sources/TerminalMacCore"
        ),
        .target(
            name: "CPhoneShim",
            path: "plugins/terminal-mac/Sources/CPhoneShim"
        ),
        .target(
            name: "TerminalUI",
            dependencies: ["CPhoneShim"],
            path: "plugins/terminal-mac/Sources/TerminalUI"
        ),
        .executableTarget(
            name: "TerminalMac",
            dependencies: ["TerminalMacCore", "TerminalUI", "CPhoneShim"],
            path: "plugins/terminal-mac/Sources/TerminalMac",
            linkerSettings: [
                .linkedFramework("Virtualization"),
                .linkedFramework("AppKit"),
                .linkedFramework("ScreenCaptureKit"),
                .linkedFramework("ApplicationServices"),
                .linkedFramework("ServiceManagement"),
                .linkedFramework("CoreMedia")
            ]
        ),
        .testTarget(
            name: "TerminalMacCoreTests",
            dependencies: ["TerminalMacCore"],
            path: "plugins/terminal-mac/Tests/TerminalMacCoreTests"
        )
    ],
    swiftLanguageVersions: [.v5]
)
