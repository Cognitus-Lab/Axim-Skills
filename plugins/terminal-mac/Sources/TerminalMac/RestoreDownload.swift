import Foundation
import TerminalMacCore

/// URLSession preserves HTTP resume data after interrupted downloads. Only Apple's
/// framework-selected restore URL is accepted by the first-run flow.
final class RestoreDownload: NSObject, URLSessionDownloadDelegate {
    let destination: URL
    let resumeURL: URL
    var continuation: CheckedContinuation<URL, Error>?
    var session: URLSession?
    var result: Result<URL, Error>?
    var lastPercent = -1
    init(destination: URL) {
        self.destination = destination
        resumeURL = destination.appendingPathExtension("resume")
    }
    func run(from url: URL) async throws -> URL {
        try await withCheckedThrowingContinuation { continuation in
            self.continuation = continuation
            let configuration = URLSessionConfiguration.default
            configuration.timeoutIntervalForRequest = 120
            configuration.timeoutIntervalForResource = 86400
            let session = URLSession(configuration: configuration, delegate: self, delegateQueue: nil)
            self.session = session
            let task: URLSessionDownloadTask
            if let resume = try? Data(contentsOf: resumeURL) {
                stderr("Resuming the macOS download…")
                task = session.downloadTask(withResumeData: resume)
            } else { task = session.downloadTask(with: url) }
            task.resume()
        }
    }
    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didWriteData bytesWritten: Int64, totalBytesWritten: Int64, totalBytesExpectedToWrite: Int64) {
        guard totalBytesExpectedToWrite > 0 else { return }
        let percent = Int(Double(totalBytesWritten) / Double(totalBytesExpectedToWrite) * 100)
        if percent / 5 != lastPercent / 5 || lastPercent == -1 {
            lastPercent = percent
            stderr(String(format: "Downloading macOS: %d%% (%.1f / %.1f GiB)", percent, Double(totalBytesWritten) / 1_073_741_824, Double(totalBytesExpectedToWrite) / 1_073_741_824))
        }
    }
    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didFinishDownloadingTo location: URL) {
        do {
            guard let response = downloadTask.response as? HTTPURLResponse, [200, 206].contains(response.statusCode) else { throw Failure("Apple restore-image download failed") }
            try FileManager.default.moveItem(at: location, to: destination)
            try? FileManager.default.removeItem(at: resumeURL)
            result = .success(destination)
        } catch { result = .failure(error) }
    }
    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        if let error {
            if let resume = (error as NSError).userInfo[NSURLSessionDownloadTaskResumeData] as? Data {
                try? resume.write(to: resumeURL, options: .atomic)
            } else { try? FileManager.default.removeItem(at: resumeURL) }
        }
        continuation?.resume(with: result ?? .failure(error ?? Failure("Download ended without a file")))
        continuation = nil
        session.finishTasksAndInvalidate(); self.session = nil
    }
}
