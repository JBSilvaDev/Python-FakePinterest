from fake_pinterest import database, app
from fake_pinterest.models import Usuario, Foto

with app.app_context():
    database.create_all()