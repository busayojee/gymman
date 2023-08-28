import functools
from flask import Flask, g, redirect, render_template, request, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename
from sqlalchemy import asc, desc
from sqlalchemy.orm import aliased
from pyffmpeg import FFmpeg
import os
import smtplib
from smtplib import SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# help(smtplib)


app = Flask(__name__)
UPLOADS = "static/uploads/"
app.config['UPLOADS'] = UPLOADS
app.secret_key = "Roberto"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gyman.db'
db = SQLAlchemy(app)
admin = Admin(app,  name='Victory Gym', template_mode='bootstrap3')
EXTS = set(['png', 'jpg', 'jpeg'])
VIDS = set(['webm', 'mp4', 'mov'])
ff = FFmpeg()


class User(db.Model):
    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    confirm = db.Column(db.String(50), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(50), nullable=False)
    joining_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    profile_image = db.Column(db.String(50), nullable=False, default="none")
    profile = db.Column(db.Text)
    trainer = db.relationship('Trainer', backref=db.backref('Trainer'))
    member = db.relationship('Member', backref=db.backref('Member'))

    def __repr__(self) -> str:
        return '%r' % (self.firstname + ' ' + self.lastname)


class Trainer(db.Model):
    trainer_id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    member_train = db.relationship('Member', backref=db.backref('Trainer'))
    image = db.relationship('Image',  backref=db.backref('Trainer'))
    diet = db.relationship('Diet', backref=db.backref('Diettrainer'))
    exercise = db.relationship(
        'Exercise', backref=db.backref('Exercisetrainer'))
    schedule = db.relationship(
        'Schedule', backref=db.backref('Scheduletrainer'))
    free_training = db.relationship('Free_training')

    def __repr__(self) -> str:
        return '<%r>' % (self.trainer_id)


class TrainerView(ModelView):
    form_columns = ['user_id']
    # column_list = ['user_id']


class Member(db.Model):
    member_id = db.Column(db.Integer, nullable=False, primary_key=True)
    status = db.Column(db.String(10), nullable=False, default="not active")
    date_active = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    trainer_id = db.Column(db.Integer, db.ForeignKey(
        'trainer.trainer_id'), nullable=True)
    diet = db.relationship('Diet', backref=db.backref('Dietmember'))
    exercise = db.relationship(
        'Exercise', backref=db.backref('Exercisemember'))
    schedule = db.relationship(
        'Schedule', backref=db.backref('Schedulemember'))

    def __repr__(self) -> str:
        return '<%r>' % (self.member_id)
# class MemberView(ModelView):
#     column_list = ['Member', 'trainer_id']


class Image(db.Model):
    image_id = db.Column(db.Integer, nullable=False, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    image_file = db.Column(db.String(50), nullable=False, default='N/A')
    caption = db.Column(db.Text)
    date_added = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)


class Diet(db.Model):
    diet_id = db.Column(db.Integer, nullable=False, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.member_id'))
    diet_description = db.Column(db.Text, nullable=False, default='N/A')
    diet_name = db.Column(db.String(200), nullable=False, default='N/A')
    diet_file = db.Column(db.String(50), nullable=False, default='N/A')
    start_date = db.Column(db.Date, nullable=False, default='N/A')
    end_date = db.Column(db.Date, nullable=False, default='N/A')
    date_added = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)


class Exercise(db.Model):
    exercise_id = db.Column(db.Integer, nullable=False, primary_key=True)
    exercise_name = db.Column(db.String(100), nullable=False, default='N/A')
    exercise_file = db.Column(db.String(50), nullable=False, default='N/A')
    exercise_link = db.Column(db.String(150), nullable=False, default='N/A')
    exercise_description = db.Column(db.Text, nullable=False, default='N/A')
    exercise_thumbnail = db.Column(
        db.String(50), nullable=False, default='none')
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.member_id'))
    date_added = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)


class Schedule(db.Model):
    schedule_id = db.Column(db.Integer, nullable=False, primary_key=True)
    schedule_date = db.Column(db.Date, nullable=False)
    schedule_time = db.Column(db.Time, nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.member_id'))
    date_added = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)


class Free_training(db.Model):
    free_id = db.Column(db.Integer, nullable=False, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'))
    free_caption = db.Column(db.String(50), nullable=False, default='N/A')
    free_thumbnail = db.Column(db.String(50), nullable=False, default='none')
    free_file = db.Column(db.String(50), nullable=False, default='N/A')
    free_link = db.Column(db.String(150), nullable=False, default='N/A')
    free_description = db.Column(db.Text, nullable=False, default='N/A')
    date_added = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)


# db.create_all()
admin.add_view(ModelView(User, db.session))
admin.add_view(TrainerView(Trainer, db.session))
admin.add_view(ModelView(Member, db.session))
admin.add_view(ModelView(Exercise, db.session))
admin.add_view(ModelView(Schedule, db.session))
admin.add_view(ModelView(Diet, db.session))
admin.add_view(ModelView(Image, db.session))
admin.add_view(ModelView(Free_training, db.session))
# admin.add_view(MemberView(Member, db.session))


def login_requiredM(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'loggedin' in session:
            return f(*args, **kwargs)
        else:
            flash("Login required", "danger")
            return redirect('/login')
    return wrapper


def login_requiredT(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'trainer' in session:
            return f(*args, **kwargs)
        else:
            flash("Login required", "danger")
            return redirect('/login')
    return wrapper


def files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTS


def vids(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in VIDS


@app.route('/image', methods=['GET', 'POST'])
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
    return render_template('upload.html', free=free)

# !!!!!!!!!!!!!!!!!!!!!! Check if the user is in session before returning home/ First pop the sessions!!!!!!!!!!!!!!!!!!!


@app.route('/')
def home():
    train = Trainer.query.all()
    t = {}
    for tr in train:
        memb = Member.query.filter_by(trainer_id=tr.trainer_id).all()
        t[tr.trainer_id] = len(memb)
    t = sorted(t.items(), key=lambda x: x[1], reverse=True)
    t = dict(t[:3])
    k = []
    for keys, values in t.items():
        trained = Trainer.query.filter_by(trainer_id=keys).join(User, User.user_id == Trainer.user_id).add_columns(
            User.firstname, User.lastname, User.profile, User.profile_image, User.user_id).first()
        k.append(trained)
    page = request.args.get('page', 1, int)
    free = Free_training.query.order_by(
        desc(Free_training.date_added)).paginate(page=page, per_page=3)
    modal = Free_training.query.join(Trainer, Free_training.trainer_id == Trainer.trainer_id).join(User, Trainer.user_id == User.user_id).add_columns(
        Free_training.free_thumbnail, Free_training.date_added, Free_training.free_caption, Free_training.free_description, Free_training.free_file, Free_training.free_link, User.firstname, User.lastname).all()
    if 'hx_request' in request.headers:
        return render_template('free.html', free=free, modal=modal, k=k)
    return render_template("home.html", free=free, modal=modal, k=k)


@app.route('/signup', methods=['GET', 'POST'])
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
                    new_user = User(username=username, password=password, confirm=confirm, firstname=firstname, lastname=lastname,
                                    email=email, phone=phone, gender=gender, age=age, country=country, profile_image=filename, profile=profile)
                    db.session.add(new_user)
                    db.session.commit()
                else:
                    new_user = User(username=username, password=password, confirm=confirm, firstname=firstname,
                                    lastname=lastname, email=email, phone=phone, gender=gender, age=age, country=country)
                    db.session.add(new_user)
                    db.session.commit()
                user_id = User.query.filter_by(
                    username=username).with_entities(User.user_id)
                new_member = Member(user_id=user_id)
                db.session.add(new_member)
                db.session.commit()
                return redirect('/login')
            flash("Username already exists", "danger")
            return redirect(request.url)
        else:
            flash("Password should be same as confirm", "danger")
            return redirect(request.url)
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and password == user.password:
            session.pop("loggedin", None)
            session.pop("trainer", None)
            id = user.user_id

            member = Member.query.filter_by(user_id=id).all()
            if member:
                session["loggedin"] = True
                flash(f"Hello {user.firstname}", "success")
                return redirect(f'/member/{id}')
            else:
                session.pop("loggedin", None)
                session["trainer"] = True
                flash(f"Hello {user.firstname}", "success")
                return redirect(f'/trainer/{id}')
        else:
            flash("Invalid Login", "danger")
            return redirect(request.url)

    return render_template('login.html')


@app.route('/logout')
def logout():
    print(session)
    session.pop("trainer", None)
    session.pop("loggedin", None)
    flash("You're logged out", "primary")
    return redirect('/')


@app.route('/member/<int:id>')
@login_requiredM
def member(id):
    user = User.query.get_or_404(id)
    user1 = aliased(User)
    user2 = aliased(User)
    today = date.today()
    d = datetime.now()
    # g = datetime.now() + timedelta(days=30)
    member = Member.query.filter_by(user_id=id).first()
    if member.date_active:
        if d > member.date_active + timedelta(days=30):
            member.status = 'not active'
            db.session.commit()
            flash("subscription expired", "primary")
    z = Trainer.query.filter_by(trainer_id=member.trainer_id).first()
    data = Schedule.query.filter_by(member_id=member.member_id).order_by(
        Schedule.schedule_date).filter(Schedule.schedule_date >= today).limit(2).all()
    page = request.args.get('page', 1, int)
    exercise = Exercise.query.filter(Exercise.member_id == member.member_id).order_by(
        desc(Exercise.date_added)).paginate(page=page, per_page=3)
    modal = Exercise.query.filter_by(member_id=member.member_id).join(Member, Member.member_id == Exercise.member_id).join(Trainer, Exercise.trainer_id == Trainer.trainer_id).join(user1, Member.user_id == user1.user_id).join(user2, Trainer.user_id == user2.user_id).add_columns(
        Exercise.exercise_id, Exercise.exercise_name, Exercise.exercise_description, Exercise.exercise_file, Exercise.exercise_link, Exercise.exercise_thumbnail, Exercise.date_added, Member.member_id, Trainer.trainer_id, user1.firstname, user1.lastname, user2.firstname.label('tfirst'), user2.lastname.label('tlast')).all()
    if z:
        trainer = User.query.filter_by(user_id=z.user_id).all()
    else:
        trainer = None
    diet = Diet.query.filter_by(member_id=member.member_id).order_by(
        desc(Diet.date_added)).paginate(page=page, per_page=3)
    modals = Diet.query.filter_by(member_id=member.member_id).join(Trainer, Trainer.trainer_id == Diet.trainer_id).join(Member, Member.member_id == Diet.member_id).join(user1, user1.user_id == Trainer.user_id).join(user2, user2.user_id == Member.user_id).add_columns(
        Diet.diet_id, Diet.diet_description, Diet.diet_name, Diet.diet_file, Diet.start_date, Diet.end_date, Diet.date_added, user1.firstname, user1.lastname, user2.firstname.label('mfirst'), user2.lastname.label('mlast')).all()

    if 'hx_request' in request.headers:
        return render_template('memberpartial.html', user=user, mem=member, free=exercise, trainer=trainer, modal=modal, diet=diet, modals=modals, today=today, data=data)
    return render_template('member.html', user=user, mem=member, free=exercise, trainer=trainer, modal=modal, modals=modals, diet=diet, today=today, data=data)


@app.route('/member/<int:id>/home/diet')
@login_requiredM
def diet_memberhome(id):
    user = User.query.get_or_404(id)
    user1 = aliased(User)
    user2 = aliased(User)
    today = date.today()
    train = Member.query.filter_by(user_id=user.user_id).first()
    page = request.args.get('pager', 1, int)
    diet = Diet.query.filter_by(member_id=train.trainer_id).order_by(
        desc(Diet.date_added)).paginate(page=page, per_page=3)
    modals = Diet.query.filter_by(member_id=train.trainer_id).join(Trainer, Trainer.trainer_id == Diet.trainer_id).join(Member, Member.member_id == Diet.member_id).join(user1, user1.user_id == Trainer.user_id).join(user2, user2.user_id == Member.user_id).add_columns(
        Diet.diet_id, Diet.diet_description, Diet.diet_name, Diet.diet_file, Diet.start_date, Diet.end_date, Diet.date_added, user1.firstname, user1.lastname, user2.firstname.label('mfirst'), user2.lastname.label('mlast')).all()
    if 'hx_request' in request.headers:
        return render_template('dietmemberhome.html', user=user, diet=diet, modals=modals, today=today)
    abort(404)


@app.route('/member/<int:id>/trainer')
@login_requiredM
def view_trainer(id):
    user = User.query.get_or_404(id)
    trainer = Trainer.query.all()
    mem = []
    for train in trainer:
        x = train.user_id
        mem.append(x)
    search = request.args.get('search')
    page = request.args.get('page', 1, int)
    te = User.query.order_by(asc(User.firstname)).filter(
        User.user_id.in_(mem)).paginate(page=page, per_page=6)
    if search:
        result = User.query.order_by(asc(User.firstname)).filter(User.user_id.in_(mem), (User.firstname.contains(search) | User.lastname.contains(
            search) | User.age.contains(search) | User.email.contains(search) | User.gender.contains(search))).paginate(page=page, per_page=6)
    else:
        result = te
    if 'hx_request' in request.headers:
        return render_template('searchresulttrain.html', user=user, result=result)
    return render_template('trainer.html', user=user, result=result)


@app.route('/member/<int:id>/trainer/<int:id2>/view')
@login_requiredM
def trainer_profile(id, id2):
    user = User.query.get_or_404(id)
    member = Member.query.filter_by(user_id=id).first()
    train = Trainer.query.filter_by(user_id=id2).all()
    page = request.args.get('page', 1, int)
    for tra in train:
        memb = Member.query.filter_by(trainer_id=tra.trainer_id).all()
        x = tra.trainer_id
    me = len(memb)
    images = Image.query.order_by(desc(Image.date_added)).filter_by(
        trainer_id=x).paginate(page=page, per_page=2)
    img = Image.query.filter_by(trainer_id=x).all()
    img = len(img)

    teacher = User.query.get_or_404(id2)
    if 'hx_request' in request.headers:
        return render_template('trainerimagemember.html', user=user, teacher=teacher, member=member, memb=me, images=images, img=img)
    return render_template('trainer_profile.html', user=user, teacher=teacher, member=member, memb=me, images=images, img=img)


@app.route('/member/<int:id>/trainer/<int:id2>/add')
@login_requiredM
def add_trainer(id, id2):
    user = User.query.get_or_404(id)
    member = Member.query.filter_by(user_id=id).first()
    trainer = Trainer.query.filter_by(user_id=id2).first()
    if member and trainer:
        member.trainer_id = trainer.trainer_id
        db.session.commit()
        return redirect(f'/member/{user.user_id}')
    else:
        return redirect(request.url)


@app.route('/member/<int:id>/trainer/remove')
@login_requiredM
def rem_trainer(id):
    user = User.query.get_or_404(id)
    member = Member.query.filter_by(user_id=id).first()
    schedule = Schedule.query.filter_by(member_id=member.member_id).all()
    diet = Diet.query.filter_by(member_id=member.member_id).all()
    exercise = Exercise.query.filter_by(member_id=member.member_id).all()
    if member:
        member.trainer_id = None
        for ex in exercise:
            db.session.delete(ex)
        for di in diet:
            db.session.delete(di)
        for sch in schedule:
            db.session.delete(sch)
        db.session.commit()

        return redirect(f'/member/{user.user_id}#trainer')
    else:
        return redirect(request.url)


@app.route('/member/<int:id>/profile')
@login_requiredM
def member_profile(id):
    user = User.query.get_or_404(id)
    member = Member.query.filter_by(user_id=id).first()
    usertrain = 'none'
    train_user = Trainer.query.filter_by(trainer_id=member.trainer_id).first()
    today = date.today()
    data = Schedule.query.filter_by(member_id=member.member_id).order_by(
        Schedule.schedule_date).filter(Schedule.schedule_date >= today).limit(3).all()
    print(data)
    if train_user:
        usertrain = User.query.get_or_404(train_user.user_id)
    return render_template('memberprofile.html', user=user, usertrain=usertrain, data=data, today=today)


@app.route('/member/<int:id>/profile/edit', methods=['GET', 'POST'])
@login_requiredM
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
                os.remove(os.path.join(
                    app.config['UPLOADS'], user.profile_image))
            user.profile_image = request.files['profile_image']
            if files(user.profile_image.filename):
                filename = secure_filename(user.profile_image.filename)
                filename = f"__{id}_{filename}"
                user.profile_image.save(os.path.join(
                    app.config['UPLOADS'], filename))
                user.profile_image = filename
                db.session.commit()
        else:
            db.session.commit()
        return redirect(f'/member/{user.user_id}/profile')
    return render_template('editmemprofile.html', user=user)


@app.route('/member/<int:id>/profile/image/delete', methods=['GET', 'POST'])
@login_requiredM
def delete_profile_image(id):
    user = User.query.get_or_404(id)
    if os.path.exists('static/uploads/' + user.profile_image):
        os.remove(os.path.join(app.config['UPLOADS'], user.profile_image))
    user.profile_image = "none"
    db.session.commit()
    return redirect(f"/member/{user.user_id}/profile")


@app.route('/member/<int:id>/premium/all')
@login_requiredM
def membpremium(id):
    user = User.query.get_or_404(id)
    user1 = aliased(User)
    user2 = aliased(User)
    page = request.args.get('page', 1, int)
    search = request.args.get('search')
    member = Member.query.filter_by(user_id=user.user_id).first()
    data = Exercise.query.filter_by(
        member_id=member.member_id).paginate(page=page, per_page=9)
    free = Exercise.query.filter_by(member_id=member.member_id).join(Member, Member.member_id == Exercise.member_id).join(Trainer, Exercise.trainer_id == Trainer.trainer_id).join(user1, Member.user_id == user1.user_id).join(user2, Trainer.user_id == user2.user_id).add_columns(
        Exercise.exercise_id, Exercise.exercise_name, Exercise.exercise_description, Exercise.exercise_file, Exercise.exercise_link, Exercise.exercise_thumbnail, Exercise.date_added, Member.member_id, Trainer.trainer_id, user1.firstname, user1.lastname, user2.firstname.label('tfirst'), user2.lastname.label('tlast')).all()
    if search:
        pagin = Exercise.query.filter_by(member_id=member.member_id).join(Member, Member.member_id == Exercise.member_id).join(Trainer, Exercise.trainer_id == Trainer.trainer_id).join(user1, Member.user_id == user1.user_id).join(user2, Trainer.user_id == user2.user_id).add_columns(user1.username, user1.firstname, user1.lastname, user1.email, user1.age, user1.gender, user1.country, user2.username, user2.firstname, user2.lastname, user2.email, user2.age, user2.gender, user2.country, Exercise.exercise_thumbnail, Exercise.exercise_id, Exercise.exercise_file, Exercise.exercise_description, Exercise.exercise_link, Exercise.exercise_name).filter(
            (user1.firstname.contains(search) | user1.lastname.contains(search) | user1.username.contains(search) | user1.country.contains(search) | user1.age.contains(search) | user1.email.contains(search) | user1.gender.contains(search) | Exercise.exercise_description.contains(search) | Exercise.date_added.contains(search) | Exercise.exercise_name.contains(search) | user2.firstname.contains(search) | user2.lastname.contains(search) | user2.username.contains(search) | user2.country.contains(search) | user2.age.contains(search) | user2.email.contains(search) | user2.gender.contains(search))).paginate(page=page, per_page=9)
    else:
        pagin = data
    if 'hx_request' in request.headers:
        return render_template("membpremium.html", user=user, pagin=pagin, free=free)
    return render_template("memberpremium.html", user=user, pagin=pagin, free=free)


@app.route('/member/<int:id>/diet')
@login_requiredM
def mem_diet(id):
    user = User.query.get_or_404(id)
    member = Member.query.filter_by(user_id=id).first()
    today = date.today()
    user1 = aliased(User)
    user2 = aliased(User)
    page = request.args.get('page', 1, int)
    search = request.args.get('search')
    diets = Diet.query.filter_by(
        member_id=member.member_id).paginate(page=page, per_page=3)
    modal = Diet.query.filter_by(member_id=member.member_id).join(Trainer, Trainer.trainer_id == Diet.trainer_id).join(Member, Member.member_id == Diet.member_id).join(user1, user1.user_id == Trainer.user_id).join(user2, user2.user_id == Member.user_id).add_columns(
        Diet.diet_id, Diet.diet_description, Diet.diet_name, Diet.diet_file, Diet.start_date, Diet.end_date, Diet.date_added, user1.firstname, user1.lastname, user2.firstname.label('mfirst'), user2.lastname.label('mlast')).all()
    if search:
        diet = Diet.query.filter_by(member_id=member.member_id).join(Member, Member.member_id == Diet.member_id).join(User, User.user_id == Member.user_id).add_columns(Diet.diet_id, Diet.diet_name, Diet.start_date, Diet.end_date, Diet.date_added, Diet.diet_file, User.firstname, User.lastname).filter(
            Diet.diet_name.contains(search) | Diet.start_date.contains(search) | Diet.end_date.contains(search) | Diet.date_added.contains(search) | User.firstname.contains(search) | User.lastname.contains(search)).paginate(page=page, per_page=3)
    else:
        diet = diets
    if 'hx_request' in request.headers:
        return render_template('memberdietpage.html', user=user, diet=diet, modal=modal, today=today)
    return render_template('memberdiet.html', user=user, diet=diet, modal=modal, today=today)


@app.route('/member/<int:id>/payment', methods=['POST', 'GET'])
@login_requiredM
def payment(id):
    user = User.query.get_or_404(id)
    member = Member.query.filter_by(user_id=id).first()
    if request.method == 'POST':
        email = request.form["email"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        member.status = 'active'
        d = datetime.now()
        member.date_active = d
        db.session.commit()
        sender = "email"
        receiver = email
        content = f"""Hello {firstname} {lastname},
You are successfully subscribed to victory gym. You can now choose a trainer and start your fitness journey
                
                """
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = receiver
        message['Subject'] = 'Subscription'  # The subject line
        # The body and the attachments for the mail
        message.attach(MIMEText(content, 'plain'))
        try:
            smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpobj.starttls()
            smtpobj.login(user=sender,
                          password="password")
            text = message.as_string()
            smtpobj.sendmail(from_addr=sender, to_addrs=receiver, msg=text)
            print("Email sent successfully")
            smtpobj.quit()
        except SMTPException as e:
            print(e)
        return redirect(f"/member/{user.user_id}")

    return render_template("payment.html", user=user)
# TRAINER


@app.route('/trainer/<int:id>')
@login_requiredT
def trainer(id):
    trainer = User.query.get_or_404(id)
    user1 = aliased(User)
    user2 = aliased(User)
    today = date.today()
    train = Trainer.query.filter_by(user_id=trainer.user_id).first()
    free = Exercise.query.filter_by(trainer_id=train.trainer_id).join(Trainer, Exercise.trainer_id == Trainer.trainer_id).join(Member, Exercise.member_id == Member.member_id).join(user1, Trainer.user_id == user1.user_id).join(user2, Member.user_id == user2.user_id).add_columns(
        Exercise.exercise_id, Exercise.exercise_thumbnail, Exercise.date_added, Exercise.exercise_name, Exercise.exercise_description, Exercise.exercise_file, Exercise.exercise_link, user1.firstname, user1.lastname, user2.firstname.label("mfirst"), user2.lastname.label("mlast")).all()
    data = Exercise.query.order_by(desc(Exercise.date_added)).filter_by(
        trainer_id=train.trainer_id).limit(3).all()
    members = []
    memb = Member.query.filter_by(trainer_id=train.trainer_id).all()
    for me in memb:
        w = me.user_id
        member = User.query.filter_by(user_id=w).all()
        members.append(member)
    members = members[0:4]
    page = request.args.get('page', 1, int)
    diet = Diet.query.filter_by(trainer_id=train.trainer_id).order_by(
        desc(Diet.date_added)).paginate(page=page, per_page=3)
    modal = Diet.query.filter_by(trainer_id=train.trainer_id).join(Trainer, Trainer.trainer_id == Diet.trainer_id).join(Member, Member.member_id == Diet.member_id).join(user1, user1.user_id == Trainer.user_id).join(user2, user2.user_id == Member.user_id).add_columns(
        Diet.diet_id, Diet.diet_description, Diet.diet_name, Diet.diet_file, Diet.start_date, Diet.end_date, Diet.date_added, user1.firstname, user1.lastname, user2.firstname.label('mfirst'), user2.lastname.label('mlast')).all()

    if 'hx_request' in request.headers:
        return render_template('premium.html', trainer=trainer, members=members, data=data, frees=free, diet=diet, modal=modal, today=today)
    return render_template('trainerhome.html', trainer=trainer, members=members, data=data, frees=free, diet=diet, modal=modal, today=today)


@app.route('/trainer/<int:id>/home/diet')
@login_requiredT
def diet_home(id):
    trainer = User.query.get_or_404(id)
    user1 = aliased(User)
    user2 = aliased(User)
    train = Trainer.query.filter_by(user_id=trainer.user_id).first()
    page = request.args.get('page', 1, int)
    diet = Diet.query.filter_by(trainer_id=train.trainer_id).order_by(
        desc(Diet.date_added)).paginate(page=page, per_page=3)
    modal = Diet.query.filter_by(trainer_id=train.trainer_id).join(Trainer, Trainer.trainer_id == Diet.trainer_id).join(Member, Member.member_id == Diet.member_id).join(user1, user1.user_id == Trainer.user_id).join(user2, user2.user_id == Member.user_id).add_columns(
        Diet.diet_id, Diet.diet_description, Diet.diet_name, Diet.diet_file, Diet.start_date, Diet.end_date, Diet.date_added, user1.firstname, user1.lastname, user2.firstname.label('mfirst'), user2.lastname.label('mlast')).all()
    if 'hx_request' in request.headers:
        return render_template('diettrainhome.html', trainer=trainer, diet=diet, modal=modal)
    abort(404)


@app.route('/trainer/<int:id>/free')
@login_requiredT
def free_train_home(id):
    trainer = User.query.get_or_404(id)
    train = Trainer.query.filter_by(user_id=trainer.user_id).first()
    free = Free_training.query.filter_by(trainer_id=train.trainer_id).join(Trainer, Free_training.trainer_id == Trainer.trainer_id).join(User, Trainer.user_id == User.user_id).add_columns(
        Free_training.free_id, Free_training.free_thumbnail, Free_training.date_added, Free_training.free_caption, Free_training.free_description, Free_training.free_file, Free_training.free_link, User.firstname, User.lastname).all()
    data = Free_training.query.order_by(desc(Free_training.date_added)).filter_by(
        trainer_id=train.trainer_id).filter(Free_training.free_file == 'N/A').limit(3).all()
    if "hx_request" in request.headers:
        return render_template('freetrainhome.html', trainer=trainer, free=free, datas=data)
    return abort(404)


@app.route('/trainer/<int:id>/member/<int:id2>/view')
@login_requiredT
def memberprofile(id, id2):
    user = User.query.get_or_404(id2)
    trainer = User.query.get_or_404(id)
    return render_template('memberprofile.html', user=user, trainer=trainer)


@app.route('/trainer/<int:id>/profile')
@login_requiredT
def trainerprofile(id):
    trainer = User.query.get_or_404(id)
    train = Trainer.query.filter_by(user_id=id).first()
    today = date.today()
    data = Schedule.query.filter_by(trainer_id=train.trainer_id).order_by(Schedule.schedule_date).join(Member, Member.member_id == Schedule.member_id).join(
        User, User.user_id == Member.user_id).add_columns(Schedule.schedule_id, Schedule.schedule_date, Schedule.schedule_time, User.firstname, User.lastname, User.profile_image).filter(Schedule.schedule_date > today).limit(3).all()
    page = request.args.get('page', 1, int)
    images = Image.query.order_by(desc(Image.date_added)).filter_by(
        trainer_id=train.trainer_id).paginate(page=page, per_page=2)
    img = Image.query.filter_by(trainer_id=train.trainer_id).all()
    img = len(img)

    memb = Member.query.filter_by(trainer_id=train.trainer_id).all()
    if memb:
        me = len(memb)
    else:
        me = 0
    if 'hx_request' in request.headers:
        return render_template('trainerimageresult.html', memb=me, trainer=trainer, images=images, img=img, data=data)
    return render_template('trainerprofile.html', memb=me, trainer=trainer, images=images, img=img, data=data)


@app.route('/trainer/<int:id>/profile/edit',  methods=['GET', 'POST'])
@login_requiredT
def traineredit(id):
    trainer = User.query.get_or_404(id)
    if request.method == 'POST':
        trainer.profile = request.form['profile']
        if request.files['profile_image'].filename != '':
            if os.path.exists('static/uploads/' + trainer.profile_image):
                os.remove(os.path.join(
                    app.config['UPLOADS'], trainer.profile_image))
            trainer.profile_image = request.files['profile_image']
            if files(trainer.profile_image.filename):
                filename = secure_filename(trainer.profile_image.filename)
                filename = f"__{id}_{filename}"
                trainer.profile_image.save(
                    os.path.join(app.config['UPLOADS'], filename))
                trainer.profile_image = filename
                db.session.commit()
        else:
            db.session.commit()
        return redirect(f'/trainer/{trainer.user_id}/profile')
    return render_template('edittrainerprofile.html', trainer=trainer)


@app.route('/trainer/<int:id>/profile/image/delete',  methods=['GET', 'POST'])
@login_requiredT
def delete_trainer_pimage(id):
    trainer = User.query.get_or_404(id)
    if os.path.exists('static/uploads/' + trainer.profile_image):
        os.remove(os.path.join(app.config['UPLOADS'], trainer.profile_image))
    trainer.profile_image = "none"
    db.session.commit()
    return redirect(f"/trainer/{trainer.user_id}/profile")


@app.route('/trainer/<int:id>/members/view', methods=['GET'])
@login_requiredT
def memberview(id):
    trainer = User.query.get_or_404(id)
    train = Trainer.query.filter_by(user_id=id).all()
    mem = []
    if train:
        for tra in train:
            memb = Member.query.filter_by(trainer_id=tra.trainer_id).all()
        for me in memb:
            w = me.user_id
            mem.append(w)
    page = request.args.get('page', 1, type=int)
    mv = User.query.order_by(asc(User.firstname)).filter(
        User.user_id.in_(mem)).paginate(page=page, per_page=6)
    search = request.args.get('search')
    if search:
        result = User.query.order_by(asc(User.firstname)).filter(User.user_id.in_(mem), (User.firstname.contains(search) | User.lastname.contains(
            search) | User.age.contains(search) | User.email.contains(search) | User.gender.contains(search))).paginate(page=page, per_page=6)
    else:
        result = mv
    if 'hx_request' in request.headers:
        return render_template('searchresult.html', trainer=trainer, result=result)
    return render_template('memberview.html', trainer=trainer, result=result)


@app.route('/trainer/<int:id>/image/upload', methods=['GET', 'POST'])
@login_requiredT
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
            post = Image(trainer_id=x, image_file=filename, caption=caption)
            db.session.add(post)
            db.session.commit()
            return redirect(f"/trainer/{trainer.user_id}/profile")
        else:
            return redirect(request.url)
    return render_template('trainerimage.html', trainer=trainer)


@app.route('/trainer/<int:id>/image/<int:id2>/delete')
@login_requiredT
def delete_image(id, id2):
    trainer = User.query.get_or_404(id)
    image = Image.query.get_or_404(id2)
    if image:
        if os.path.exists('static/uploads/' + image.image_file):
            os.remove(os.path.join(app.config['UPLOADS'], image.image_file))
        db.session.delete(image)
        db.session.commit()
    else:
        abort(404)
    return redirect(f'/trainer/{trainer.user_id}/profile')


@app.route('/trainer/<int:id>/premiumworkout', methods=['POST', 'GET'])
@login_requiredT
def premium_workout(id):
    user1 = aliased(User)
    user2 = aliased(User)
    trainer = User.query.get_or_404(id)
    page = request.args.get('page', 1, int)
    search = request.args.get('search')
    train = Trainer.query.filter_by(user_id=trainer.user_id).first()
    free = Exercise.query.filter_by(trainer_id=train.trainer_id).join(Trainer, Exercise.trainer_id == Trainer.trainer_id).join(Member, Exercise.member_id == Member.member_id).join(user1, Trainer.user_id == user1.user_id).join(user2, Member.user_id == user2.user_id).add_columns(
        Exercise.exercise_id, Exercise.exercise_thumbnail, Exercise.date_added, Exercise.exercise_name, Exercise.exercise_description, Exercise.exercise_file, Exercise.exercise_link, user1.firstname, user1.lastname, user2.firstname.label("mfirst"), user2.lastname.label("mlast")).all()

    data = Exercise.query.filter_by(
        trainer_id=train.trainer_id).paginate(page=page, per_page=9)

    memb = Member.query.filter_by(trainer_id=train.trainer_id).join(User, User.user_id == Member.user_id).add_columns(
        User.user_id, User.firstname, User.lastname, Member.member_id).all()
    if request.method == 'POST':
        video_file = request.files['video_file']
        link = request.form['link']
        caption = request.form['caption']
        description = request.form['description']
        member = request.form['member']
        if video_file:
            if vids(video_file.filename):
                filename = secure_filename(video_file.filename)
                filename = f"p{id}_{filename}"
                video_file.save(os.path.join(app.config['UPLOADS'], filename))
                new = filename.replace("mp4", "jpg")
                new_db = filename.replace(".mp4", "")
                ff.convert(os.path.join(app.config['UPLOADS'], filename), os.path.join(
                    app.config['UPLOADS'], new))
                new_vid = Exercise(trainer_id=train.trainer_id, exercise_file=filename, exercise_name=caption,
                                   exercise_description=description, exercise_thumbnail=new_db, member_id=member)
                db.session.add(new_vid)
                db.session.commit()
                return redirect(request.url)
            else:
                return redirect(request.url)
        else:
            link_id = link.split('/')[-1]
            def check(x): return x in link.lower().split('/')
            if check("youtu.be"):
                new_vid = Exercise(trainer_id=train.trainer_id, exercise_link=link_id, exercise_name=caption,
                                   exercise_description=description, exercise_thumbnail=link_id, member_id=member)
                db.session.add(new_vid)
                db.session.commit()
                return redirect(request.url)
            else:
                return redirect(request.url)
    if search:
        pagin = Exercise.query.filter_by(trainer_id=train.trainer_id).join(Trainer, Exercise.trainer_id == Trainer.trainer_id).join(Member, Member.member_id == Exercise.member_id).join(user1, Trainer.user_id == user1.user_id).join(user2, Member.user_id == user2.user_id).add_columns(user1.username, user1.firstname, user1.lastname, user1.email, user1.age, user1.gender, user1.country, user2.username, user2.firstname, user2.lastname, user2.email, user2.age, user2.gender, user2.country, Exercise.exercise_thumbnail, Exercise.exercise_id, Exercise.exercise_file, Exercise.exercise_description, Exercise.exercise_link, Exercise.exercise_name).filter(
            (user1.firstname.contains(search) | user1.lastname.contains(search) | user1.username.contains(search) | user1.country.contains(search) | user1.age.contains(search) | user1.email.contains(search) | user1.gender.contains(search) | Exercise.exercise_description.contains(search) | Exercise.date_added.contains(search) | Exercise.exercise_name.contains(search) | user2.firstname.contains(search) | user2.lastname.contains(search) | user2.username.contains(search) | user2.country.contains(search) | user2.age.contains(search) | user2.email.contains(search) | user2.gender.contains(search))).paginate(page=page, per_page=9)
    else:
        pagin = data
    if 'hx_request' in request.headers:
        return render_template("trainexerciseview.html", trainer=trainer, memb=memb, free=free, pagin=pagin)
    return render_template('exercisevideo.html', trainer=trainer, memb=memb, free=free, pagin=pagin)


@app.route('/trainer/<int:id>/exerciseworkout/<int:id2>/delete')
@login_requiredT
def premium_delete(id, id2):
    trainer = User.query.get_or_404(id)
    video = Exercise.query.get_or_404(id2)
    if os.path.exists('static/uploads/' + video.exercise_file):
        os.remove(os.path.join(app.config['UPLOADS'], video.exercise_file))
    if os.path.exists('static/uploads/' + video.exercise_thumbnail + '.jpg'):
        os.remove(os.path.join(
            app.config['UPLOADS'], video.exercise_thumbnail + '.jpg'))
    db.session.delete(video)
    db.session.commit()
    return redirect(f"/trainer/{trainer.user_id}/premiumworkout")
# @app.route('/trainer/<int:id>/freevideo/upload', methods = ['POST','GET'])
# def free_upload(id):
    # trainer = User.query.get_or_404(id)
    # train = Trainer.query.filter_by(user_id=id).all()
    # for tr in train:
    #     w = tr.trainer_id
    # if request.method == 'POST':
    #     video_file = request.files['video_file']
    #     link = request.form['link']
    #     caption = request.form['caption']
    #     description = request.form['description']
    #     if video_file and vids(video_file.filename):
    #         filename = secure_filename(video_file.filename)
    #         filename = f"f{id}_{filename}"
    #         video_file.save(os.path.join(app.config['UPLOADS'], filename))
    #         thumbnail = filename.split('.')
    #         y = len(thumbnail) - 1
    #         thumbnail[y] = "jpg"
    #         new = '.'.join(thumbnail)
    #         thumbnail[y] = ""
    #         new_db = ''.join(thumbnail)
    #         ff.convert(os.path.join(app.config['UPLOADS'], filename), os.path.join(
    #             app.config['UPLOADS'], new))
    #         new_vid = Free_training(trainer_id=w, free_file=filename, free_caption=caption,
    #                                 free_description=description, free_thumbnail=new_db)
    #         db.session.add(new_vid)
    #         db.session.commit()
    #         return redirect(request.url)
    #     else:
    #         link_id = link.split('/')[-1]
    #         new_vid = Free_training(trainer_id=w, free_link=link_id, free_caption=caption,
    #                                 free_description=description, free_thumbnail=link_id)
    #         db.session.add(new_vid)
    #         db.session.commit()
    #         return redirect(request.url)
    # return render_template('freevideo.html', trainer=trainer)


@app.route('/trainer/<int:id>/freeworkout', methods=['POST', 'GET'])
@login_requiredT
def trainer_free(id):
    page = request.args.get('page', 1, int)
    search = request.args.get('search')
    trainer = User.query.get_or_404(id)

    train = Trainer.query.filter_by(user_id=trainer.user_id).first()
    free = Free_training.query.filter_by(trainer_id=train.trainer_id).join(Trainer, Free_training.trainer_id == Trainer.trainer_id).join(User, Trainer.user_id == User.user_id).add_columns(
        Free_training.free_id, Free_training.free_thumbnail, Free_training.date_added, Free_training.free_caption, Free_training.free_description, Free_training.free_file, Free_training.free_link, User.firstname, User.lastname).all()
    data = Free_training.query.filter_by(
        trainer_id=train.trainer_id).paginate(page=page, per_page=9)
    if request.method == "POST":
        video_file = request.files['video_file']
        link = request.form['link']
        caption = request.form['caption']
        description = request.form['description']
        if video_file:
            if vids(video_file.filename):
                filename = secure_filename(video_file.filename)
                filename = f"f{id}_{filename}"
                video_file.save(os.path.join(app.config['UPLOADS'], filename))
                new = filename.replace("mp4", "jpg")
                new_db = filename.replace(".mp4", "")
                ff.convert(os.path.join(app.config['UPLOADS'], filename), os.path.join(
                    app.config['UPLOADS'], new))
                new_vid = Free_training(trainer_id=train.trainer_id, free_file=filename,
                                        free_caption=caption, free_description=description, free_thumbnail=new_db)
                db.session.add(new_vid)
                db.session.commit()
                return redirect(request.url)
            else:
                return redirect(request.url)
        else:
            link_id = link.split('/')[-1]
            def check(x): return x in link.lower().split('/')
            if check("youtu.be"):
                link_id = link.split('/')[-1]
                new_vid = Free_training(trainer_id=train.trainer_id, free_link=link_id,
                                        free_caption=caption, free_description=description, free_thumbnail=link_id)
                db.session.add(new_vid)
                db.session.commit()
                return redirect(request.url)
            else:
                return redirect(request.url)
    if search:
        pagin = Free_training.query.filter_by(trainer_id=train.trainer_id).join(Trainer, Free_training.trainer_id == Trainer.trainer_id).join(User, Trainer.user_id == User.user_id).add_columns(User.username, User.firstname, User.lastname, User.email, User.age, User.gender, User.country, Free_training.free_thumbnail, Free_training.free_id, Free_training.free_file, Free_training.free_description, Free_training.free_link, Free_training.free_caption).filter(
            (User.firstname.contains(search) | User.lastname.contains(search) | User.username.contains(search) | User.country.contains(search) | User.age.contains(search) | User.email.contains(search) | User.gender.contains(search) | Free_training.free_description.contains(search) | Free_training.date_added.contains(search) | Free_training.free_caption.contains(search))).paginate(page=page, per_page=9)
    else:
        pagin = data
    if 'hx_request' in request.headers:
        return render_template("trainfreeview.html", trainer=trainer, free=free, pagin=pagin)
    return render_template("trainfreevideo.html", trainer=trainer, free=free, pagin=pagin)


@app.route('/trainer/<int:id>/freeworkout/<int:id2>/delete')
@login_requiredT
def free_delete(id, id2):
    trainer = User.query.get_or_404(id)
    video = Free_training.query.get_or_404(id2)
    if os.path.exists('static/uploads/' + video.free_file):
        os.remove(os.path.join(app.config['UPLOADS'], video.free_file))
    if os.path.exists('static/uploads/' + video.free_thumbnail + '.jpg'):
        os.remove(os.path.join(
            app.config['UPLOADS'], video.free_thumbnail + '.jpg'))
    db.session.delete(video)
    db.session.commit()
    return redirect(f"/trainer/{trainer.user_id}/freeworkout")


@app.route('/trainer/<int:id>/diet', methods=['POST', 'GET'])
@login_requiredT
def trainer_diet(id):
    trainer = User.query.get_or_404(id)
    train = Trainer.query.filter_by(user_id=id).first()
    members = Member.query.filter_by(trainer_id=train.trainer_id).join(
        User, User.user_id == Member.user_id).add_columns(Member.member_id, User.firstname, User.lastname).all()
    user1 = aliased(User)
    user2 = aliased(User)
    today = date.today()
    page = request.args.get('page', 1, int)
    search = request.args.get('search')
    diets = Diet.query.filter_by(
        trainer_id=train.trainer_id).paginate(page=page, per_page=3)
    modal = Diet.query.filter_by(trainer_id=train.trainer_id).join(Trainer, Trainer.trainer_id == Diet.trainer_id).join(Member, Member.member_id == Diet.member_id).join(user1, user1.user_id == Trainer.user_id).join(user2, user2.user_id == Member.user_id).add_columns(
        Diet.diet_id, Diet.diet_description, Diet.diet_name, Diet.diet_file, Diet.start_date, Diet.end_date, Diet.date_added, user1.firstname, user1.lastname, user2.firstname.label('mfirst'), user2.lastname.label('mlast')).all()

    if request.method == 'POST':
        diet_file = request.files["diet_file"]
        diet_name = request.form['name']
        start_date = request.form['startdate']
        end_date = request.form['enddate']
        diet_description = request.form['description']
        member_id = request.form['member']
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        # diet_description = diet_description.replace('<p>','<span>')
        # diet_description = diet_description.replace('</p>','</span>')
        if end_date > start_date:
            if diet_file:
                if files(diet_file.filename):
                    filename = secure_filename(diet_file.filename)
                    filename = f"d_{id}_{filename}"
                    diet_file.save(os.path.join(
                        app.config['UPLOADS'], filename))
                    new = Diet(trainer_id=train.trainer_id, diet_name=diet_name, diet_file=filename,
                               diet_description=diet_description, start_date=start_date, end_date=end_date, member_id=member_id)
                    db.session.add(new)
                    db.session.commit()
                    return redirect(f"/trainer/{trainer.user_id}/diet")
                else:
                    return redirect(request.url)
            else:
                new = Diet(trainer_id=train.trainer_id, diet_name=diet_name, diet_description=diet_description,
                           start_date=start_date, end_date=end_date, member_id=member_id)
                db.session.add(new)
                db.session.commit()
                return redirect(f"/trainer/{trainer.user_id}/diet")
        else:
            return redirect(request.url)
    if search:
        diet = Diet.query.filter_by(trainer_id=train.trainer_id).join(Member, Member.member_id == Diet.member_id).join(User, User.user_id == Member.user_id).add_columns(Diet.diet_id, Diet.diet_name, Diet.start_date, Diet.end_date, Diet.date_added, Diet.diet_file, User.firstname, User.lastname).filter(
            Diet.diet_name.contains(search) | Diet.start_date.contains(search) | Diet.end_date.contains(search) | Diet.date_added.contains(search) | User.firstname.contains(search) | User.lastname.contains(search)).paginate(page=page, per_page=3)
    else:
        diet = diets
    if 'hx_request' in request.headers:
        return render_template('traindietpage.html', trainer=trainer, diet=diet, members=members, modal=modal, today=today)
    return render_template('trainerdiet.html', trainer=trainer, diet=diet, members=members, modal=modal, today=today)


@app.route('/trainer/<int:id>/diet/<int:id2>/delete')
@login_requiredT
def delete_diet(id, id2):
    trainer = User.query.get_or_404(id)
    diet = Diet.query.get_or_404(id2)
    # print(diet)
    if os.path.exists('static/uploads/' + diet.diet_file):
        os.remove(os.path.join(app.config['UPLOADS'], diet.diet_file))
    db.session.delete(diet)
    db.session.commit()
    return redirect(f"/trainer/{trainer.user_id}/diet")


@app.route('/trainer/<int:id>/diet/<int:id2>/edit', methods=["POST"])
@login_requiredT
def edit_diet(id, id2):
    trainer = User.query.get_or_404(id)
    diet = Diet.query.get_or_404(id2)
    diet.diet_name = request.form['name']
    start_date = request.form['startdate']
    end_date = request.form['enddate']
    diet.diet_description = request.form['description2']
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    diet.start_date = start_date
    diet.end_date = end_date
    if end_date > start_date:
        if request.files['diet_file'].filename != '':
            if os.path.exists('static/uploads/' + diet.diet_file):
                os.remove(os.path.join(app.config['UPLOADS'], diet.diet_file))
            diet.diet_file = request.files['diet_file']
            if files(diet.diet_file.filename):
                filename = secure_filename(diet.diet_file.filename)
                filename = f"de_{id}_{filename}"
                diet.diet_file.save(os.path.join(
                    app.config['UPLOADS'], filename))
                diet.diet_file = filename
                db.session.commit()
        else:
            db.session.commit()
    else:
        return redirect(f'/trainer/{trainer.user_id}/diet')
    return redirect(f'/trainer/{trainer.user_id}/diet')


@app.route('/trainer/<int:id>/schedule', methods=["POST", "GET"])
@login_requiredT
def trainer_schedule(id):
    trainer = User.query.get_or_404(id)
    train = Trainer.query.filter_by(user_id=id).first()
    member = Member.query.filter_by(trainer_id=train.trainer_id).join(
        User, User.user_id == Member.user_id).add_columns(Member.member_id, User.firstname, User.lastname).all()
    today = datetime.today().date()
    # print(today)
    if request.method == "POST":
        member_id = request.form["member"]
        schedule_date = request.form["date"]
        schedule_time = request.form["time"]
        schedule_date = datetime.strptime(schedule_date, "%Y-%m-%d").date()
        schedule_time = datetime.strptime(schedule_time, "%H:%M").time()
        new = Schedule(schedule_date=schedule_date, schedule_time=schedule_time,
                       member_id=member_id, trainer_id=train.trainer_id)
        db.session.add(new)
        db.session.commit()
        return redirect(request.url)
    page = request.args.get('page', 1, int)
    data = Schedule.query.filter_by(trainer_id=train.trainer_id).order_by(Schedule.schedule_date).join(Member, Member.member_id == Schedule.member_id).join(
        User, User.user_id == Member.user_id).add_columns(Schedule.schedule_id, Schedule.schedule_date, Schedule.schedule_time, User.firstname, User.lastname, User.profile_image).paginate(page=page, per_page=5)
    datas = Schedule.query.filter_by(trainer_id=train.trainer_id).join(Member, Member.member_id == Schedule.member_id).join(
        User, User.user_id == Member.user_id).add_columns(Schedule.schedule_id, Schedule.schedule_date, Schedule.schedule_time, User.firstname, User.lastname, User.profile_image).all()
    search = request.args.get('search')
    if search:
        schedule = Schedule.query.filter_by(trainer_id=train.trainer_id).order_by(Schedule.schedule_date).join(Member, Member.member_id == Schedule.member_id).join(User, User.user_id == Member.user_id).add_columns(
            Schedule.schedule_id, Schedule.schedule_date, Schedule.schedule_time, User.firstname, User.lastname, User.profile_image).filter(User.firstname.contains(search) | User.lastname.contains(search)).paginate(page=page, per_page=5)
    else:
        schedule = data
    if "hx_request" in request.headers:
        return render_template("schetrain.html", trainer=trainer, members=member, schedule=schedule, today=today, datas=datas)
    return render_template("trainschedule.html", trainer=trainer, members=member, schedule=schedule, today=today, datas=datas)


@app.route('/trainer/<int:id>/schedule/<int:id2>/delete')
@login_requiredT
def delete_schedule(id, id2):
    trainer = User.query.get_or_404(id)
    schedule = Schedule.query.get_or_404(id2)
    db.session.delete(schedule)
    db.session.commit()
    return redirect(f"/trainer/{trainer.user_id}/schedule")


@app.route('/trainer/<int:id>/schedule/<int:id2>/edit', methods=["POST"])
@login_requiredT
def edit_schedule(id, id2):
    trainer = User.query.get_or_404(id)
    schedule = Schedule.query.get_or_404(id2)
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        schedule_date = datetime.strptime(date, "%Y-%m-%d").date()
        schedule_time = datetime.strptime(time, "%H:%M").time()
        schedule.schedule_date = schedule_date
        schedule.schedule_time = schedule_time
        db.session.commit()
        return redirect(f"/trainer/{trainer.user_id}/schedule")


@app.route('/freevideo/all')
def freevideo_all():
    page = request.args.get('page', 1, int)
    free = Free_training.query.join(Trainer, Free_training.trainer_id == Trainer.trainer_id).join(User, Trainer.user_id == User.user_id).add_columns(
        Free_training.free_thumbnail, Free_training.date_added, Free_training.free_caption, Free_training.free_description, Free_training.free_file, Free_training.free_link, User.firstname, User.lastname).all()
    data = Free_training.query.paginate(page=page, per_page=9)
    search = request.args.get('search')
    if search:
        pagin = Free_training.query.join(Trainer, Free_training.trainer_id == Trainer.trainer_id).join(User, Trainer.user_id == User.user_id).add_columns(User.username, User.firstname, User.lastname, User.email, User.age, User.gender, User.country, Free_training.free_thumbnail, Free_training.free_file, Free_training.free_description, Free_training.free_link, Free_training.free_caption).filter(
            (User.firstname.contains(search) | User.lastname.contains(search) | User.username.contains(search) | User.country.contains(search) | User.age.contains(search) | User.email.contains(search) | User.gender.contains(search) | Free_training.free_description.contains(search) | Free_training.date_added.contains(search) | Free_training.free_caption.contains(search))).paginate(page=page, per_page=9)
    else:
        pagin = data

    # for pagi in pagin.items:
    #     print(pagi)
    if 'hx_request' in request.headers:
        return render_template("freeviewall.html", free=free, pagin=pagin)
    return render_template("freevideoall.html", free=free, pagin=pagin)


@app.route('/parallax')
def parallax():
    return render_template("parallax.html")
# link = "https://www.youtube.com/embed/-237OttBIBE"
# linklist = link.split("/")
# print(linklist)
# if "embed" in linklist:
#     print('yes')
# else:
#     print('no')
# d = date(2022, 9, 29).strftime("%A %d %B %Y")
# print(d)
# free = Free_training.query.all()
# for fr in free:
#     db.session.delete(fr)
#     db.session.commit()
# schedule_time = "12:30 PM"
# schedule_time = datetime.strptime(schedule_time, "%I:%M %p").time()
# print(schedule_time.strftime("%I:%M %p"))
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
# link = "https://youtu.be/embed/-237OttBIBE"
# print(link.lower().split('/'))
# check = lambda x: x in link.lower().split('/')
# print(check("youtu.be"))
# free =Exercise.query.filter_by(trainer_id = 2).join(Trainer, Exercise.trainer_id == Trainer.trainer_id).join(Member, Member.member_id == Exercise.member_id).join(User, Trainer.user_id == User.user_id).add_columns(User.firstname.label("tfirst"), User.lastname.label("tlast"), Member.member_id.label("tid")).group_by("tfirst","tlast","tid").union_all(Exercise.query.filter_by(trainer_id = 2).join(Trainer, Exercise.trainer_id == Trainer.trainer_id).join(Member, Member.member_id == Exercise.member_id).join(User, Member.user_id == User.user_id).add_columns(User.firstname.label("first"), User.lastname.label("last"), Member.member_id.label("id")).group_by("first","last","id")).all()


# free =Exercise.query.filter_by(trainer_id = 2).join(Trainer, Exercise.trainer_id == Trainer.trainer_id).join(Member, Member.member_id == Exercise.member_id).join(user1, Trainer.user_id == user1.user_id).join(user2, Member.user_id == user2.user_id).add_columns(user1.user_id, user2.user_id,user1.firstname.label("first"), user1.lastname.label("last"), user2.firstname, user2.lastname, Member.member_id).all()
# print(free)

# fr = Exercise.query.filter_by(trainer_id = 2).join(Trainer, Exercise.trainer_id == Trainer.trainer_id).join(Member, Member.member_id == Exercise.member_id).join(User, Member.user_id == User.user_id).add_columns(User.firstname, User.lastname, Member.member_id).all()
# print(free.union(fr))
# exer = Exercise.query.all()
# for ex in free:
#     print(ex.last)
# start_date = '19/09/2022'
# end_date = '22/09/2022'
# start_date = datetime.strptime(start_date, '%d/%m/%Y').date()
# end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
# new = Diet(member_id = 3, trainer_id = 2, start_date=start_date, end_date=end_date)
# db.session.add(new)
# db.session.commit()


# if vids(filename) is True:
#     print(True)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
