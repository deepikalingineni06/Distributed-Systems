#importing required packages
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import os,time
import requests
import json
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

#Getting the files and directories present in the BASE DIR
data = os.listdir(BASE_DIR)


#Getting the Data from server2 Two using requests package 
#The data will be in the form of request.response and we can get text
#using request.response.text and format it accordingly
try:
    data2 = requests.get("http://localhost:8000")
    print("server B got connected")
    data2 = data2.text
except:
    print("Not able to get server B info")


file_sizes = []
file_modified = []

#getting file sizes and last modified info
def get_file_sizes(lists):
    for i in lists:
        stat = os.stat(i)
        file_sizes.append(stat.st_size)
        file_modified.append(time.ctime(stat.st_mtime)[4:10])
get_file_sizes(data)



try:
    #Appending the data of server 2  to the data of server 1
    def appender(data2):
        data_in_str = eval(data2)
        data2 = data_in_str["body"]
        data2_sizes = data_in_str["sizes"]
        data2_times = data_in_str["times"]
        data.extend(data2)
        file_sizes.extend(data2_sizes)
        file_modified.extend(data2_times)

    appender(data2)
except:
    print("NO data from server B")

final_data = data
count = 1 
#Creating a class named Server inheriting BaseHTTPRequestHandler
#Using do_GET method to handle GET requests
class Server(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            print("server A working")
            self.send_response(200)
        except:
            file_to_open = "not working"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(json.dumps({'body':data,'sizes':file_sizes,'times':file_modified}),'utf-8'))



#Creating a server on localhost at port 8080 and making it use the server class created
#Running the server forever till the termination of program
httpd = HTTPServer(('localhost', 8080), Server)
print("server1 is working now")
httpd.serve_forever()
