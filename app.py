from flask import Flask, render_template, request,flash,get_flashed_messages,jsonify
from ultralytics import YOLO
import os
import pandas as pd
import cv2
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)
app.secret_key = b'filesystem'
model = YOLO('best.pt')

# Define the path for uploaded files
UPLOAD_FOLDER = 'runs/detect'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Read the COCO class list from a file
with open("coco.txt", "r") as my_file:
    class_list = my_file.read().split("\n")


@app.route('/home')
def home():
     return render_template('home.html')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/oilspill')
def oilspill():
    return render_template('oilspill.html')

@app.route('/methods')
def methods():
    return render_template('methods.html')
@app.route('/methods1')
def methods1():
    return render_template('methods1.html')
@app.route('/methods2')
def methods2():
    return render_template('methods2.html')
@app.route('/toregister')
def toregister():
    return render_template('register.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'id' in session:

        if request.method == 'POST':
            file = request.files['file']
            filename = file.filename
            file_path = f'static/images/{filename}'
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

            frame = cv2.imread(file_path)
            frame = cv2.resize(frame, (500, 500))

            results = model.predict(frame)
            detections = results[0].boxes.data
            px = pd.DataFrame(detections).astype("float")

            for index, row in px.iterrows():
                x1, y1, x2, y2, _, d = map(int, row)
                if d < len(class_list):
                    c = class_list[d]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)
            output_path = f'static/detections/{filename}'
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, frame)


            # Run YOLOv8 inference on the uploaded file
            # results = model.predict(filename, save=True, imgsz=320, conf=0.5, iou=0.7)

            # predicted_image_path = os.path.join('runs/detect/', os.path.basename(filename))
            
            # Pass the results to the results page
            return render_template('results.html', predicted_image=output_path)
        return "No file uploaded."
    else:
        # User is not authenticated, redirect to login page
        return render_template('registration/login.html')


app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Hitesh#0707'
app.config['MYSQL_DB'] = 'major_project'

mysql = MySQL(app)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                       (username, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Assuming the password is at index 2 (adjust as needed)
            hashed_password_from_db = user[3]

            if bcrypt.checkpw(password.encode('utf-8'), hashed_password_from_db.encode('utf-8')):
                session['id'] = user[0]  # Assuming the user ID is at index 0
                return redirect(url_for('home'))

    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        # Display user-specific content
        return "Welcome to the dashboard!"
    else:
        return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)


'''
from ultralytics import YOLO

# Load a pretrained YOLOv8 model
model = YOLO('best.pt')

results = model.predict('spill1.jpg', save=True, imgsz=320, conf=0.5, iou=0.7)
if results:
    print("First detection: ", results[0])
'''


