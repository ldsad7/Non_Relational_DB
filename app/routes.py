from flask import render_template, flash, redirect, url_for, request, jsonify

from app import app, redis
from app.forms import CreateForm, UpdateForm, DeleteForm

FIELDS = ['last_name', 'first_name', 'patronymic', 'date_of_birth', 'photo']


@app.route('/')
@app.route('/index')
def index():
    message = request.args.get('message') or ''
    return render_template('index.html', message=message)


@app.route('/create', methods=['GET', 'POST'])
def create():
    form = CreateForm()
    data = form.data
    if form.validate_on_submit():
        del data['csrf_token']
        data['date_of_birth'] = str(data['date_of_birth'])
        redis.create_men([{key: value or '' for key, value in data.items()}])
        return redirect(url_for('.index', message='Пользователь успешно добавлен'))
    else:
        flash('Введены некорректные данные')
    return render_template('create_form.html', form=form)


@app.route('/read', methods=['GET', 'POST'])
def read():
    return render_template('read_page.html', men=redis.read_all_men())


@app.route('/update', methods=['GET', 'POST'])
def update():
    form = UpdateForm()
    data = form.data
    print(data)
    if form.validate_on_submit():
        del data['csrf_token']
        data['date_of_birth'] = str(data['date_of_birth'])
        id_ = data.pop('id')
        redis.update_men([id_], [data])
        return redirect(url_for('.index', message='Пользователь успешно обновлён'))
    else:
        flash('Введены некорректные данные')
    return render_template('update_form.html', form=form)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    form = DeleteForm()
    data = form.data
    if form.validate_on_submit():
        id_ = data.pop('id')
        redis.delete_men([id_])
        return redirect(url_for('index', message='Пользователь успешно удалён'))
    else:
        flash('Введены некорректные данные')
    return render_template('delete_form.html', form=form)


@app.route('/sort', methods=['GET', 'POST'])
def sort():
    selected = []
    field_1 = request.args.get('field_1', None, type=str)
    field_2 = request.args.get('field_2', None, type=str)
    field_3 = request.args.get('field_3', None, type=str)
    fields = [field_1, field_2, field_3]
    for field in fields:
        if field is not None:
            selected.append(FIELDS.index(field) + 1)
        else:
            selected.append(1)
    if field_1 is not None or field_2 is not None or field_3 is not None:
        result = redis.sort_men(fields)
        # NB: uncomment?
        # result = sorted(redis.read_all_men(), key=lambda elem: tuple(elem[field] for field in fields))
    else:
        result = redis.read_all_men()
    return render_template('sort_page.html', men=result, selected=selected)


@app.route('/group', methods=['GET', 'POST'])
def group():
    data = redis.group_men()
    return render_template('group_page.html', data=data)


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route('/_filter_men')
def filter_men():
    field = request.args.get('field', None, type=str)
    value = request.args.get('value', None, type=str)
    result = redis.filter_men(field, value)
    print(f'result: {result}')
    return jsonify(result=result)
