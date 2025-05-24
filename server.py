import http.server as httpServer
import os

class Case(object):
    '''Base class for all cases.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return True

    def act(self, handler):
        pass

class Case_no_file(Case):
    '''File or directory does not exist.'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise Exception("'{0}' not found".format(handler.path))


class Case_existing_file(Case):
    '''File exists.'''

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path)

class Case_always_fail(Case):
    '''Base case if nothing else worked.'''

    def act(self, handler):
        raise Exception("Unknown object '{0}'".format(handler.path))
    
class Case_directory_index_file(Case):
    '''Serve index.html page for a directory.'''

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler))

class Case_directory_no_index_file(Case):
    '''Serve listing for a directory without an index.html page.'''

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)

class Case_cgi_file(Case):
    '''Something runnable.'''

    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')

    def act(self, handler):
        handler.run_cgi(handler.full_path)

class requestHandler(httpServer.BaseHTTPRequestHandler):
    Page = '''\
    <html>
    <body>
    <table>
    <tr>  <td>Header</td>         <td>Value</td>          </tr>
    <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
    <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
    <tr>  <td>Client port</td>    <td>{client_port}s</td> </tr>
    <tr>  <td>Command</td>        <td>{command}</td>      </tr>
    <tr>  <td>Path</td>           <td>{path}</td>         </tr>
    </table>
    </body>
    </html>
    '''

    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """
    
    Listing_Page = '''\
        <html>
        <body>
        <ul>
        {0}
        </ul>
        </body>
        </html>
        '''
    
    Cases = [Case_no_file(),
             Case_cgi_file(),
             Case_existing_file(),
             Case_directory_index_file(),
             Case_directory_no_index_file(),
             Case_always_fail()]

    def do_GET(self):
        try:
            # Figure out what exactly is being requested.
            self.full_path = os.getcwd() + self.path

            # Figure out how to handle it.
            for case in self.Cases:
                # handler = case()
                if case.test(self):
                    print(f"Handling {case.__class__.__name__}")
                    case.act(self)
                    break

        # Handle errors.
        except Exception as error:
            self.handle_error(error)

    # Handle unknown objects.
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        print(f"Error: {msg}")
        self.send_content(content, 404)

    # Send actual content.
    def send_content(self, content, status=200):
        if isinstance(content, str):
            content = content.encode('utf-8')

        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) 
                for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets))
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

    def run_cgi(self, full_path):
        cmd = "python " + full_path
        child_stdin, child_stdout = os.popen2(cmd)
        child_stdin.close()
        data = child_stdout.read()
        child_stdout.close()
        self.send_content(data)

    # def create_page(self):
    #     values = {
    #         'date_time'   : self.date_time_string(),
    #         'client_host' : self.client_address[0],
    #         'client_port' : self.client_address[1],
    #         'command'     : self.command,
    #         'path'        : self.path
    #     }
    #     page = self.Page.format(**values)
    #     return page

    # def send_page(self, page):
    #     self.send_response(200)
    #     self.send_header('Content-type', 'text/html')
    #     self.send_header('Content-Length', str(len(page)))
    #     self.end_headers()
    #     self.wfile.write(page.encode('utf-8'))
    
#----------------------------------------------------------------------

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = httpServer.HTTPServer(serverAddress, requestHandler)
    server.serve_forever()
