from flask import Flask, render_template, request, json, Response, redirect, url_for, send_file, session
from flask_dropzone import Dropzone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from zipfile import ZipFile, ZipInfo
from io import BytesIO
from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config
import oe_translation, datetime, uuid

app = Flask(__name__)
dropzone = Dropzone(app)
app.secret_key = config("SECRET_KEY")


app.config.update(
  upload_folder = "tmp",
  DROPZONE_MAX_FILE_SIZE = 1, # mb
  # DROPZONE_TIMEOUT = 60*1000, # ms
  DROPZONE_MAX_FILES = 50,
  DROPZONE_PARALLEL_UPLOADS = 50,
  DROPZONE_ALLOWED_FILE_CUSTOM = True,
  DROPZONE_ALLOWED_FILE_TYPE = '.json',
  DROPZONE_UPLOAD_MULTIPLE = True,
  DROPZONE_REDIRECT_VIEW = 'download',
  SQLALCHEMY_DATABASE_URI = 'sqlite:///temporary.db',
  UPLOAD_FOLDER = 'tmp'
)

db = SQLAlchemy(app)
app.app_context().push()

class LogEntry(db.Model):
  __tablename__ = 'log_entries'

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  text = db.Column(db.String())
  filename = db.Column(db.String())
  timestamp = db.Column(db.Integer, default=lambda: datetime.datetime.now(datetime.UTC))
  
  @classmethod
  def delete_expired(cls):
    expiration_minutes = 5
    limit = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=expiration_minutes)
    cls.query.filter(cls.timestamp <= limit).delete()
    db.session.commit()      

def delete_expired_logs():
  app.app_context().push()
  LogEntry.delete_expired()
    
    
@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')
  
@app.route('/download/', methods=['GET'])
def download():
  if request.method == 'GET':
    if session['tlist']:
      files = {}
      tlist = session['tlist']

      for i in tlist:
        row = db.session.get(LogEntry, i)
        try:
          files[row.filename] = row.id
        except:
          return redirect(url_for('index'))
      return render_template('download.html', files=files)

    return render_template("index.html")

@app.route('/sendfile/<value>', methods=['GET'])
def sendfile(value):
  if request.method == 'GET':
    value = uuid.UUID(value)
    try:
      row = db.session.get(LogEntry, value)
      callback = send_file(BytesIO(row.text.encode()), as_attachment=True, download_name=f"visualizer_{row.filename}" )
      return callback, 200
    except:
      return redirect(url_for('expired'))
    
@app.route('/expired', methods=['GET'])
def expired():
  if request.method == 'GET':
    return render_template('expired.html')

@app.route('/sendzip', methods=['GET'])
def sendzip():
  if request.method == 'GET':
    try:
      tlist = session['tlist']
      archive = BytesIO()
      zip_archive = ZipFile(archive, 'w')
      for value in tlist:
        row = db.session.get(LogEntry, value)
        file1 = ZipInfo(f'visualizer_{row.filename}')
        zip_archive.writestr(file1, row.text.encode())
          
      zip_archive.close()
      archive.seek(0)
      callback = send_file(archive, as_attachment=True, download_name=f"visualizer_json.zip" )
      
      return callback, 200
    except:
      return render_template('expired.html')
    
@app.route('/process', methods=['POST'])
def process():
  if request.method == 'POST':
    tlist = []
    for f in request.files:
      flag = False
      f = request.files.get(f)
      r = f.read().decode("utf-8")
      try:
        parsed_json = json.loads(r)
      except:
        print(f'{f} not a valid JSON file')
        continue
      for i in ['name', 'date', 'dosage', 'brewTemp']:
        if i not in parsed_json:
          print(f'{f} not a valid OE JSON file')
          flag = True
          break
      if flag:
        continue
      
      translated = json.dumps(oe_translation.main(parsed_json))
      new_entry = LogEntry(text=translated, filename=f.filename)
      try:
        db.session.add(new_entry)
        db.session.commit()
        tlist.append(new_entry.id)
      except:
        print('failed')
    session['tlist'] = tlist
    print(tlist)
    return 'OK'

sched = BackgroundScheduler(daemon=True)
sched.add_job(delete_expired_logs,'interval', seconds=30)
sched.start()

if __name__ == "__main__":
  app.run()
  