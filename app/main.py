#!/usr/bin/env python3

from os import path, makedirs
from bottle import route, request, run, get, post
from bottle import default_app, static_file, error, response
import base64
import json
import magic
from hashlib import sha1
import re
from io import BytesIO

file_path_pattern = re.compile(
    r"^[0-9a-fA-F]{2}\/[0-9a-fA-F]{2}\/[0-9a-fA-F]{40}$")
file_pattern = re.compile(
    r"^[0-9a-fA-F]{40}$")


@error(404)
def error404(error):
    theBody = json.dumps({'error': 'Not Found'})
    response.content_type = 'application/json'
    response.status = 404
    return theBody


@error(405)
def error405(error):
    theBody = json.dumps({'error': 'Method Not Allowed'})
    response.content_type = 'application/json'
    response.status = 405
    return theBody


@route('/storage/<file_path:re:.+>')
def storage(file_path):
    if file_path_pattern.match(file_path):
        return static_file(file_path, root=ROOT_DIR, download=True)
    else:
        theBody = json.dumps({'error': 'Bad Request'})
        response.content_type = 'application/json'
        response.status = 400
        return theBody


@get('/pictures/<f_hash:re:.+>')  # return file by file hash
def get_by_hash(f_hash):
    if file_pattern.match(f_hash):
        file_path = "%s/%s/%s" % (f_hash[:2], f_hash[2:4], f_hash)
        return static_file(file_path, root=ROOT_DIR, download=True)
    else:
        theBody = json.dumps({'error': 'Bad Request'})
        response.content_type = 'application/json'
        response.status = 400
        return theBody


@post('/pictures')
def do_upload():
    try:
        # for BytesIO
        if request.body is BytesIO:
            upload = request.body.getvalue()
        # for TemporaryFile
        else:
            upload = request.body.read()
        len_upload = len(upload)
        print("len of upload: ", len_upload)
    except Exception as e:
        print("request.body.getvalue() cause error: ", e)

    try:
        decode_data = base64.decodebytes(upload)
        file_type = magic.from_buffer(decode_data, mime=True)
        if file_type not in (
                'image/png',
                'image/svg+xml',
                'image/jpeg',
                'image/gif'):
            print("error: Wrong file type: %s, len of upload: %s" %
                  (file_type, len_upload))
            theBody = json.dumps({'error': 'Wrong file type'})
            response.content_type = 'application/json'
            response.status = 400
            return theBody

    except Exception as e:
        print("decode magic type of file error: ", e)
        theBody = json.dumps({'error': str(e)})
        response.content_type = 'application/json'
        response.status = 500
        return theBody

    file_name = sha1(decode_data).hexdigest()
    dir_path = "%s/%s/%s" % (ROOT_DIR, file_name[:2], file_name[2:4])
    if not path.exists(dir_path):
        makedirs(dir_path)

    file_path = "%s/%s" % (dir_path, file_name)
    with open(file_path, 'wb') as f:
        f.write(decode_data)
    file_size = len(decode_data)
    print("filename(hash): %s, filetype: %s, size: %d" %
          (file_name, file_type, file_size))
    theBody = json.dumps({
        'hash': "%s" % (file_name),
        'filetype': file_type,
        'size': file_size,
        'message': "File successfully saved to %s" % (file_path)
    })
    response.content_type = 'application/json'
    response.status = 200
    return theBody


@get('/encode')  # base64 encoder - just for testing
def upload_view():
    return """
        <form action="/encode" method="post" enctype="multipart/form-data">
          <input type="text" name="name" />
          <input type="file" name="data" />
          </br></br>
          <input type="submit" name="submit" value="Encode now" />
        </form>
        """


@post('/encode')
def do_encode():
    data = request.files.get('data')
    if data is not None:
        raw = data.file.read()
        filename = data.filename
        encoded = base64.b64encode(raw).decode('ascii')
        return """
        You uploaded %s (%d bytes).</br>
        Encoded:</br></br>
        <textarea readonly>%s</textarea>
        """ % (filename, len(raw), encoded)

    return "You missed a field."


# Run bottle internal test server when invoked directly ie: non-uxsgi mode
if __name__ == '__main__':
    ROOT_DIR = 'storage'
    run(host='0.0.0.0', port=8080, debug=True, reloader=True)
# Run bottle in application mode.
# Required in order to get the application working with uWSGI!
else:
    ROOT_DIR = '/storage'
    app = application = default_app()
