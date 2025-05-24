import BaseHTTPServer
class requestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("<html><body><h1>Hello, world!</h1></body></html>")
        return
    
#----------------------------------------------------------------------

if __name__ == '__main__':
    serverAddress = ('127.0.0.1', 8080)
    server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
