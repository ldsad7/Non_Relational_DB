import os

from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from wtforms import StringField, DateField

from app import app

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads')

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


class CreateForm(FlaskForm):
    first_name = StringField('Имя', validators=[])
    last_name = StringField('Фамилия', validators=[])
    patronymic = StringField('Отчество', validators=[])
    date_of_birth = DateField('Дата рождения', validators=[])
    photo = StringField('Фотография', validators=[])


class UpdateForm(FlaskForm):
    first_name = StringField('Имя', validators=[])
    last_name = StringField('Фамилия', validators=[])
    patronymic = StringField('Отчество', validators=[])
    date_of_birth = DateField('Дата рождения', validators=[])
    photo = StringField('Фотография', validators=[])
    id = StringField('id', validators=[])


class DeleteForm(FlaskForm):
    first_name = StringField('Имя', validators=[])
    last_name = StringField('Фамилия', validators=[])
    patronymic = StringField('Отчество', validators=[])
    date_of_birth = DateField('Дата рождения', validators=[])
    photo = StringField('Фотография', validators=[])
    id = StringField('id', validators=[])
