# from flask import Flask, jsonify, request, make_response
from flask import *
from flask_cors import CORS
import os

import numpy as np

import subprocess
import urllib

import caffe
import cv2
import json

caffe_root = "/Users/nishanksingla/Downloads/caffe/"
model = "FaceRecognition/vgg_face_deploy.prototxt"
weights = "FaceRecognition/face_recog_iter_4000.caffemodel"
mean_file = "FaceRecognition/train_mean.binaryproto"
image_file = "FaceRecognition/me1.jpg"
synset_file = "FaceRecognition/synset_FR.txt"

# def initialize_model():
net = caffe.Net(caffe_root+model,caffe_root+weights,caffe.TEST)

transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})

#converting binaryproto into mean npy
data=open(caffe_root+mean_file,'rb').read()
blob=caffe.proto.caffe_pb2.BlobProto()
blob.ParseFromString(data)
mean=np.array(caffe.io.blobproto_to_array(blob))[0,:,:,:]

#caffe.set_mode_gpu()

#image transformation
transformer.set_mean('data',mean.mean(1).mean(1)) # mean is set
transformer.set_raw_scale('data', 255) # normalizes the values in the image based on the 0-255 range
transformer.set_transpose('data', (2,0,1)) # transform an image from (256,256,3) to (3,256,256).

label_mapping = np.loadtxt(caffe_root+synset_file, str, delimiter='\t')

def detect_face(image_name):
    img = cv2.imread(image_name)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  
    faces = face_cascade.detectMultiScale(gray, 1.4, 3, minSize=(200, 200))

    if len(faces)==0:
        return {"error":"No face detected. Please try other image."}
    print "number of faces detected: "
    print len(faces)
    for index,face in enumerate(faces):
        x,y,w,h = face
        #drawing rectangle
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        cv2.imwrite( "static/images/" + "detected_" +str(index) +"_"+ image_name,img)

        detected_face = img[y:y+h, x:x+w]
        print "Detected face shape"
        print detected_face.shape  
    # print detect_face.dtype
    return detected_face

def recognize_face(image_name):
    detected_face = detect_face(image_name)
    
    if type(detect_face) == dict:
        return jsonify(detect_face)
    
    transformed_image = transformer.preprocess('data', detected_face)
    net.blobs['data'].data[...] = transformed_image
    output = net.forward()
    output_prob = output['prob'][0]

    print "output probability: "
    print output_prob

    #predicted class
    predicted_class = output_prob.argmax()
    accuracy = output_prob[predicted_class]
    print '\n Predicted class is:', predicted_class
    print "Accuracy:"
    print accuracy
    #getting name of the user

    user_recognized = label_mapping[predicted_class]
    print "Recognized user: " + user_recognized

    return {"predicted_class":predicted_class,"accuracy":str(accuracy),"recognized_user":user_recognized,"image":"detected_" + image_name}

app = Flask(__name__,static_url_path='')
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognizeByUrl', methods=['POST'])
def recognizeByUrl():
    # print("web url:")
    # print "REQUEST:"
    # print request.form
    # print "JSON"
    print request.get_json()
    # postData = request.get_json()
    # json.load
    url = request.get_json()["image_url"]
    # print "test----"
    # print "web url:" + url

    imageName = url.split("/")[-1]
    imageFormat = imageName.split(".")[-1]

    if imageFormat not in ["jpg","png","jpeg"]:
        return jsonify({"error":"Image Format not supported. Please try .jpg, .png & .jpeg format"})
    
    urllib.urlretrieve(url, imageName)
    output = recognize_face(imageName)

    # resp = make_response(json.dumps(["true", 0]))
    return jsonify(output)

@app.route('/recognizeByImage', methods=['POST'])
def recognizeByImage():
    image = request.files['file']
    f.save("uploadImage.jpg")
    filename ="uploadImage.jpg"
    output = recognize_face("urlImage.jpg")

    # resp = make_response(json.dumps(["true", 0]))
    return jsonify(output) 

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == '__main__':
    print("environment LD_LIBRARY_PATH:")
    print os.environ.get("LD_LIBRARY_PATH")
    if os.environ.get("LD_LIBRARY_PATH")==None:
	    os.environ['LD_LIBRARY_PATH'] = "/usr/local/cuda/lib64"
    print("environment LD_LIBRARY_PATH AFTER:")
    print os.environ.get("LD_LIBRARY_PATH")
    # initialize_model()
    #OpenCV
    face_cascade = cv2.CascadeClassifier("/usr/local/Cellar/opencv3/3.2.0/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml")    
    app.run(debug=True,host='0.0.0.0')
