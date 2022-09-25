from app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from itertools import combinations
import io
from PIL import Image
import base64
from blur_helper import *
import os
import shutil
import numpy
from collections import Counter

ALLOWED_EXTENSIONS = set(['jpg'])
filename = ""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/blur', methods=['POST'])
def upload_image():
    global filename
    images = []
    for file in request.files.getlist("file[]"):
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = filename
            filestr = file.read()
            npimg = np.frombuffer(filestr, np.uint8)
            image = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
            ratio = image.shape[0] / 500.0
            orig = image.copy()
            image = Helpers.resize(image, height=500)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            fm = cv2.Laplacian(gray, cv2.CV_64F).var()
            result = "Not Blurry"
            if fm < 140:
                result = "Blurry"
            sharpness_value = "{:.0f}".format(fm)
            message = [result, sharpness_value]
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            file_object = io.BytesIO()
            img = Image.fromarray(Helpers.resize(img, width=500))
            img.save(file_object, 'PNG')
            base64img = "data:image/png;base64," + base64.b64encode(file_object.getvalue()).decode('ascii')
            images.append([message, base64img])
            if fm >140:
                img.save(filename, 'JPEG')
                dest_path = "/Users/Ariv/PycharmProjects/duplicate and blur detection/non_blur images"
                for images1 in os.listdir("/Users/Ariv/PycharmProjects/duplicate and blur detection"):
                    if (images1.endswith(".jpg")):
                        src_path = "/Users/Ariv/PycharmProjects/duplicate and blur detection/" + filename
                        shutil.move(src_path, dest_path)
    return render_template('upload.html', images=images)

@app.route('/remove', methods = ['POST'])
def duplicate_detection():
    global filename
    list_names = []
    file_name = []
    list_combinations = []
    copies = []
    different = []
    final = []
    def orb_sim(img1, img2):
        orb = cv2.ORB_create()
        kp_a, desc_a = orb.detectAndCompute(img1, None)
        kp_b, desc_b = orb.detectAndCompute(img2, None)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(desc_a, desc_b)
        similar_regions = [i for i in matches if i.distance < 50]
        if len(matches) == 0:
            return 0
        return len(similar_regions) / len(matches)
    for picture in os.listdir("/Users/Ariv/PycharmProjects/duplicate and blur detection/non_blur images"):
        file_name.append(picture)
        picture = cv2.imread("/Users/Ariv/PycharmProjects/duplicate and blur detection/non_blur images/" + picture,0)
        list_names.append(picture)
    for n in range(len(list_names) + 1):
        list_combinations += list(combinations(list_names, n))
    filtered_list = [tup for tup in list_combinations if len(tup) == 2]
    filtered_list = [list(ele) for ele in filtered_list]
    flat_list = [item for sublist in filtered_list for item in sublist]
    print(flat_list)
    for i in range(0, len(flat_list), 2):
        if orb_sim(flat_list[i], flat_list[i+1])>0.7:
            copies.append(flat_list[i])
            copies.append(flat_list[i + 1])
        else:
            different.append(flat_list[i])
            different.append(flat_list[i + 1])
    print(copies[0])
    print(different)
    # unique, counts = numpy.unique(different, return_counts=True)
    # data = dict(zip(unique, counts))
    # print(data)
    # different1 = [k for k, v in data.items() if v == max(data.values())]
    # print(different1)
    # if len(different) == 1:
    #     final.append(different[0])
    #     final.append(copies[0])
    # else:
    #     for item in different:
    #         final.append(item)
    #         final.append(copies[0])
    #         break
    # for item in final:
    #     pass
        # array = np.reshape(item, (1024, 720))
        # data = Image.fromarray(array)
        # os.chdir("/Users/Ariv/PycharmProjects/duplicate and blur detection/non_duplicate images")
        # data.save('gfg_dummy_pic.jpg')
    #print(final)
    return render_template('upload.html')


if __name__ == "__main__":
    app.run(debug=True)