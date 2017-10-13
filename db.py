# euclid ip: 198.110.204.9
from http.server import *
import json

d_db = None

def JSON_Load ( ):
  with open('db.json', 'r') as dbfile:
    return json.loads(dbfile.read().replace('\n', ''));
def JSON_Write ():
  with open('db.json', 'w') as dbfile:
    dbfile.write(json.dumps(d_db));

def JSON_Get(key):
  return str(d_db.get(key));
def JSON_Del_All():
  global d_db
  d_db = json.loads("{}");
  return "Deleted everything";
def JSON_Get_All():
  _str = "";
  for key, value in d_db.items():
    _str += key + ", "
  if ( len(_str) > 0 ):
    _str = _str[0:-2]; # remove comma
  return "{ " + _str + " }";
def JSON_Del ( key ):
  if ( not key in d_db ):
    return "404 file not found";
  del d_db[key]
  return "Deleted " + str(key);
def JSON_JSON_Put ( value ):
  print("VAL: ", value);
  nval = json.loads(value);POST
  _str = "";
  for key, value in nval.items():
    print("KEY: ", key);
    print("VALUE: ", value);
    _str += JSON_Put(key, value);
  return _str;

def JSON_Put ( key, value ):
  key = str(key);
  value = str(value);
  d_db[key] = value;
  return "Wrote " + value + " to " + key + "\n";


class DBRequestHandler(BaseHTTPRequestHandler):
  def RInfo_Struct(s):
    s.send_response(200);
    s.send_header('Content-type','text/html')
    s.end_headers()
    _len = s.headers['content-length'];
    dat = None
    if ( _len != None ):
      dat = s.rfile.read(int(_len)).decode('utf-8');
    return (s.headers['content-length'],
            s.path,
            JSON_Get(s.path),
            dat);
  Output = lambda s, msg: s.wfile.write(bytes(str(msg), 'utf-8'));
  def do_GET(s):
    length, key, value, data = s.RInfo_Struct();
    # Write content as utf-8 data
    omsg = str(key) + ": " + str(value) + "\n"
    if ( key == "/" ): omsg = JSON_Get_All() + "\n";
    s.Output(omsg);
  def do_PUT(s):
    length, key, value, data = s.RInfo_Struct();
    if ( key == "/" ): omsg = JSON_JSON_Put(data);
    else:              omsg = JSON_Put(key, data);
    JSON_Write();
    s.Output(omsg);
  def do_DELETE(s):
    length, key, value, data = s.RInfo_Struct();
    if ( key == "/" ): omsg = JSON_Del_All();
    else:              omsg = JSON_Del(key);
    print("DB: ", d_db);
    JSON_Write();
    s.Output(omsg);




if __name__ == "__main__":
  print("Starting server");
  d_db = JSON_Load();

  server_address = ('127.0.0.1', 26512);
  httpd = HTTPServer(server_address, DBRequestHandler);
  httpd.serve_forever();
