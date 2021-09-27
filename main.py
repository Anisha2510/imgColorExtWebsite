import os

from flask import Flask, render_template, request, url_for
import datetime
import numpy as np
import cv2
import pandas as pd

from werkzeug.utils import secure_filename, redirect

UPLOAD_FOLDER = 'static/Uploads'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('static/colors.csv', names=index, header=None)
csv.head()


def getColorName(R, G, B):
    minimum = 10000
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if (d <= minimum):
            minimum = d
            cname = csv.loc[i, "color_name"]
            hexCode = csv.loc[i, "hex"]
    return cname, hexCode


def asvoid(arr):
    arr = np.ascontiguousarray(arr)
    return arr.view(np.dtype((np.void, arr.dtype.itemsize * arr.shape[-1])))


def palette(image):
    arr = np.asarray(image)
    pal, idx = np.unique(asvoid(arr).ravel(), return_inverse=True)
    pal = pal.view(arr.dtype).reshape(-1, arr.shape[-1])
    count = np.bincount(idx)
    order = np.argsort(count)
    return pal[order[::-1]]


@app.route("/", )
def home():
    date = datetime.datetime.now().year

    return render_template("index.html", year=date)


@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='Uploads/' + filename))


@app.route('/colour', methods=['POST'])
def colours():
    if request.method == 'POST':
        file = request.files['file']
        # print(request.files)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print(filename)
        image = cv2.imread('static/Uploads/' + filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (1200, 600))
        colours = palette(image)[:20]

        color_arr = []
        color_hex = []
        for j in range(len(colours)):
            R = colours[j][0]
            G = colours[j][1]
            B = colours[j][2]
            color, hex = getColorName(R, G, B)
            color_arr.append([color,hex])
            # color_hex.append(hex)
        new_color = []
        url_set = set()

        for item in color_arr:
            if item[0] not in url_set:
                url_set.add(item[0])
                new_color.append(item)
            else:
                pass

        # color_hex = list(set(color_hex))
        length = len(new_color)
        return render_template('colours.html', filename=filename, colors=new_color, l=length)


if __name__ == '__main__':
    app.run()
