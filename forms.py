from flask_wtf import FlaskForm

from wtforms import IntegerField, StringField, SelectField, BooleanField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class NewGameForm(FlaskForm):
    valid_name = Length(min=3, max=30, message="укажите ваше имя (от 3 до 30 символов!")
    name = StringField('Ваше имя: ', validators=[DataRequired(), valid_name],
                       render_kw={'placeholder': 'укажите свое имя', 'id': 'id_name'})

    valid_size = NumberRange(min=10, max=30, message="размер поля от 10 до 30!")
    height = IntegerField('Высота', validators=[DataRequired(), valid_size],
                          render_kw={'placeholder': 'укажите высоту лабиринта', 'id': 'id_height'})
    width = IntegerField('Ширина', validators=[DataRequired(), valid_size],
                         render_kw={'placeholder': 'укажите ширину лабиринта', 'id': 'id_width'})

    difficult = SelectField('Сложность', choices=[(30, 'легко'), (50, 'нормально'), (70, 'сложно')], coerce=int,
                            render_kw={'placeholder': 'укажите плотность стен в лабиринте', 'id': 'id_difficult'})
    valid_count = NumberRange(min=1, max=10, message="количество выходов от 1 до 10!")
    exit_count = IntegerField('Кол-во выходов', validators=[DataRequired(), valid_count],
                              render_kw={'placeholder': 'укажите количество выходов лабиринта', 'id': 'id_exit_count'})
    ninja = BooleanField('Ниндзя на поле',
                         render_kw={'id': 'id_ninja'})

    btn_submit = SubmitField('Начать игру', render_kw={'class': 'btn btn-primary'})
    # btn_index = SubmitField(label='На главную')  # , render_kw={"onclick": 'location.href=\"/index.html\"'}
    # btn_game = SubmitField(label='Вернуться в игру', render_kw={'class': 'btn btn-primary', 'disable': ''})  # , render_kw={"onclick": 'location.href=\"/index.html\"'}
