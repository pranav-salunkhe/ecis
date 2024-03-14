import os
from flask import Flask, render_template, send_file, url_for, request, jsonify
from . import encrypt as enc
import shutil
import cv2

def move_image_to_static():
    # Define paths
    root_folder = "project_web_app"  # Assuming this is your root folder
    image_file = "enc.jpg"
    static_folder = os.path.join(root_folder, "ecis", "static", "assets")

    # Ensure the static/assets folder exists, create if it doesn't
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

    # Move the image file to static/assets folder
    shutil.move(os.path.join(root_folder, image_file), os.path.join(static_folder, image_file))


def create_app(test_config=None):

    UPLOAD_FOLDER_CONTENT = 'ecis/static/assets'



    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    app.config['UPLOAD_FOLDER_CONTENT'] = UPLOAD_FOLDER_CONTENT

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    def save_image(file, folder, filename):
        file_path = os.path.join(app.config[folder], filename)
        file.save(file_path)

    @app.route('/')
    def hello_world():
        return render_template('index.html')
    
    @app.route('/upload', methods=['POST'])
    def upload():
        try:
            content_image = request.files['content_image']
            # style_image = request.files['style_image']

            if content_image:
                save_image(content_image, 'UPLOAD_FOLDER_CONTENT', 'ci.jpeg')
                # save_image(style_image, 'UPLOAD_FOLDER_STYLE', 'si.jpg')

                # run_style_transfer(UPLOAD_FOLDER_CONTENT, UPLOAD_FOLDER_STYLE)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

        return jsonify({'status': 'success', 'message': 'Images uploaded successfully'})

    # a simple page that says hello
    @app.route('/encrypt')
    def encrypt():
        try:
            static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
            global org_img_path
            org_img_path = os.path.join(static_folder, 'assets', 'ci.jpeg')
            print(os.path.join(os.path.dirname(os.path.abspath(__file__))))
            # org_img_path = url_for('static', filename='assets/test.png')
            print(org_img_path)
            key, m, n = enc.securekey(org_img_path)
            global blue, green, red
            blue, green, red = enc.decompose_matrix(org_img_path)
            blue_e, green_e, red_e = enc.dna_encode(blue, green, red)
            global Mk_e
            Mk_e = enc.key_matrix_encode(key, blue)
            blue_final, green_final, red_final = enc.xor_operation(blue_e, green_e, red_e, Mk_e)
            x, y, z, u, v = enc.gen_hyperchaos_seq(m, n)
            global fx,fy,fz
            fx, fy, fz = enc.sequence_indexing(x, y, z)
            blue_scrambled, green_scrambled, red_scrambled = enc.scramble(fx, fy, fz, blue_final, red_final, green_final)
            b, g, r = enc.dna_decode(blue_scrambled, green_scrambled, red_scrambled)
            global img
            img = enc.recover_image(b, g, r, org_img_path)
        
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

        return jsonify({'status': 'success', 'message': 'Image encrypted successfully'})
        # cv2.imwrite('static/assets/enc.jpg', img)
        # shutil.copyfile('project_web_app/enc.jpg', 'static/assets/enc.jpg')
        # print("decrypting...")
        # encrypt.decrypt(img, fx, fy, fz, org_img_path, Mk_e, blue, green, red)

    @app.route('/decrypt')
    def decrypt():
        try:
            enc.decrypt(img, fx, fy, fz, org_img_path, Mk_e, blue, green, red)
            # img, fx, fy, fz, org_img_path, Mk_e, blue, green, red = None
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

        return jsonify({'status': 'success', 'message': 'Image decrypted successfully'})

    @app.route('/downloadimage')
    def downloadimage():
        return send_file('static/assets/enc.jpg', mimetype='image/jpg')

    return app



