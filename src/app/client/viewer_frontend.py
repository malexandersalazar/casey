import webview

if __name__ == "__main__":
    webview.create_window('Casey', 'http://127.0.0.1:5000', fullscreen=True)
    webview.start()