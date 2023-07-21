#importing required packages
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import os,time
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

#Getting the files and directories present in the BASE DIR
data = os.listdir(BASE_DIR)
file_sizes = []
file_modified = []


#getting file sizes and last modified info
def get_file_sizes(lists):
    for i in lists:
        stat = os.stat(i)
        file_sizes.append(stat.st_size)
        file_modified.append(time.ctime(stat.st_mtime)[4:10])

get_file_sizes(data)




		
#Creating a class named Server inheriting BaseHTTPRequestHandler
#Using do_GET method to handle GET requests
class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    def do_GET(self):
        try:
            print("server B working")
        except:
            file_to_open = "File not found"
            self.send_response(404)
        self._set_headers()
        self.wfile.write(bytes(json.dumps({'body':data,'sizes':file_sizes,'times':file_modified}),'utf-8'))


#Creating a server on localhost at port 8000 and making it use the server class created
#Running the server forever till the termination of program
httpd = HTTPServer(('localhost', 8000), Server)
print("server B is working")
httpd.serve_forever()