from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

# Configuração do site e do banco de dados.
app = Flask(__name__)
app.secret_key = "linkbase-chave-secreta"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///linkbase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Cada classe abaixo representa uma tabela do banco.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    links = db.relationship("SavedLink", backref="category")


class SavedLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("category.id"), nullable=False
    )


# Rotas do site.
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/home")
    return render_template("begin.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        identifier = request.form["identifier"].lower()
        password = request.form["password"]
        users_db = User.query.all()

        for user in users_db:
            # Compara os dados digitados com cada conta cadastrada.
            if (
                identifier == user.username.lower()
                or identifier == user.email.lower()
            ) and password == user.password:
                # Guarda os dados necessários enquanto estiver conectada.
                session["user_id"] = user.id
                session["username"] = user.username
                return redirect("/home")

        # A mensagem é exibida no próprio formulário de login.
        error = "Usuário ou senha incorretos."

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def registration():
    error = ""

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        users_db = User.query.all()
        user_exists = False

        for user in users_db:
            # Não permite repetir nome de usuário ou e-mail.
            if username.lower() == user.username.lower():
                user_exists = True
            if email == user.email.lower():
                user_exists = True

        if username == "" or email == "" or password == "":
            error = "Preencha todos os campos."
        elif "@" not in email or "." not in email.split("@")[-1]:
            error = "Digite um e-mail válido."
        elif len(email) > 120 or len(username) > 100 or len(password) > 100:
            error = "Confira o tamanho dos campos."
        elif user_exists:
            error = "Esse usuário ou e-mail já está cadastrado."
        else:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect("/login")

    return render_template("registration.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")


@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/login")

    categories = Category.query.filter_by(user_id=session["user_id"]).all()
    return render_template("home.html", categories=categories, error="")


@app.route("/categories/new", methods=["POST"])
def create_category():
    if "user_id" not in session:
        return redirect("/login")

    name = request.form["name"].strip()
    if name != "" and len(name) <= 60:
        category = Category(name=name, user_id=session["user_id"])
        db.session.add(category)
        db.session.commit()
        return redirect("/home")

    categories = Category.query.filter_by(user_id=session["user_id"]).all()
    return render_template(
        "home.html",
        categories=categories,
        error="O nome da categoria deve ter até 60 caracteres.",
    )


@app.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
def edit_category(category_id):
    if "user_id" not in session:
        return redirect("/login")

    # A consulta confere também o dono, não apenas o número da categoria.
    category = Category.query.filter_by(
        id=category_id, user_id=session["user_id"]
    ).first_or_404()
    error = ""

    if request.method == "POST":
        name = request.form["name"].strip()
        if name != "" and len(name) <= 60:
            category.name = name
            db.session.commit()
            return redirect("/home")
        error = "O nome da categoria deve ter até 60 caracteres."

    return render_template(
        "edit_category.html", category=category, error=error
    )


@app.route("/categories/<int:category_id>/delete", methods=["POST"])
def delete_category(category_id):
    if "user_id" not in session:
        return redirect("/login")

    category = Category.query.filter_by(
        id=category_id, user_id=session["user_id"]
    ).first_or_404()

    # Os links são excluídos primeiro porque pertencem a esta categoria.
    for link in category.links:
        db.session.delete(link)

    db.session.delete(category)
    db.session.commit()
    return redirect("/home")


@app.route("/categories/<int:category_id>/links/new", methods=["GET", "POST"])
def create_link(category_id):
    if "user_id" not in session:
        return redirect("/login")

    category = Category.query.filter_by(
        id=category_id, user_id=session["user_id"]
    ).first_or_404()
    error = ""

    if request.method == "POST":
        title = request.form["title"].strip()
        url = request.form["url"].strip()
        description = request.form["description"].strip()

        if (
            title != ""
            and len(title) <= 100
            and description != ""
            and len(url) <= 2048
            and (url.startswith("http://") or url.startswith("https://"))
        ):
            link = SavedLink(
                title=title,
                url=url,
                description=description,
                category_id=category.id,
            )
            db.session.add(link)
            db.session.commit()
            return redirect("/home")

        error = "Confira o título, o endereço e a descrição do link."

    return render_template(
        "link_form.html", category=category, saved_link=None, error=error
    )


@app.route("/links/<int:link_id>/edit", methods=["GET", "POST"])
def edit_link(link_id):
    if "user_id" not in session:
        return redirect("/login")

    # Confere se a categoria do link pertence à conta conectada.
    link = SavedLink.query.get_or_404(link_id)
    category = Category.query.filter_by(
        id=link.category_id, user_id=session["user_id"]
    ).first_or_404()
    error = ""

    if request.method == "POST":
        title = request.form["title"].strip()
        url = request.form["url"].strip()
        description = request.form["description"].strip()

        if (
            title != ""
            and len(title) <= 100
            and description != ""
            and len(url) <= 2048
            and (url.startswith("http://") or url.startswith("https://"))
        ):
            link.title = title
            link.url = url
            link.description = description
            db.session.commit()
            return redirect("/home")

        error = "Confira o título, o endereço e a descrição do link."

    return render_template(
        "link_form.html", category=category, saved_link=link, error=error
    )


@app.route("/links/<int:link_id>/delete", methods=["POST"])
def delete_link(link_id):
    if "user_id" not in session:
        return redirect("/login")

    link = SavedLink.query.get_or_404(link_id)
    Category.query.filter_by(
        id=link.category_id, user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(link)
    db.session.commit()
    return redirect("/home")


@app.route("/account", methods=["GET", "POST"])
def account():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get_or_404(session["user_id"])
    error = ""

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        users_db = User.query.all()
        user_exists = False
        email_exists = False

        for other_user in users_db:
            # Ignora a própria conta ao procurar nomes e e-mails repetidos.
            if other_user.id != user.id:
                if username.lower() == other_user.username.lower():
                    user_exists = True
                if email == other_user.email.lower():
                    email_exists = True

        if user.password != password:
            error = "Digite sua senha atual para confirmar as alterações."
        elif username == "":
            error = "Informe um nome de usuário."
        elif "@" not in email or "." not in email.split("@")[-1]:
            error = "Digite um e-mail válido."
        elif len(email) > 120 or len(username) > 100:
            error = "Confira o tamanho dos campos."
        elif user_exists:
            error = "Esse nome de usuário já está em uso."
        elif email_exists:
            error = "Esse e-mail já está em uso."
        else:
            user.username = username
            user.email = email
            session["username"] = username
            db.session.commit()
            return redirect("/account")

    return render_template("account.html", user=user, error=error)


@app.route("/account/password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get_or_404(session["user_id"])
    current_password = request.form["current_password"]
    new_password = request.form["new_password"]

    if user.password == current_password and new_password != "":
        user.password = new_password
        db.session.commit()
        return redirect("/account")

    return render_template(
        "account.html",
        user=user,
        error="Confira sua senha atual e informe uma nova senha.",
    )


@app.route("/account/delete", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get_or_404(session["user_id"])
    categories = Category.query.filter_by(user_id=user.id).all()

    # Remove primeiro os links e categorias ligados à conta.
    for category in categories:
        for link in category.links:
            db.session.delete(link)
        db.session.delete(category)

    db.session.delete(user)
    db.session.commit()
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
