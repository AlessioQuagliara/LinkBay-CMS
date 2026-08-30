from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class RegisterForm(FlaskForm):
    name = StringField(_l("Name"), validators=[DataRequired(), Length(max=120)])
    email = StringField(_l("Email"), validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField(
        _l("Password"), validators=[DataRequired(), Length(min=8, message=_l("Minimum 8 characters."))]
    )
    confirm_password = PasswordField(
        _l("Confirm password"),
        validators=[DataRequired(), EqualTo("password", message=_l("Passwords do not match."))],
    )
    submit = SubmitField(_l("Create account"))


class LoginForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    submit = SubmitField(_l("Sign in"))


class OtpForm(FlaskForm):
    code = StringField(
        _l("Code"),
        validators=[
            DataRequired(),
            Regexp(r"^\d{6}$", message=_l("Enter the 6-digit code.")),
        ],
    )
    submit = SubmitField(_l("Verify"))
