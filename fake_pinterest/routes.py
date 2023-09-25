from fake_pinterest.models import Usuario, Foto
from flask import config, render_template, url_for, redirect
from fake_pinterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from fake_pinterest.forms import FormLogin, FormCriarConta, FormFoto
import os
from werkzeug.utils import secure_filename


@app.route("/", methods=["GET", "POST"])
def home_page():
    """Rota inicial"""
    formLogin = FormLogin()
    if formLogin.validate_on_submit():
        usuario = Usuario.query.filter_by(
            email=formLogin.email.data,
        ).first()
        if usuario and  bcrypt.check_password_hash(usuario.senha, formLogin.senha.data):
            login_user(usuario)
        return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("home_page.html", form=formLogin)


@app.route("/criarconta", methods=["GET", "POST"])
def criar_conta():
    """Formulario"""
    formCriarConta = FormCriarConta()
    if formCriarConta.validate_on_submit():
        senha = bcrypt.generate_password_hash(formCriarConta.senha.data)
        usuario = Usuario(
            username=formCriarConta.username.data,
            senha=senha,
            email=formCriarConta.email.data,
        )
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("criarconta.html", form=formCriarConta)


@app.route("/perfil/<id_usuario>", methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    """Pagina de perfil"""
    if int(id_usuario) == int(current_user.id):
        # User ver e edita seu proprio perfil
        form_foto = FormFoto()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename)
            # Salvar arquivo na pasta
            caminho_projeto = os.path.abspath(os.path.dirname(__file__))
            path = os.path.join(caminho_projeto, app.config["UPLOAD_FOLDER"], nome_seguro)
            arquivo.save(path)
            # Salvar nome seguro do arquivo no bd
            foto = Foto(imagem = nome_seguro, id_usuario = current_user.id)
            database.session.add(foto)
            database.session.commit()
        return render_template("perfil.html", usuario=current_user, form=form_foto)
    else:
        # User apenas ver perfis
        usuario = Usuario.query.get(int(id_usuario))
        return render_template("perfil.html", usuario=usuario, form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home_page"))

@app.route("/feed")
@login_required
def feed():
    fotos=Foto.query.order_by(Foto.data_criacao).all()
    return render_template('feed.html', fotos=fotos)