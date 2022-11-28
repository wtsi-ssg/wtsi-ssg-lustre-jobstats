#!/usr/bin/python
#Copyright (c) 2022 Genome Research Ltd.
#
#Author: James Beal <James.Beal@sanger.ac.uk> , Dave Holland <dh3@sanger.ac.uk>
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#
import sys
from subprocess import Popen, PIPE
import re
import glob
import yaml
import base64
import struct
import BaseHTTPServer 
import json


hostName = "0.0.0.0"
serverPort = 8081
fix_jobname = re.compile(r'^- job_id:(\s*)(\S(?:.*\S)?)\s*$')

def process_line(line):
  # Quote the job_id
  line = fix_jobname.sub(r'- job_id:\1"\2"',line)
  # Ensure valid yaml with a space
  return line.replace("max:", "max: ").replace("min:", "min: ").replace("sum:", "sum: ").replace("samples:", "samples: ").replace("sumsq:", "sumsq: ")

def run_lctl(cmd):
  p = Popen(cmd, stdout=PIPE)
  # skip the first two headers lines
  # https://stackoverflow.com/questions/15571137/yaml-scanner-scannererror-while-scanning-a-directive
  data_stream = "\n".join(map(process_line,p.communicate()[0].split("\n")[2:]))
  return  yaml.load(data_stream)

class MyServer(BaseHTTPServer.BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    def do_GET(self):
        data={}
        self._set_headers()
        osts=map( lambda x: x.replace("/proc/fs/lustre/obdfilter/",""),glob.glob("/proc/fs/lustre/obdfilter/lus*"))
        mdts=map( lambda x: x.replace("/proc/fs/lustre/mdt/",""),glob.glob("/proc/fs/lustre/mdt/lus*"))
        for ost in osts:
           data[ost]=run_lctl('lctl get_param obdfilter.{0}.job_stats'.format(ost).split())
        for mdt in mdts:
           data[mdt]=run_lctl('lctl get_param mdt.{0}.job_stats'.format(mdt).split())
        self.wfile.write(json.dumps(data))



if __name__ == "__main__":        
    webServer = BaseHTTPServer.HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
