from flask_wtf import FlaskForm

from wtforms import IntegerField, StringField, SelectField, BooleanField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class NewGameForm(FlaskForm):
    valid_name = Length(min=3, max=30, message="укажите ваше имя (от 3 до 30 символов!")
    name = StringField('Ваше имя: ', validators=[DataRequired(), valid_name],
                       render_kw={'placeholder': 'укажите свое имя'})

    valid_size = NumberRange(min=10, max=30, message="размер поля от 10 до 30!")
    height = IntegerField('Высота', validators=[DataRequired(), valid_size])
    width = IntegerField('Ширина', validators=[DataRequired(), valid_size])

    difficult = SelectField('Сложность', choices=[(0, 'easy'), (1, 'normal'), (3, 'high')], coerce=int)
    valid_count = NumberRange(min=1, max=10, message="количество выходов от 1 до 10!")
    exit_count = IntegerField('Кол-во выходов', validators=[DataRequired(), valid_count])
    ninja = BooleanField('Ниндзя на поле')

    btn_submit = SubmitField('Новая игра', render_kw={'class': 'btn btn-primary'})
    btn_index = SubmitField(label='На главную')  # , render_kw={"onclick": 'location.href=\"/index.html\"'}
