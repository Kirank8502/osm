from datetime import datetime
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.utils import ImageReader
from pathlib import Path
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'OSM'
mysql = MySQL(app)

UPLOAD_FOLDER = './static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['pdf'])

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/add/teacher')
def addteacher():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM teacher")
    data = cur.fetchall()
    cur.close()
    return render_template('addteacher.html', computers=data)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return "Login via the login Form"
    if request.method == 'POST':
        salutations = request.form['salutations']
        name = request.form['name']
        email = request.form['email']
        pswd = request.form['pswd']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO teacher (salutations,name,email, pswd) VALUES(%s,%s,%s,%s)''',
                       (salutations, name, email, pswd))
        mysql.connection.commit()
        flash("Teacher Added Successfully")
        return redirect(url_for('addteacher'))


@app.route('/update', methods=["POST"])
def update():
    id = request.form['id']
    salutations = request.form['salutations']
    name = request.form['name']
    email = request.form['email']
    pswd = request.form['pswd']
    cursor = mysql.connection.cursor()

    cursor.execute("""UPDATE teacher SET salutations=%s,name=%s, email=%s, pswd=%s WHERE id=%s""",
                   (salutations, name, email, pswd, id))
    mysql.connection.commit()

    flash("Teacher updated Successfully")
    
    return redirect(url_for('addteacher'))


@app.route('/delete/<id>')
def delete(id):
    # id = request.form['id']
    cursor = mysql.connection.cursor()
    cursor.execute("""DELETE FROM teacher where id=%s""", (id))
    mysql.connection.commit()
    flash("Teacher Deleted Successfully")
    return redirect(url_for('addteacher'))


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'admin' in request.form and 'pass' in request.form:
        username = request.form['admin']
        password = request.form['pass']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE name = %s AND pwd = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['name']
            return redirect('/admin/dashboard')
        else:
            return 'Incorrect username/password!'
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('dash.html')

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        teacher_name = request.form['teacher_name']
        email = request.form['teacher_email']
        password = request.form['pass']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM teacher WHERE name = %s AND email = %s AND pswd = %s', (teacher_name, email, password))
        account = cursor.fetchone()
        if account:
            session['teacher_loggedin'] = True
            session['id'] = account['id']
            session['teacher_name'] = account['name']
            return redirect('/teacher/dashboard')
        else:
            return 'Invalid username or password'
    return render_template('teacher_login.html')

@app.route('/teacher/dashboard', methods=['GET', 'POST'])
def teacherdashboard():
    if session.get('teacher_name') != None:
        var1 = session['teacher_name']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT subject,course,class_name,count(file_name) FROM assign WHERE name=%s GROUP BY subject",(var1,))
        data = cursor.fetchall()
        cursor.execute("SELECT file_name FROM assign where name=%s",(var1,))
        file_name = cursor.fetchall()
        cursor.close()
    else:
        data = ''
    return render_template('teacher_dash.html', data=data,file_name=file_name)

# @app.route('/select_paper/<subject>')
# def select_paper(subject):
#     if session.get('teacher_name') != None:
#         var2 = session['teacher_name']
#         cursor = mysql.connection.cursor()
#         cursor.execute("SELECT file_name FROM assign where name=%s",(var2,))
#         file_name = cursor.fetchall()
#     return redirect(url_for('teacherdashboard',file_name=file_name))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/dashboard/assign',methods=['GET', 'POST'])
def upload_file():
    cur = mysql.connection.cursor()
    now = datetime.now()
    cur.execute('SELECT name FROM teacher')
    teachers_name = cur.fetchall()
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                check_path = os.path.dirname(app.config['UPLOAD_FOLDER'])+ '/upload/' +filename
                check_path = check_path[1:]
                name = request.form['teacher_name']
                subject = request.form['subject']
                course = request.form['course']
                class_name = request.form['class_name']
                cur.execute("INSERT INTO assign (file_name,uploaded_on, name, subject, course, class_name) VALUES (%s, %s,%s, %s, %s, %s)", [check_path,now,name, subject,course, class_name])
                mysql.connection.commit()
            else:
                flash("File can't be uploaded")
                break
        cur.close()
    return render_template('assign.html',teacher_name = teachers_name)

@app.route("/teacher/paper")
def paper_check():
    if session.get('teacher_name') != None:
        var2 = session['teacher_name']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT file_name FROM assign WHERE name=%s",(var2,))
        path = cursor.fetchone()
        cursor.close()
        imgTemp = BytesIO()
        imgDoc = canvas.Canvas(imgTemp)
        c = canvas.Canvas("D:/web/osm-project-1/static/upload/AI_Index.pdf")
        reader = ImageReader("D:/web/osm-project-1/static/img/remove.png")
        imgDoc.drawImage(reader,80,400,250,250)
        imgDoc.save()
        c.setStrokeColorRGB(0.2, 0.5, 0.3)
        c.rect(10, 740, 100, 80, stroke=1, fill=0)
        c.save()
        # pdf_reader = PdfFileReader("D:/web/osm-project-1/static/upload/AI_Index.pdf","rb").getPage(0)
        # overlay = PdfFileReader(BytesIO(imgTemp.getvalue())).getPage(0)
        # pdf_reader.mergePage(overlay)
        # output = PdfFileWriter()
        # output.addPage(pdf_reader)
        # pdfOutput = open('output_file.pdf', 'wb')
        # output.write(pdfOutput)
        # pdfOutput.close()
        # pdf_writer = PdfFileWriter()
        # pdf_writer.appendPagesFromReader(pdf_reader)
        # pdf_writer.encrypt(user_pwd="abcd")
        # output_path = Path.home() / "top_secret_encrypted.pdf"
        # with output_path.open(mode="wb") as output_file:
        #     pdf_writer.write(output_file)
    return render_template("paper_check.html",path=path)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session['loggedin'] = False
    session.pop('username',None)
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.secret_key = 'admin1234'
    app.run(debug=True)
