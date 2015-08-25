from tornado.ioloop import IOLoop
from tornado.web import Application
from Socket import Socket
from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int) # The default port, commandline option 

allowedHost = "http://localhost:8383" # The allowed host, only connections from this place are allowed

app = Application([
    (r'/socket', Socket)
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    IOLoop.instance().start()
