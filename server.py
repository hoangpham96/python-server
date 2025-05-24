import http.server as httpServer
class requestHandler(httpServer.BaseHTTPRequestHandler):
    page = '''
    <html>
        <body>
            <p>Hello, web!</p>
        </body>
    </html>
    '''

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header("Content-Length", str(len(self.page)))
        self.end_headers()
        self.wfile.write(self.page.encode('utf-8'))
    
#----------------------------------------------------------------------

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = httpServer.HTTPServer(serverAddress, requestHandler)
    server.serve_forever()
