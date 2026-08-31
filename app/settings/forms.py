from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length


class ProfileForm(FlaskForm):
    name = StringField(_l("Name"), validators=[DataRequired(), Length(max=120)])
    locale = SelectField(_l("Language"), choices=[("en", "English"), ("it", "Italiano")])
    submit = SubmitField(_l("Save changes"))


class NotificationsForm(FlaskForm):
    weekly_digest_enabled = BooleanField(_l("Weekly email with my top declining pages"))
    submit = SubmitField(_l("Save changes"))


class WhiteLabelForm(FlaskForm):
    white_label_enabled = BooleanField(_l("Hide LinkBayCMS branding from PDF/CSV exports"))
    submit = SubmitField(_l("Save changes"))


class PasswordForm(FlaskForm):
    current_password = PasswordField(_l("Current password"), validators=[DataRequired()])
    new_password = PasswordField(
        _l("New password"), validators=[DataRequired(), Length(min=8, message=_l("Minimum 8 characters."))]
    )
    confirm_password = PasswordField(
        _l("Confirm new password"),
        validators=[DataRequired(), EqualTo("new_password", message=_l("Passwords do not match."))],
    )
    submit = SubmitField(_l("Change password"))
