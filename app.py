from flask import Flask, g, redirect, render_template, request, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename
from sqlalchemy import asc, desc
from pyffmpeg import FFmpeg
import os
app = Flask(__name__)
UPLOADS = "static/uploads/"
app.config['UPLOADS'] = UPLOADS
app.secret_key = "Roberto"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gyman.db'
db = SQLAlchemy(app)
admin = Admin(app,  name='gymonline', template_mode='bootstrap3')
EXTS = set(['png', 'jpg', 'jpeg'])
VIDS = set(['webm', 'mp4'])
ff = FFmpeg()

class User(db.Model):
    user_id = db.Column(db.Integer, nullable = False, primary_key = True)
    username = db.Column(db.String(20), nullable = False, unique = True)
    password = db.Column(db.String(50), nullable= False)
    confirm = db.Column(db.String(50), nullable= False)
    firstname = db.Column(db.String(50), nullable= False)
    lastname = db.Column(db.String(50), nullable= False)
    email = db.Column(db.String(50), nullable= False)
    phone = db.Column(db.String(50), nullable= False)
    gender = db.Column(db.String(10), nullable= False)
    age = db.Column(db.Integer, nullable= False)
    country = db.Column(db.String(50), nullable= False)
    joining_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    profile_image = db.Column(db.String(50), nullable = False, default = "none")
    profile = db.Column(db.Text)
    trainer = db.relationship('Trainer', backref = db.backref('Trainer'))
    member = db.relationship('Member', backref = db.backref('Member'))

    def __repr__(self) -> str:
        return '%r' % (self.firstname +  ' ' + self.lastname)

class Trainer(db.Model):
    trainer_id = db.Column(db.Integer, nullable = False, primary_key= True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    member_train = db.relationship('Member', backref = db.backref('Trainer'))
    image = db.relationship('Image',  backref = db.backref('Trainer'))
    diet = db.relationship('Diet')
    exercise = db.relationship('Exercise')
    schedule = db.relationship('Schedule')
    free_training = db.relationship('Free_training')
    def __repr__(self) -> str:
        return '<%r>' % (self.trainer_id)
class TrainerView(ModelView):
    form_columns = ['user_id']
    # column_list = ['user_id']
class Member(db.Model):
    member_id = db.Column(db.Integer, nullable = False, primary_key= True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'), nullable=True)
    diet = db.relationship('Diet')
    exercise = db.relationship('Exercise')
    schedule = db.relationship('Schedule')
# class MemberView(ModelView):
#     column_list = ['Member', 'trainer_id']
class Image(db.Model):
    image_id = db.Column(db.Integer, nullable=False, primary_key = True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    image_file = db.Column(db.String(50), nullable = False, default = 'N/A')
    caption = db.Column(db.Text)
    date_added = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
class Diet(db.Model):
    diet_id = db.Column(db.Integer, nullable=False, primary_key = True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.member_id'))
    diet_description = db.Column(db.Text, nullable = False, default = 'N/A')
    diet_file = db.Column(db.String(50), nullable = False, default = 'N/A')
    date_added = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
class Exercise(db.Model):
    exercise_id = db.Column(db.Integer, nullable=False, primary_key = True)
    exercise_name = db.Column(db.String(100), nullable = False, default = 'N/A')
    exercise_file = db.Column(db.String(50), nullable = False, default = 'N/A')
    exercise_link = db.Column(db.String(150), nullable = False, default = 'N/A')
    exercise_description = db.Column(db.Text, nullable = False, default = 'N/A')
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.member_id'))
    date_added = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

class Schedule(db.Model):
    schedule_id = db.Column(db.Integer, nullable=False, primary_key = True)
    schedule_date = db.Column(db.Date, nullable = False)
    schedule_time = db.Column(db.Time, nullable = False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.member_id'))
    date_added = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
class Free_training(db.Model):
    free_id = db.Column(db.Integer, nullable=False, primary_key = True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    free_caption = db.Column(db.String(50), nullable = False, default = 'N/A')
    free_thumbnail = db.Column(db.String(50), nullable = False, default = 'none')
    free_file = db.Column(db.String(50), nullable = False, default = 'N/A')
    free_link = db.Column(db.String(150), nullable = False, default = 'N/A')
    free_description = db.Column(db.Text, nullable = False, default = 'N/A')
    date_added = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
# db.create_all()
admin.add_view(ModelView(User, db.session))
admin.add_view(TrainerView(Trainer, db.session))
admin.add_view(ModelView(Exercise, db.session))
admin.add_view(ModelView(Member, db.session))
admin.add_view(ModelView(Image, db.session))
admin.add_view(ModelView(Free_training, db.session))
# admin.add_view(MemberView(Member, db.session))

# x = "member"
# admin = User(username = x, password = "newguy", confirm = "newguy", firstname = "Busayo", lastname = "Roberto", email = "newRobertoguy@gmail.com", phone = "0011110000", gender = "Male", age = 31, country = "Burundi")
# new_admin = Admin(user_id = 1)
# db.session.add(admin)
# db.session.commit()
# date = datetime.strptime('01062022', "%d%m%Y").date()
# timer  = time.fromisoformat("06:00:00")
# new_schedule = Schedule(schedule_date = date, schedule_time = timer)
# db.session.add(new_schedule)
# db.session.commit()
# schedule = Schedule.query.all()
# for sch in schedule:
#     print(sch.schedule_date)
#     print(sch.schedule_time)


# train_id = User.query.filter(User.username == x).with_entities(User.user_id)
# new_train = Member(user_id = train_id)
# db.session.add(new_train)
# db.session.commit()
# x = 1
# asks = Member.query.all()
# mem  = Member.query.filter(Member.member_id == x).first()
# mem.trainer_id = 1

# administrate = User(username = "admin", password = "victory12345", confirm = "victory12345", firstname = "Admin", lastname="Admin", email="admin@gmail.com", phone = "00000000", gender = "Male", age=25, country="Cyprus", profile = "I am the Admin") 
# db.session.add(administrate)
# db.session.commit()
# trainer = Trainer(user_id = 1)
# db.session.add(trainer)
# db.session.commit()
# member = Trainer.query.all()
# print(member)


# db.session.commit()
# for ask in asks:
#     print(ask.member_id)
#     print(ask.user_id)
#     print(ask.trainer_id)

# users =  User.query.filter_by(user_id = x).all()
# for user in users:
#     print(user.username)
#     print(user.firstname)
#     print(user.lastname)
#     print(user.country)
def files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTS
def vids(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in VIDS


@app.route('/image', methods = ['GET', 'POST'])
def image():
    free = Free_training.query.all()
    if request.method == 'POST':
        profile_image = request.files['profile_image']
        if 'profile_image' not in request.files:
            return redirect(request.url)
        if profile_image.filename == '':
            return redirect(request.url)
        if profile_image and files(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join(app.config['UPLOADS'], filename))
            return redirect('/')
        else:
            return redirect(request.url)
    return render_template('upload.html', free = free)
@app.route('/')
def home():
    page = request.args.get('page', 1, int)
    free = Free_training.query.paginate(page = page, per_page = 3)
    modal = Free_training.query.all()
    if 'hx_request' in request.headers:
        return render_template('free.html', free = free, modal=modal)
    return render_template("home.html", free = free, modal=modal)
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    filename = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        country = request.form['country']
        gender = request.form['gender']
        age = request.form['age']
        email = request.form['email']
        phone = request.form['phone']
        profile_image = request.files['profile_image']
        profile = request.form['profile']
        if profile_image and files(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join(app.config['UPLOADS'], filename))

        users = User.query.filter(User.username == username).all()
        if password == confirm:
            if not users:
                if filename != None:
                    new_user = User(username = username, password = password, confirm = confirm, firstname = firstname, lastname=lastname, email=email, phone = phone, gender = gender, age=age, country=country, profile_image = filename, profile = profile) 
                    db.session.add(new_user)
                    db.session.commit()
                else:
                    new_user = User(username = username, password = password, confirm = confirm, firstname = firstname, lastname=lastname, email=email, phone = phone, gender = gender, age=age, country=country) 
                    db.session.add(new_user)
                    db.session.commit()
                user_id = User.query.filter_by(username = username).with_entities(User.user_id)
                new_member = Member(user_id = user_id)
                db.session.add(new_member)
                db.session.commit()
                return redirect('/login')

            return redirect(request.url)
        else:
            return redirect(request.url)
    return render_template('signup.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if user and password == user.password:
            session.pop("loggedin", None)
            session.pop("trainer", None)
            id = user.user_id
            
            member = Member.query.filter_by(user_id = id).all()
            if member:
                session["loggedin"] = True
                return redirect(f'/member/{id}')
            else:
                session["loggedin"] = False
                session["trainer"] = True
                return redirect(f'/trainer/{id}')
        else:
            return redirect(request.url)

    return render_template('login.html')

@app.route('/member/<int:id>')
def member(id):
    member = Member.query.filter_by(user_id = id).all()
    x = 0
    w = 0
    for mem in member:
        x = mem.member_id
        if mem.trainer_id:
            y = mem.trainer_id
            z = Trainer.query.filter_by(trainer_id = y).all()
            for ze in z:
               w = ze.user_id 
    exercise = Exercise.query.filter(Exercise.member_id == x).all()
    trainer = User.query.filter_by(user_id = w).all()
    user = User.query.get_or_404(id)
    return render_template('member.html', user =user, member = member, exercise = exercise, trainer = trainer)

@app.route('/member/<int:id>/trainer')
def view_trainer(id):
    user = User.query.get_or_404(id)
    trainer = Trainer.query.all()
    mem = []
    for train in trainer:
        x = train.user_id  
        mem.append(x)
    search = request.args.get('search')
    page = request.args.get('page', 1, int)
    te = User.query.order_by(asc(User.firstname)).filter(User.user_id.in_(mem)).paginate(page = page, per_page = 6)
    if search:
        result = User.query.order_by(asc(User.firstname)).filter(User.user_id.in_(mem), (User.firstname.contains(search)| User.lastname.contains(search)| User.age.contains(search)| User.email.contains(search)| User.gender.contains(search))).paginate(page = page, per_page = 6) 
    else:
        result = te
    if 'hx_request' in request.headers:
        return render_template('searchresulttrain.html', user = user, result = result)
    return render_template('trainer.html', user = user, result = result)
@app.route('/member/<int:id>/trainer/<int:id2>/view')
def trainer_profile(id, id2):
    user = User.query.get_or_404(id)
    member = Member.query.filter_by(user_id = id).first()
    train = Trainer.query.filter_by(user_id = id2).all()
    page = request.args.get('page', 1, int)
    for tra in train:
        memb = Member.query.filter_by(trainer_id = tra.trainer_id).all()
        x = tra.trainer_id
    me = len(memb)
    images = Image.query.order_by(desc(Image.date_added)).filter_by(trainer_id = x).paginate(page = page, per_page = 2)
    img = Image.query.filter_by(trainer_id = x).all()
    img = len(img)
    
    teacher = User.query.get_or_404(id2)
    if 'hx_request' in request.headers:
        return render_template('trainerimagemember.html', user = user, teacher = teacher, member = member, memb = me, images = images, img = img)
    return render_template('trainer_profile.html', user = user, teacher = teacher, member = member, memb = me, images=images, img = img)
@app.route('/member/<int:id>/trainer/<int:id2>/add')
def add_trainer(id, id2):
    user = User.query.get_or_404(id)
    member = Member.query.filter_by(user_id = id).first()
    trainer = Trainer.query.filter_by(user_id = id2).first()
    if member and trainer:
        member.trainer_id = trainer.trainer_id
        db.session.commit()
        return redirect(f'/member/{user.user_id}')
    else:
        return redirect(request.url)
@app.route('/member/<int:id>/trainer/remove')
def rem_trainer(id):
    user = User.query.get_or_404(id)
    member = Member.query.filter_by(user_id = id).first()
    if member:
        member.trainer_id = None
        db.session.commit()
        return redirect(f'/member/{user.user_id}#trainer')
    else:
        return redirect(request.url)
@app.route('/member/<int:id>/profile')
def member_profile(id):
    user = User.query.get_or_404(id)
    member = Member.query.filter_by(user_id=id).all()
    x =0
    y =0
    usertrain = 'none'
    for mem in member:
        x = mem.trainer_id
    train_user = Trainer.query.filter_by(trainer_id = x).all()
    for train in train_user:
        y = train.user_id
    if y !=0:
        usertrain = User.query.get_or_404(y)
    return render_template('memberprofile.html', user=user, usertrain = usertrain)
@app.route('/member/<int:id>/profile/edit', methods=['GET', 'POST'])
def edit_member(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.firstname = request.form['firstname']
        user.lastname = request.form['lastname']
        user.country = request.form['country']
        user.age = request.form['age']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.profile = request.form['profile']
        if request.files['profile_image'].filename != '':
            if os.path.exists('static/uploads/' + user.profile_image):
                os.remove(os.path.join(app.config['UPLOADS'], user.profile_image))
            user.profile_image = request.files['profile_image']
            if files(user.profile_image.filename):
                filename = secure_filename(user.profile_image.filename)
                filename = f"__{id}_{filename}"
                user.profile_image.save(os.path.join(app.config['UPLOADS'], filename))
                user.profile_image = filename
                db.session.commit()
        else:
            db.session.commit()
        return redirect(f'/member/{user.user_id}/profile')
    return render_template('editmemprofile.html', user = user)
@app.route('/member/<int:id>/profile/image/delete', methods = ['GET', 'POST'])
def delete_profile_image(id):
    user = User.query.get_or_404(id)
    if os.path.exists('static/uploads/' + user.profile_image):
        os.remove(os.path.join(app.config['UPLOADS'], user.profile_image))
    user.profile_image = "none"
    db.session.commit()
    return redirect(f"/member/{user.user_id}/profile")

# TRAINER
@app.route('/trainer/<int:id>')
def trainer(id):
    trainer = User.query.get_or_404(id)
    train = Trainer.query.filter_by(user_id = id).all()
    members = []
    if train:
        for tra in train:
            memb = Member.query.filter_by(trainer_id = tra.trainer_id).all()
        for me in memb:
            w = me.user_id
            member = User.query.filter_by(user_id = w).all()
            members.append(member)
    members = members[0:4]
    return render_template('trainerhome.html', trainer = trainer, members = members)
@app.route('/trainer/<int:id>/member/<int:id2>/view')
def memberprofile(id, id2):
    user = User.query.get_or_404(id2)
    trainer = User.query.get_or_404(id)
    return render_template('memberprofile.html', user = user, trainer = trainer)
@app.route('/trainer/<int:id>/profile')
def trainerprofile(id):
    trainer = User.query.get_or_404(id)
    train = Trainer.query.filter_by(user_id = id).all()
    for tr in train:
        x = tr.trainer_id
    page = request.args.get('page', 1, int)
    images = Image.query.order_by(desc(Image.date_added)).filter_by(trainer_id = x).paginate(page = page, per_page = 2)
    img = Image.query.filter_by(trainer_id = x).all()
    img = len(img)
    for tr in train:
        memb = Member.query.filter_by(trainer_id = tr.trainer_id).all()
    if memb:
        me = len(memb)
    else:
        me = 0
    if 'hx_request' in request.headers:
        return render_template('trainerimageresult.html', memb = me, trainer = trainer, images = images, img = img)
    return render_template('trainerprofile.html', memb = me, trainer = trainer, images = images, img = img )

@app.route('/trainer/<int:id>/profile/edit',  methods=['GET', 'POST'])
def traineredit(id):
    trainer = User.query.get_or_404(id)
    if request.method == 'POST':
        trainer.profile = request.form['profile']
        if request.files['profile_image'].filename != '':
            if os.path.exists('static/uploads/' + trainer.profile_image):
                os.remove(os.path.join(app.config['UPLOADS'], trainer.profile_image))
            trainer.profile_image = request.files['profile_image']
            if files(trainer.profile_image.filename):
                filename = secure_filename(trainer.profile_image.filename)
                filename = f"__{id}_{filename}"
                trainer.profile_image.save(os.path.join(app.config['UPLOADS'], filename))
                trainer.profile_image = filename
                db.session.commit()
        else:
            db.session.commit()
        return redirect(f'/trainer/{trainer.user_id}/profile')
    return render_template('edittrainerprofile.html', trainer = trainer)

@app.route('/trainer/<int:id>/profile/image/delete',  methods=['GET', 'POST'])
def delete_trainer_pimage(id):
    trainer = User.query.get_or_404(id)
    if os.path.exists('static/uploads/' + trainer.profile_image):
        os.remove(os.path.join(app.config['UPLOADS'], trainer.profile_image))
    trainer.profile_image = "none"
    db.session.commit()
    return redirect(f"/trainer/{trainer.user_id}/profile")
@app.route('/trainer/<int:id>/members/view', methods = ['GET'])
def memberview(id):
    trainer = User.query.get_or_404(id)
    train = Trainer.query.filter_by(user_id = id).all()
    mem = []
    if train:
        for tra in train:
            memb = Member.query.filter_by(trainer_id = tra.trainer_id).all()
        for me in memb:
            w = me.user_id
            mem.append(w)
    page = request.args.get('page', 1, type=int)
    mv = User.query.order_by(asc(User.firstname)).filter(User.user_id.in_(mem)).paginate(page = page, per_page = 6)
    search = request.args.get('search')
    if search:
        result = User.query.order_by(asc(User.firstname)).filter(User.user_id.in_(mem), (User.firstname.contains(search)| User.lastname.contains(search)| User.age.contains(search)| User.email.contains(search)| User.gender.contains(search))).paginate(page = page, per_page = 6)
    else:
        result = mv
    if 'hx_request' in request.headers:
        return render_template('searchresult.html', trainer = trainer, result = result)
    return render_template('memberview.html', trainer = trainer, result = result)
@app.route('/trainer/<int:id>/image/upload', methods = ['GET', 'POST'])
def addimage(id):
    trainer = User.query.get_or_404(id)
    train = Trainer.query.filter(Trainer.user_id == id).all()
    for tr in train:
        x = tr.trainer_id
    if request.method == 'POST':
        caption = request.form['caption']
        if 'image' not in request.files:
            return redirect(request.url)
        image = request.files['image']
        if image.filename == '':
            return redirect(request.url)
        if image and files(image.filename):
            filename = secure_filename(image.filename)
            filename = f"__{x}_{filename}"
            image.save(os.path.join(app.config['UPLOADS'], filename))
            post = Image(trainer_id = x, image_file=filename, caption = caption)
            db.session.add(post)
            db.session.commit()
            return redirect(f"/trainer/{trainer.user_id}/profile")
        else:
            return redirect(request.url)
    return render_template('trainerimage.html', trainer = trainer)

@app.route('/trainer/<int:id>/image/<int:id2>/delete')
def delete_image(id, id2):
    trainer = User.query.get_or_404(id)
    image = Image.query.get_or_404(id2)
    if image:
        if os.path.exists('static/uploads/'+ image.image_file):
            os.remove(os.path.join(app.config['UPLOADS'], image.image_file))
        db.session.delete(image)
        db.session.commit()
    else:
        abort(404)
    return redirect(f'/trainer/{trainer.user_id}/profile')
@app.route('/trainer/<int:id>/freevideo/upload', methods = ['POST','GET'])
def free_upload(id):
    trainer = User.query.get_or_404(id)
    train = Trainer.query.filter_by(user_id = id).all()
    for tr in train:
        w = tr.trainer_id
    if request.method == 'POST':
        video_file = request.files['video_file']
        link = request.form['link']
        caption = request.form['caption']
        description = request.form['description']

        
        if video_file and vids(video_file.filename):
            filename = secure_filename(video_file.filename)
            filename = f"f{id}_{filename}"
            video_file.save(os.path.join(app.config['UPLOADS'], filename))
            thumbnail = filename.split('.')
            y = len(thumbnail) -1
            thumbnail[y] = "jpg"
            new = '.'.join(thumbnail)
            thumbnail[y] = ""
            new_db = ''.join(thumbnail)
            ff.convert(os.path.join(app.config['UPLOADS'], filename),os.path.join(app.config['UPLOADS'], new))
            new_vid = Free_training(trainer_id = w, free_file = filename, free_caption = caption, free_description = description, free_thumbnail = new_db)
            db.session.add(new_vid)
            db.session.commit()
            return redirect(request.url)
        else:
            link_id = link.split('/')[-1]
            new_vid = Free_training(trainer_id = w, free_link = link_id, free_caption = caption, free_description = description, free_thumbnail = link_id)
            db.session.add(new_vid)
            db.session.commit() 
            return redirect(request.url)
    return render_template('freevideo.html', trainer = trainer)
# link = "https://www.youtube.com/embed/-237OttBIBE"
# linklist = link.split("/")
# print(linklist)
# if "embed" in linklist:
#     print('yes')
# else:
#     print('no')

# free = Free_training.query.all()
# for fr in free:
#     db.session.delete(fr)
#     db.session.commit()


# img = User.query.filter_by(user_id = 7).all()
# print(img)
# for im in img:
#     print(im.profile_image)
#     if im:
#         print(im.image_file)
#     else:
#         print("None")
#     db.session.delete(im)
#     db.session.commit()
# x = "static/uploads/3.Pexels_Videos_2759484.mp4"
# thumbnail = x.split('.')
# y = len(thumbnail) -1
# thumbnail[y] = "jpg"
# new = '.'.join(thumbnail)
# print(new)

# y = "static/uploads/3.Pexels_Videos_2759484.jpg"
# print(FFmpeg().convert(x,new))


if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port=80)