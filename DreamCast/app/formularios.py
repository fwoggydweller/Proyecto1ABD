"""
Modulo en el que definimos los formularios de nuestra aplicacion
"""
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf import FlaskForm

class SignupForm(FlaskForm):
    """Formulario para el registro de usuarios"""
    email = StringField(
        'Email',
        [
            Email(message='No es un email válido.'),
            DataRequired()
        ]
    )
    password = PasswordField(
        'Contraseña',
        [
            DataRequired(message="Introduzca una contraseña."),
            Length(8, message="Contraseña mínimo de 8")
        ]
    )
    confirmPassword = PasswordField(
        'Repite Contraseña',
        [
            DataRequired(message="Please enter a password."),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    submit = SubmitField('Submit')


class SignInForm(FlaskForm):
    """Formulario para hacer login"""
    email = StringField(
        'Email',
        [
            Email(message='No es un email válido.'),
            DataRequired()
        ]
    )
    password = PasswordField(
        'Contraseña',
        [
            DataRequired(message="Introduzca una contraseña."),
        ]
    )

    submit = SubmitField('Submit')