import os
from flask import Flask, url_for
from . import encrypt

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

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

    @app.route('/')
    def hello_world():
        return 'Hello, World!'
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        org_img_path = os.path.join(static_folder, 'assets', 'test.png')
   
        # org_img_path = url_for('static', filename='assets/test.png')
        print(org_img_path)
        key, m, n = encrypt.securekey(org_img_path)
        blue, green, red = encrypt.decompose_matrix(org_img_path)
        blue_e, green_e, red_e = encrypt.dna_encode(blue, green, red)
        Mk_e = encrypt.key_matrix_encode(key, blue)
        blue_final, green_final, red_final = encrypt.xor_operation(blue_e, green_e, red_e, Mk_e)
        x, y, z, u, v = encrypt.gen_hyperchaos_seq(m, n)
        fx, fy, fz = encrypt.sequence_indexing(x, y, z)
        blue_scrambled, green_scrambled, red_scrambled = encrypt.scramble(fx, fy, fz, blue_final, red_final, green_final)
        b, g, r = encrypt.dna_decode(blue_scrambled, green_scrambled, red_scrambled)
        img = encrypt.recover_image(b, g, r, org_img_path)

        print("decrypting...")
        encrypt.decrypt(img, fx, fy, fz, org_img_path, Mk_e, blue, green, red)
        return 'Hello, World!'

    return app



