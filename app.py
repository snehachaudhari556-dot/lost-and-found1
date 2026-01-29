from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import or_, func
import uuid, os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kumbh-mela-secret-key'

# ✅ FIXED DB URI (CHANGE USERNAME/PASSWORD IF NEEDED)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin123@localhost:5432/kumbh_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Uploads
UPLOAD_FOLDER = "static/item_pics"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


# ================= MODELS =================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(20), default="Volunteer")


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_person = db.Column(db.Boolean, default=False)
    age = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    height = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Open")
    image_file = db.Column(db.String(100))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ================= AI MATCHING =================
def find_matches(new_item):
    opposite = "found" if new_item.type == "lost" else "lost"
    candidates = Item.query.filter_by(type=opposite, status="Open").all()

    if not candidates:
        return []

    texts = [f"{i.name} {i.description or ''}" for i in candidates]
    texts.append(f"{new_item.name} {new_item.description or ''}")

    try:
        vec = TfidfVectorizer(stop_words="english")
        tfidf = vec.fit_transform(texts)
        scores = cosine_similarity(tfidf[-1], tfidf[:-1])[0]

        results = []
        for i, score in enumerate(scores):
            if score > 0.25:
                results.append({
                    "item": candidates[i],
                    "score": round(score * 100, 2)
                })
        return sorted(results, key=lambda x: x["score"], reverse=True)
    except:
        return []


# ================= ROUTES =================
@app.route("/")
def index():
    lost = Item.query.filter_by(type="lost").order_by(Item.date_reported.desc()).limit(3)
    found = Item.query.filter_by(type="found").order_by(Item.date_reported.desc()).limit(3)
    return render_template("index.html", lost_items=lost, found_items=found)


@app.route("/dashboard")
@login_required
def dashboard():
    search = request.args.get("search", "")

    q = Item.query
    if search:
        q = q.filter(or_(
            Item.name.ilike(f"%{search}%"),
            Item.description.ilike(f"%{search}%"),
            Item.location.ilike(f"%{search}%"),
            Item.category.ilike(f"%{search}%")
        ))

    items = q.order_by(Item.date_reported.desc()).all()

    stats = {
        "lost": Item.query.filter_by(type="lost", status="Open").count(),
        "found": Item.query.filter_by(type="found", status="Open").count(),
        "resolved": Item.query.filter_by(status="Resolved").count()
    }

    locs = db.session.query(Item.location, func.count(Item.id)).group_by(Item.location).all()
    labels = [l for l, _ in locs]
    counts = [c for _, c in locs]

    return render_template("dashboard.html",
        all_items=items,
        stats=stats,
        labels=labels,
        counts=counts,
        search_query=search
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            if user.role != request.form["role"]:
                flash("Incorrect role selected", "error")
            else:
                login_user(user)
                return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(email=request.form["email"]).first():
            flash("Email already exists", "error")
        else:
            user = User(
                name=request.form["name"],
                email=request.form["email"],
                role=request.form["role"],
                password=generate_password_hash(request.form["password"])
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/report/<string:kind>", methods=["GET", "POST"])
@login_required
def report(kind):
    if request.method == "POST":
        file = request.files.get("item_image")
        filename = None

        if file and file.filename:
            ext = os.path.splitext(file.filename)[1]
            if ext.lower() not in [".jpg", ".jpeg", ".png"]:
                flash("Invalid image format", "error")
                return redirect(request.url)

        filename = f"{uuid.uuid4().hex}{ext}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))


        item = Item(
            type=kind,
            name=request.form["name"],
            category=request.form["category"],
            location=request.form["location"],
            description=request.form["description"],
            contact_name=request.form["contact_name"],
            contact_phone=request.form["contact_phone"],
            user_id=current_user.id,
            is_person=request.form["category"] in ["Missing Person", "Found Person"],
            age=request.form.get("age"),
            gender=request.form.get("gender"),
            height=request.form.get("height"),
            image_file=filename
        )

        db.session.add(item)
        db.session.commit()

        matches = find_matches(item)
        if matches:
            return render_template("matches.html", item=item, matches=matches)

        flash("Report submitted successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template(f"report_{kind}.html")


@app.route("/resolve/<int:item_id>", methods=["POST"])
@login_required
def resolve(item_id):
    if current_user.role != "Police":
        flash("Unauthorized", "error")
        return redirect(url_for("dashboard"))

    item = db.session.get(Item, item_id)
    item.status = "Resolved"
    db.session.commit()
    flash("Case resolved", "success")
    return redirect(url_for("dashboard"))

@app.route("/report-lost")
@login_required
def report_lost():
    return redirect(url_for("report", kind="lost"))

@app.route("/report-found")
@login_required
def report_found():
    return redirect(url_for("report", kind="found"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
