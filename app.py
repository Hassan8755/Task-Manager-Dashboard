from flask import Flask, request,render_template,redirect,url_for,session,flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired,  Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL



app = Flask(__name__)

# MySQL Configuration
app.config['SECRET_KEY'] = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tms_db'
app.secret_key = 'your_secret_key_here'


mysql = MySQL(app)




class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # mobile = MobileField('Mobile',validators=[DataRequired()])
    # confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('user_Register')

class LoginForm(FlaskForm):
    
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('user_Register')

@app.route('/')
def index():
    return render_template('index.html')





@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if 'register' in session:
        return redirect(url_for('user_login'))

    if request.method == 'POST':
        username = request.form['username']
        userEmail= request.form['user_email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        

        query = """
            INSERT INTO user ( name, email, password)
            VALUES (%s, %s, %s);
            """

        cursor.execute(query, ( username, userEmail, password))
        mysql.connection.commit()

        cursor.close()

        return redirect(url_for("userLogin"))
    else:
        return render_template('user/user_register.html')





@app.route('/user_login', methods = ['GET','POST'])
def userLogin():
    if request.method == "POST":
        userEmail = request.form["user_email"]
        password = request.form["password"]
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email=%s and password=%s and role=%s",(userEmail,password,'user'))
        user = cursor.fetchone()
         # Check if user exists
        if user:
            session["user"] = user 
            return redirect(url_for("user_dashboard"))
        else:
            return render_template('user/user_login.html',form=request.form)

    return render_template('user/user_login.html')


# USER CODE COMPLETE START

@app.route('/user_dashboard')
def user_dashboard():
    if session["user"]:
        
        userId = session.get("user")[0]
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT count(*) as count  FROM leave_application WHERE user_id=%s and status=%s", (userId,"Rejected"))
        rejectedCount = cursor.fetchone()[0]
       
        cursor.execute("SELECT count(*) as count  FROM leave_application WHERE user_id=%s and status=%s", (userId,"Accepted"))
        acceptedCount = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) as count  FROM leave_application WHERE user_id=%s ", (userId,))
        totalLeavesCount = cursor.fetchone()[0]



        cursor.execute("SELECT count(*) as count FROM task WHERE user_id=%s", (userId,))
        taskCount = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) as count  FROM task WHERE user_id=%s and status=%s", (userId,"completed"))
        completedTaskCount = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) as count  FROM task WHERE user_id=%s and status=%s", (userId,"pending"))
        pendingTaskCount = cursor.fetchone()[0]
        
   
        return render_template('user/user_dashboard.html',
        task_count=taskCount,completed_task_count=completedTaskCount, pending_task_count=pendingTaskCount,
         accepted_leave_count=acceptedCount, rejected_leave_count = rejectedCount,total_leaves_count = totalLeavesCount,  )
        cursor.close()
    
    else:
        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('user_login'))




# apply leave code
@app.route('/apply_leave', methods=['GET', 'POST'])

def apply_leave():

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT user_id, subject FROM leave_application WHERE status=%s", ('user',))
    applyList = cursor.fetchall()
   
    # cursor = mysql.connection.cursor()
    if request.method == 'POST':
        # user_id = request.form['id']
        subject = request.form['subject']
        message = request.form['message']
        leave_date = request.form['leave_date']
    
        # priority = request.form['priority']
        user_id = session.get("user")[0]

        query = """
            INSERT INTO leave_application ( subject, message, leave_date,user_id)
            VALUES (%s, %s, %s,%s);
            """

        cursor.execute(query, ( subject, message, leave_date,user_id))
        mysql.connection.commit()

        cursor.close()
        return redirect(url_for('leave_status'))

    return render_template('user/apply_leave.html',lists=applyList)

    # apply leave code end


    # leave_status code start

@app.route('/leave_status')
def leave_status():

    cursor = mysql.connection.cursor()
    userId = session.get("user")[0]

    cursor.execute("SELECT * FROM leave_application where user_id = '%s' order by id desc",(userId,))
    applicationlist = cursor.fetchall()
    cursor.close()
    return render_template('user/leave_status.html',leave_status=applicationlist)

# leave_status code end


    # task list code
@app.route('/task_list', methods=['GET'])
def get_tasks():
    cursor = mysql.connection.cursor()
    userId = session.get("user")[0]

    cursor.execute("SELECT * FROM task where user_id = '%s' order by id desc",(userId,))
    taskList = cursor.fetchall()
    cursor.close()
    return render_template('user/task_list.html',task = taskList)

     # task list code end

# update password code start
# @app.route('/update_password', methods=['GET', 'POST'])
# def update_password():
#     if request.method == 'POST':
#         current_password = request.form.get('current_password')
#         new_password = request.form.get('new_password')

#         user_id = session.get("user")[0]

#         if admin in session:
#             user_id = session.get("admin")[0]


        

#         flash("Password updated successfully!", "success")
#         return redirect(url_for('update_password'))

#     return render_template('/update_password.html')

    # update password code end





@app.route('/user_logout')
def user_logout():
    session.pop('user', None)
    return redirect(url_for('userLogin'))
# USER CODE COMPLETE END



# ADMIN CODE COMPLETE START

  # start admin login code
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'admin' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email=%s and password=%s and role=%s", (username, password, 'admin'))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['admin'] = user

            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            return render_template('admin/admin_login.html',form=request.form)
    else:
        return render_template('admin/admin_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin' in session:
     if session["admin"]:
        
        userId = session.get("user")[0]
        
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT count(*) as count  FROM leave_application WHERE user_id=%s and status=%s", (userId,"Rejected"))
        rejectedCount = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) as count  FROM leave_application WHERE user_id=%s and status=%s", (userId,"Accepted"))
        acceptedCount = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) as count  FROM leave_application WHERE user_id=%s ", (userId,))
        totalLeavesCount = cursor.fetchone()[0]



        cursor.execute("SELECT count(*) as count FROM task WHERE user_id=%s", (userId,))
        taskCount = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) as count  FROM task WHERE user_id=%s and status=%s", (userId,"completed"))
        completedTaskCount = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) as count  FROM task WHERE user_id=%s and status=%s", (userId,"pending"))
        pendingTaskCount = cursor.fetchone()[0]

        
        cursor.execute("SELECT count(*) as count FROM user")
        allUserCount = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) as count  FROM user WHERE role=%s", ("user",))
        userCount = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) as count  FROM user WHERE role=%s ", ("admin",))
        adminCount = cursor.fetchone()[0]






    
        
   
        return render_template('admin/admin_dashboard.html',
        task_count=taskCount,completed_task_count=completedTaskCount, pending_task_count=pendingTaskCount,
         accepted_leave_count=acceptedCount, rejected_leave_count = rejectedCount,total_leaves_count = totalLeavesCount,
         total_user_count=allUserCount, user_count=userCount,  admin_count = adminCount )
        # return render_template('admin/admin_dashboard.html')
    else:
        return redirect(url_for('admin_login'))


@app.route('/create_task', methods=['POST',"GET"])
def create_task():
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name FROM user WHERE role=%s", ('user',))
    usersList = cursor.fetchall()
    
    if request.method == 'POST':
        user_id = request.form['user_id']
        task_title = request.form['task_title']
        task_description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        # priority = request.form['priority']
        admin_id = session.get("admin")[0]

        query = """
            INSERT INTO task (created_by_id, user_id, task_title, description, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s);
            """

        cursor.execute(query, (admin_id, user_id, task_title, task_description, start_date, end_date))
        mysql.connection.commit()

        cursor.close()
        return redirect(url_for('manage_tasks'))
  
    cursor.close()
    return render_template('admin/create_task.html', users=usersList, name="aman")

# Helper function to find a task by ID
def find_task(task_id):
    return next((task for task in tasks if task["id"] == task_id), None)


# manage task code start
@app.route('/manage_task')
def manage_tasks():

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT task.*,user.name FROM user right join task on task.user_id=user.id order by id desc")
    taskList = cursor.fetchall()
    cursor.close()

    return render_template("admin/manage_task.html", task = taskList)
# manage task code end

# edit form code start 
@app.route('/edit', methods=['GET', 'POST'])
def edit_task():

    task_id = request.args.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM task where id= %s",(task_id,))
    task = cursor.fetchall()[0]
    cursor.close()

    if request.method == 'POST':
        # Get form data
        user_id = request.form['user_id']
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        cursor.execute("update task set user_id=%s, task_title=%s, description=%s, start_date=%s, end_date=%s;", ( user_id, task_title, task_description, start_date, end_date))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('manage_task'))

    return render_template('admin/edit_task.html',task_data = task)
    # edit form code end

    # delete_task code start

@app.route('/delete_task')
def delete_task():
    id = request.args.get('id')
    # new_status = request.args.get('status')
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM task WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('manage_tasks'))
# delete_task code end

# update task code start
@app.route('/update_task')
def update_task():
    id = request.args.get('id')
    new_status = request.args.get('status')
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE task SET status = %s WHERE id = %s', (new_status, id))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('get_tasks'))
# update task code end

#start view_leave
@app.route('/view_leave')
def view_leave():
    # cursor.execute("SELECT task.*,user.name FROM user right join task on task.user_id=user.id order by id desc")
    cursor = mysql.connection.cursor()
    # cursor.execute("SELECT * FROM leave_application order by id desc")
    cursor.execute("SELECT leave_application.*,user.name FROM user right join leave_application on leave_application.user_id=user.id order by id desc")
    applicationList = cursor.fetchall()
    cursor.close()

    return render_template('admin/view_leave.html',leaves=applicationList)

# update leave code start
@app.route('/update_leave')
def update_leave():
    id = request.args.get('id')
    new_status = request.args.get('status')
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', (new_status, id))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('view_leave'))
# update leave code end


    # user list code start
@app.route('/user_list')
def userList():

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user order by id desc")
 
    usersList = cursor.fetchall()
    cursor.close()

    return render_template('admin/user_list.html',users=usersList)
#  user list code end


# delete user code start
@app.route('/delete_user')
def delete_user():
    id = request.args.get('id')
    # new_status = request.args.get('status')
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM user WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('user_list'))

# delete user  end code

# edit user code start
@app.route("/edit_user", methods=['GET', 'POST'])
def edit_user():
   
    id = request.args.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user WHERE id=%s", (id,))
    user = cursor.fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # password = request.form['password']
        mobile = request.form['mobile']
        # priority = request.form['priority']
        # admin_id = session.get("admin")[0]


        cursor.execute("update user set name=%s, email=%s, mobile=%s where id =%s",( name, email, mobile,id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('userList'))
    
    return render_template("admin/edit_user.html",user_data=user)



   


# add user code start
@app.route("/Add_Users", methods=['GET', 'POST'])
def add_user():
   
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name,email,password,mobile FROM user WHERE role=%s", ('user',))
    usersList = cursor.fetchall()
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        mobile = request.form['mobile']
        # priority = request.form['priority']
        # admin_id = session.get("admin")[0]

        query = """
            INSERT INTO user ( name, email, password, mobile)
            VALUES (%s, %s, %s, %s);
            """

        cursor.execute(query, ( name, email, password, mobile))
        mysql.connection.commit()

        cursor.close()
        return redirect(url_for('userList'))
    
    return render_template("admin/add_user.html")

# add user code end


# Route: Logout
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


# ADMIN CODE COMPLETE END









if  __name__ == '__main__':
    app.run(debug=True)  




   

# @app.route('/add_task', methods=['POST'])
# def add_task():
#     new_id = max(task["id"] for task in tasks) + 1 if tasks else 1
#     tasks.append({
#         "id": new_id,
#         "title": request.form.get('title'),
#         "description": request.form.get('description'),
#         "status": "Pending",
#     })
#     return redirect(url_for('manage_tasks.html'))

# @app.route('/update_task/<int:task_id>', methods=['POST'])
# def update_task(task_id):
#     task = find_task(task_id)
#     if task:
#         task["title"] = request.form.get('title')
#         task["description"] = request.form.get('description')
#         task["status"] = request.form.get('status')
#     return redirect(url_for('manage_tasks'))

# @app.route('/delete_task/<int:task_id>')
# def delete_task(task_id):
#     global tasks
#     tasks = [task for task in tasks if task["id"] != task_id]
#     return redirect(url_for('manage_tasks'))


# update password code

# @app.route('/update_password', methods=['GET', 'POST'])
# def update_password():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         current_password = request.form.get('current_password')
#         new_password = request.form.get('new_password')

#         user = User.query.filter_by(username=username).first()

#         if not user:
#             flash("User not found!", "danger")
#             return redirect(url_for('update_password'))

#         if not check_password_hash(user.password_hash, current_password):
#             flash("Incorrect current password!", "danger")
#             return redirect(url_for('update_password'))

#         # Update password
#         user.password_hash = generate_password_hash(new_password)
#         db.session.commit()
#         flash("Password updated successfully!", "success")
#         return redirect(url_for('update_password'))

#     return render_template('user/update_password.html')


# update password end








# admin dashboard sidebar code task total

# @app.route('/admin/dashboard')
# @login_required
# def admin_dashboard():
#     total_users = User.query.count()
#     total_tasks = Task.query.count()
#     total_leave_applications = LeaveApplication.query.count()

#     return render_template('admin_dashboard.html', 
#                            total_users=total_users, 
#                            total_tasks=total_tasks, 
#                            total_leave_applications=total_leave_applications)




# Run the App





