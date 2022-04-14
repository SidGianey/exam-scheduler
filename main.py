# Siddharth Gianey

from flask import Flask, render_template, request, redirect, session, send_file
from flask.helpers import url_for
from flask.scaffold import F
from werkzeug.utils import secure_filename
from ics import Calendar, Event
import textract

app = Flask(__name__, template_folder='templates')

app.config['tmp'] = '/tmp/'
app.config['FILE_TYPES'] = ['PDF']
app.secret_key = "exam stuff"

def readFile(path):
  file = textract.process(path, encoding='ascii').decode()
  exams = file.split('\n')
  x = len(exams)//3
  for i in range(0, x):
    exams[i] = exams[i] +'\t'+ exams[i+x] +'\t'+ exams[i+x+x]
  for i in range(0,2*x+2):
    exams.pop()
  return exams

def isPDF(filename):
  if not '.' in filename:
    return False
  extention = filename.rsplit('.', 1)[1]
  if extention.upper() in app.config['FILE_TYPES']:
    return True
  return False

@app.route('/', methods=['GET', 'POST'])
def home():
  if request.method == 'POST':
    if request.files:
      file = request.files["file"]
      if file.filename == "":
        print("File must have a filename.")
        return render_template('upload.html', message="Error: The file needs a name.")
      if not isPDF(file.filename):
        print("File must be a PDF.")
        return render_template('upload.html', message="Error: The only accepted file type is PDF.") 
      filename = secure_filename(file.filename)
      file.save(app.config['tmp'] + filename)
      print("File saved")
      exams = readFile(app.config['tmp'] + filename)
      session['exams'] = exams
      return redirect(url_for('output', exams=exams))
  return render_template('upload.html', message="Please Upload a PDF")

@app.route('/output', methods=['GET', 'POST'])
def output():
  exams = request.args['exams']
  exams = session['exams']
  classes = []
  typeOfExam = []
  date = []
  size = len(exams)
  for i in range(0, size):
    temp = exams[i].split('\t')
    classes.append(temp[0])
    typeOfExam.append(temp[1])
    date.append(temp[2])
  if request.method == 'POST':
    cal = Calendar()
    for i in range(0, size):
      event = Event()
      event.name = classes[i] + '   ' + typeOfExam[i]
      temp = date[i].split('/')
      if(len(temp[0]) == 1):
        temp[0] = '0' + temp[0]
      if(len(temp[1]) == 1):
        temp[1] = '0' + temp[1]
      if(len(temp[2]) < 4):
        temp[2] = '20' + temp[2]
      event.begin = temp[2]+'-'+temp[0]+'-'+temp[1]+' 05:00:00'
      cal.events.add(event)
    name = app.config['tmp'] + 'ExamSchedule.ics'
    with open(name, 'w') as cal_download:
      cal_download.writelines(cal)
    return send_file(name, as_attachment=True)
  return render_template('output.html', classes=classes, typeOfExam=typeOfExam, date=date)
