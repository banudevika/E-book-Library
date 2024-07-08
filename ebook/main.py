from flask import  Flask,render_template,request,redirect,url_for,jsonify
from flask_mysqldb import MySQL,MySQLdb
import os
import re
import random
app = Flask(__name__)


app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "ebook"
app.config['UPLOAD_FOLDER1'] = 'static/bookimages'
app.config['UPLOAD_FOLDER2'] = 'static/bookpdfs'

mysql = MySQL(app)

@app.route('/')
def base():
    return render_template('base.html')


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        Name = request.form['Name']
        Email = request.form['Email']
        Password = request.form['CPassword']
        Username = request.form['Username']

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO register (name, email, password, username) VALUES (%s, %s, %s, %s)",
                        (Name, Email, Password, Username))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('book'))
        except MySQLdb.IntegrityError as e:
            msg = str(e)
            if 'Duplicate entry' in msg:
                return render_template('registerpage.html', dmsg=True)
            else:
                return jsonify({'error': 'An error occurred while registering'}), 500
    return render_template('registerpage.html')




@app.route('/login',methods=['Get','POST'])
def login():
    if  request.method == 'POST':
        Email = request.form['Email']
        Password = request.form['Password']
        Username = request.form['Email']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM register WHERE email = %s OR username = %s", (Email,Username))
        user = cur.fetchone()
        cur.close()

        if user and user[2] != Password:
            return render_template('loginpage.html',eh = True)
        else:
            return redirect(url_for('book'))
    return render_template('loginpage.html')












@app.route('/addbook', methods=['GET', 'POST'])
def addbook():
    if request.method == 'POST':
        book_name = request.form['bookname']
        author_name = request.form['authorname']
        book_category = request.form['bookcategory']
        book_information = request.form['bookinformation']
        book_image = request.files['bookimage']
        book_file = request.files['bookfile']

        image_filename = None
        file_filename = None

        if book_image:
            image_filename = book_image.filename
            book_image.save(os.path.join(app.config['UPLOAD_FOLDER1'], image_filename))

        if book_file:
            file_filename = book_file.filename
            book_file.save(os.path.join(app.config['UPLOAD_FOLDER2'], file_filename))

        try:

            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO books (bookname, bookauthorname, bookcategory, bookcontent, bookimage, bookpdf) VALUES (%s, %s, %s, %s, %s, %s)",
                           (book_name, author_name, book_category, book_information, image_filename, file_filename))
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('book'))
        except MySQLdb.IntegrityError as e:
            msg = str(e)
            if 'Duplicate entry' in msg:
                return render_template('addbook.html', dmsg=True)
            else:
                return jsonify({'error': 'An error occurred while registering'}), 500

    return render_template('addbook.html')








@app.route('/book', methods=['GET'])
def book():
    query = request.args.get('query')
    selected_categories = request.args.getlist('category')
    cur = mysql.connection.cursor()

    if query:
        regex_query = re.escape(query)
        regex_pattern = f'.*{regex_query}.*'
        cur.execute("SELECT * FROM books WHERE bookname REGEXP %s OR bookauthorname REGEXP %s OR bookcategory REGEXP %s",
                    (regex_pattern, regex_pattern, regex_pattern))

    elif not selected_categories or 'all' in selected_categories:
        cur.execute("SELECT * FROM books")

    else:
        placeholders = ', '.join(['%s'] * len(selected_categories))
        querys1 = "SELECT * FROM books WHERE bookcategory IN (%s)" % placeholders
        cur.execute(querys1, selected_categories)

    bookdetails = cur.fetchall()
    cur.close()


    shuffled_books = list(bookdetails)
    random.shuffle(shuffled_books)

    return render_template('book.html', book=shuffled_books)




if __name__ == '__main__':
    app.run(debug=True)


