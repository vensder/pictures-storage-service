#!/usr/bin/env python3

import base64
import os
import requests
from hashlib import sha1
import shutil

sha1_list = []

workdir = "pictures"
url = "http://pictures-storage-service:80/pictures"

for item_file in os.listdir("pictures"):
    with open("pictures/" + item_file, "rb") as image_file:
        image_file_read = image_file.read()
        sha1_list.append(sha1(image_file_read).hexdigest())
        encoded = base64.b64encode(image_file_read)  #.decode('ascii') # in one line
        response = requests.post(url, data=encoded)
        print(item_file, response)
        # encoded = base64.encodestring(image_file_read).decode('ascii') # with line wrapping
        with open("base64/" + item_file + "_base64", "w") as text_file:
            text_file.write(encoded.decode('ascii'))

#print(sha1_list)

for item_hash in sha1_list:
    response = requests.get(url + "/" + item_hash, stream=True)
    print(item_hash, response)
    with open("download/" + item_hash, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
