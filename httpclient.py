#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        response = data.split("\r\n")
        print("in get_code:")
        print(response[0])
        result = re.search('HTTP\/\d.*\d* (\d+)', response[0])
        code = int(result.group(1))
        return code 

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # Parsing URL
        parseUrl = urllib.parse.urlparse(url)
        host = parseUrl.netloc.split(":")[0]
        port = parseUrl.port
        path = parseUrl.path

        request = "GET {} HTTP/1.1\r\nHost: {}\r\n\r\n".format(path,host)
        self.connect(host,port)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()
        
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parseUrl = urllib.parse.urlparse(url)
        host = parseUrl.netloc.split(":")[0]
        port = parseUrl.port
        path = parseUrl.path

        content = ""
        if args:
            for arg in args:
                content+="{}={}&".format(arg,args[arg])
            if content[-1] == "&":
                content = content [:-1]
        repr(content)
        requestHeaders = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Length: {}\r\n\r\n".format(path,host,len(content))
        request = requestHeaders+content+"\r\n\r\n"
        self.connect(host,port)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()
        print("RESPONSE")
        print(response)
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
