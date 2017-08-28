from os import path, makedirs
from bottle import route, request, run, get, post, HTTPResponse, default_app, static_file
import base64
import time
import json
import magic
import random
from hashlib import sha1
import re

id_pattern = re.compile(r"^[0-9]{10}[-][0-9a-fA-F]{40}$")
file_path_pattern = re.compile(r"^[0-9]{6}\/[0-9]{2}\/[0-9]{2}\/[0-9a-fA-F]{40}$")

@route('/storage/<file_path:re:.+>')
def storage(file_path):
    if file_path_pattern.match(file_path):
        return static_file(file_path, root=ROOT_DIR, download=True)
    else:
        theBody = json.dumps({'bad file path': file_path})
        return HTTPResponse(status=500, body=theBody)

@route('/id/<id_hash:re:.+>') # return file by id-hash
def get_by_id(id_hash):
    if id_pattern.match(id_hash):
        splitted = id_hash.split('-')
        s0, file_name = splitted[0], splitted[1]
        file_path = "%s/%s/%s/%s" % (s0[:6], s0[6:8], s0[8:], file_name)
        return static_file(file_path, root=ROOT_DIR, download=True)
    else:
        theBody = json.dumps({'bad id format': id_hash})
        return HTTPResponse(status=500, body=theBody)

@post('/upload')
def do_upload():
    upload = request.body.getvalue()
    random.seed()

    try:
        decode_data = base64.decodebytes(upload)

        file_type = magic.from_buffer(decode_data, mime=True)

        if file_type not in ('image/png', 'image/svg+xml', 'image/jpeg', 'image/gif'):
            theBody = json.dumps({'bad file type': file_type})
            return HTTPResponse(status=500, body=theBody)

    except Exception as e:
        theBody = json.dumps({'error': str(e)})
        return HTTPResponse(status=500, body=theBody)

    root_dir = ROOT_DIR
    
    s_time = str(int(time.time()))
    s_path = "%s/%s/%s/%s" % (root_dir, s_time[:6], s_time[6:8], s_time[8:])
    if not path.exists(s_path):
        makedirs(s_path)

#    filename = str(random.randrange(1000,9999))
    filename = sha1(decode_data).hexdigest()
    file_path = "%s/%s" % (s_path, filename)
    with open(file_path, 'wb') as f:
        f.write(decode_data)
    theBody = json.dumps({
        'id': "%s-%s" % (s_time, filename),
        'url':"id/%s-%s" % (s_time, filename),
        'file type': file_type,
        'size': len(decode_data),
        'message': "File successfully saved to %s" % (file_path)
        })
    return HTTPResponse(status=200, body=theBody)

@get('/encode')  # base64 encoder - just for testing 
def upload_view():
    return """
        <form action="/encode" method="post" enctype="multipart/form-data">
          <input type="text" name="name" />
          <input type="file" name="data" />
          <input type="submit" name="submit" value="Encode now" />
        </form>
        """    

@post('/encode')
def do_upload():
    data = request.files.get('data')
    if data is not None:
        raw = data.file.read()
        filename = data.filename
        encoded = base64.b64encode(raw).decode('ascii')
        return """
        You uploaded %s (%d bytes).</br>
        Encoded:</br>
        <textarea readonly>%s</textarea>
        """ % (filename, len(raw), encoded)

    return "You missed a field."


# Run bottle internal test server when invoked directly ie: non-uxsgi mode
if __name__ == '__main__':
    ROOT_DIR = 'storage'
    run(host='0.0.0.0', port=8080, debug=True, reloader=True)
# Run bottle in application mode. Required in order to get the application working with uWSGI!
else:
    ROOT_DIR = '/storage'
    app = application = default_app()

