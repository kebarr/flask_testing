import base64
import datetime
import io
import os
from cStringIO import StringIO


from flask import Flask, flash, request
from werkzeug.utils import secure_filename
from flask_caching import Cache

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy

import simplejson
import traceback

from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_bootstrap import Bootstrap

from lib.upload_file import uploadfile

cwd = os.getcwd()
UPLOAD_FOLDER = cwd + '/uploads'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
print UPLOAD_FOLDER
SECRET_KEY = 'hard to guess string'
UPLOAD_FOLDER = 'uploads/'


ALLOWED_EXTENSIONS = set(['txt', 'csv'])
IGNORED_FILES = set(['.gitignore'])

bootstrap = Bootstrap(app)


CACHE_CONFIG = {
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379'),
    'CACHE_DEFAULT_TIMEOUT':1200 # cache 20 mins- doesn't work!!!
}
cache = Cache()
cache.init_app(app, config=CACHE_CONFIG)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """

    i = 1
    while os.path.exists(os.path.join('UPLOAD_FOLDER', filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i += 1

    return filename



@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files['file']

        if files:
            filename = secure_filename(files.filename)
            filename = gen_file_name(filename)
            mime_type = files.content_type

            if not allowed_file(files.filename):
                print(files.filename)
                return render_template('file_uploaded.html', filename_not_uploaded=filename + " File type not allowed, not uploaded")

            else:
                # save file to disk
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'] , filename)
                if os.path.exists(uploaded_file_path):
                    # TODO if file exists, don't recompute, store peaks and reload to save computing time
                    return render_template('file_uploaded.html', filename=filename + " already uploaded, ready for use")
                files.save(uploaded_file_path)
                
                # get file size after saving
                size = os.path.getsize(uploaded_file_path)

                # return json for js call back
                result = uploadfile(name=filename, type=mime_type, size=size)
                print result.get_file()
            
                return render_template('file_uploaded.html', filename=filename)






def get_example_matches(fm, confidence="medium", number_to_plot=2):
    matches = fm.get_condifence_matches(confidence)
    number_matches = len(matches)
    index_to_plot_1 = np.random.randint(0, number_matches)
    index_to_plot_2 = np.random.randint(0, number_matches)
    m1 = fm.matches.matches[index_to_plot_1][2]
    m2 = fm.matches.matches[index_to_plot_2][2]
    ymax = np.max([np.max(m1.values), np.max(m2.values)]) + 50
    #string = '%d matches found' % number_matches
    fig, (ax1, ax2) = plt.subplots(1,2, sharex=True, sharey=True, figsize=(13, 5))
    plt.ylim(ymin=-200, ymax=ymax)
    ax1.set(xlabel = 'Shift (cm$^{-1}$)')
    ax1.set(ylabel='Intensity')
    ax2.set(xlabel = 'Shift (cm$^{-1}$)')
    ax2.set(ylabel='Intensity')
    m1.plot(ax=ax1)
    m2.plot(ax=ax2)
    io = StringIO()
    fig.savefig(io, format='png')
    return number_matches, base64.encodestring(io.getvalue())

def plot_example_match(fm, confidence="medium"):
    with open(fm, 'rb') as image:
        img_data = base64.b64encode(image.read())
    return render_template('plot_data.html', number_matches=42, number_locations=121, match_example=img_data, filename=fm, material="graphene_oxide", confidence=confidence)

@app.route('/uploadajax', methods = ['POST'])
def upload_image():
    if request.method == 'POST':
        files = request.files['file']
        if files:
            filename = secure_filename(files.filename)
            filename = gen_file_name(filename)
            if filename.endswith(".bmp") or filename.endswith(".jpeg"):
                mime_type = files.content_type
                # save file to disk
                uploaded_file_path = os.path.join(UPLOAD_FOLDER, filename)
                files.save(uploaded_file_path)
                # get file size after saving
                size = os.path.getsize(uploaded_file_path)
                uploadfile(name=filename, type=mime_type, size=size)
                data_filename = request.form.get("filename")
                material = request.form.get("material")
                sb = request.form.get("sb")
                output_filename = "test.png" # hard code for testing
                with open(output_filename, 'rb') as image:
                    img_str = base64.b64encode(image.read())
                return {'image': img_str, 'output_filename': output_filename}



@app.route('/download_image', methods=['GET', 'POST'])
def download():
    filename = request.form['output_filename']
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)

# TODO: export sample spectra, shuffle random spectrum in case poor match shown

@app.route('/find_peaks', methods=['POST'])
def actually_do_the_stuff():
    filename = "test_candidate.png"
    return plot_example_match(filename)

# @app.route('download-image', methods=['POST'])
# def send_image_to_user():
#     filename = 
#     send_from_directory()

@app.route('/')
def home():
    return render_template('file_uploaded.html')

@app.route('/test', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)


# grep -rno 'jquery-file-upload.appspot.com' .
#./index.html:15:jquery-file-upload.appspot.com
#./templates/index.html:15:jquery-file-upload.appspot.com
#./flask-file-uploader/static/js/main.js:37:jquery-file-upload.appspot.com
#./flask-file-uploader/static/js/main.js:49:jquery-file-upload.appspot.com
#./flask-file-uploader/static/js/app.js:19:jquery-file-upload.appspot.com
#./flask-file-uploader/templates/index.html:15:jquery-file-upload.appspot.com

#sed -i -e 's,jquery-file-upload.appspot.com,flask-file-uploader/static/js/jQuery-File-Upload-9.32.0/,g' ./index.html
#sed -i -e 's,jquery-file-upload.appspot.com,flask-file-uploader/static/js/jQuery-File-Upload-9.32.0/,g' ./templates/index.html
#sed -i -e 's,jquery-file-upload.appspot.com,flask-file-uploader/static/js/jQuery-File-Upload-9.32.0/,g' ./flask-file-uploader/static/js/main.js
#sed -i -e 's,jquery-file-upload.appspot.com,flask-file-uploader/static/js/jQuery-File-Upload-9.32.0/,g' ./flask-file-uploader/static/js/app.js
#sed -i -e 's,jquery-file-upload.appspot.com,flask-file-uploader/static/js/jQuery-File-Upload-9.32.0/,g' ./flask-file-uploader/templates/index.html
#sed -i -e 's,http://127.0.0.1:5000/flask-file-uploader,flask-file-uploader,g' ./flask-file-uploader/static/js/main.js
#sed -i -e 's,http://127.0.0.1:5000/flask-file-uploader,flask-file-uploader,g' ./flask-file-uploader/static/js/app.js
#sed -i -e 's,http://127.0.0.1:5000/flask-file-uploader,flask-file-uploader,g' ./index.html
#sed -i -e 's,http://127.0.0.1:5000/flask-file-uploader,flask-file-uploader,g'./templates/index.html
#sed -i -e 's,http://127.0.0.1:5000/flask-file-uploader,flask-file-uploader,g' ./flask-file-uploader/templates/index.html

#sed -i -e 's,127.0.0.1:5000/flask-file-uploader,jquery-file-upload.appspot.com,g' ./flask-file-uploader/static/js/main.js
#sed -i -e 's,127.0.0.1:5000/flask-file-uploader,jquery-file-upload.appspot.com,g' 
# (u'uploads/D_M1_Spleen_Slide3_2019_02_11_14_43_47.txt', 'graphene_oxide', False)

# first call: (u'uploads/D_M1_Spleen_Slide3_2019_02_11_14_43_47.txt', 'graphene_oxide', u'False')
# is now: (u'uploads/D_M1_Spleen_Slide3_2019_02_11_14_43_47.txt', u'graphene_oxide', u'False')
#         (u'uploads/D_M1_Spleen_Slide3_2019_02_11_14_43_47.txt', u'graphene_oxide', u'False')
# theyt're exactly the same so pwhat is the issue!!!