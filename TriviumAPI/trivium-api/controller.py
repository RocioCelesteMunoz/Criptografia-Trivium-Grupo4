from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
from flask import jsonify

from trivium import Trivium

from PIL import Image

import base64



app = Flask(__name__)


img_ext = '.png'
img_orig_name = 'originalImg'
img_enc_name = 'encryptedImg'
img_dec_name = 'decryptedImg'

@app.route('/hello')
def index():
    return 'Web App with Python Flask!'



@app.route('/encrypt', methods=['POST'])
@cross_origin(origin='http://localhost:4200')
@cross_origin(supports_credentials=True)
def encrypt():
    request_data = request.get_json()

    image_b64 = request_data['image']


    image_b64_bytes = bytes(image_b64, 'utf-8')

    # Decode image from base64
    decoded_img_name = img_orig_name + img_ext

    with open(decoded_img_name, "wb") as fh:
        fh.write(base64.decodebytes(image_b64_bytes))

    # Open image
    image = Image.open(decoded_img_name)
    #image = Image.open('Arrow-T1.png')

    # Encoding a string
    trivium_encoder = Trivium()
    trivium_encoder.encrypt_image(image)

    # Encode image in base64
    encoded_img_name = img_enc_name + img_ext 
    with open(encoded_img_name, "rb") as img_file:
        image_64_encode = base64.b64encode(img_file.read())

    return jsonify(
        image = str(image_64_encode)
    )


@app.route('/decrypt', methods=['POST'])
def decrypt():
    request_data = request.get_json()

    image_b64 = request_data['image']
    image_b64_bytes = bytes(image_b64, 'utf-8')

    # Decode image from base64
    decoded_img_name = img_enc_name + img_ext

    with open(decoded_img_name, "wb") as fh:
        fh.write(base64.decodebytes(image_b64_bytes))

    # Open image
    image = Image.open(decoded_img_name)
    #image = Image.open('Arrow-T1.png')

    # Encoding a string
    trivium_decoder = Trivium()
    trivium_decoder.decrypt_image(image)

    # Encode image in base64
    encoded_img_name = img_dec_name + img_ext 
    with open(encoded_img_name, "rb") as img_file:
        image_64_encode = base64.b64encode(img_file.read())

    return 'tu imagen fue deshackeada: ' + str(image_64_encode)



app.run(host='0.0.0.0', port=5000)

