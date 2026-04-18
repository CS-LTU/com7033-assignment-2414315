"""
forms.py

All WTForms for StrokeGuard.
CSRF token automatically included by Flask-WTF on every form.
Server-side validation runs even if JS is disabled.
"""

import re
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField,
    FloatField, SubmitField, EmailField, BooleanField
)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo,
    NumberRange, ValidationError, Regexp, Optional
)


# ── Auth Forms ────────────────────────────────────────────────────────────────

class RegistrationForm(FlaskForm):
    """Registration with strong password policy."""

    username = StringField("Username", validators=[
        DataRequired(),
        Length(min=3, max=30, message="Username must be 3–30 characters."),
        Regexp(r"^[A-Za-z0-9_]+$",
               message="Only letters, numbers, and underscores allowed."),
    ])
    email = EmailField("Email", validators=[
        DataRequired(), Email(), Length(max=120),
    ])
    password = PasswordField("Password", validators=[
        DataRequired(), Length(min=8, message="Minimum 8 characters."),
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password", message="Passwords must match."),
    ])
    submit = SubmitField("Register")

    def validate_password(self, field):
        """Enforce: uppercase, lowercase, digit, special character."""
        pwd = field.data
        if not re.search(r"[A-Z]", pwd):
            raise ValidationError("Must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", pwd):
            raise ValidationError("Must contain at least one lowercase letter.")
        if not re.search(r"\d", pwd):
            raise ValidationError("Must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_]", pwd):
            raise ValidationError("Must contain at least one special character.")


class LoginForm(FlaskForm):
    username    = StringField("Username",  validators=[DataRequired()])
    password    = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit      = SubmitField("Sign In")


# ── Patient Form ──────────────────────────────────────────────────────────────

class PatientForm(FlaskForm):
    """
    Add / Edit patient form.
    Choices match the actual Kaggle dataset values exactly.
    """

    gender = SelectField("Gender", validators=[DataRequired()], choices=[
        ("Male", "Male"), ("Female", "Female"), ("Other", "Other"),
    ])
    age = FloatField("Age (years)", validators=[
        DataRequired(), NumberRange(min=0, max=120),
    ])
    hypertension = SelectField("Hypertension", validators=[DataRequired()], choices=[
        ("0", "No"), ("1", "Yes"),
    ])
    heart_disease = SelectField("Heart Disease", validators=[DataRequired()], choices=[
        ("0", "No"), ("1", "Yes"),
    ])
    ever_married = SelectField("Ever Married", validators=[DataRequired()], choices=[
        ("Yes", "Yes"), ("No", "No"),
    ])
    work_type = SelectField("Work Type", validators=[DataRequired()], choices=[
        ("children",      "Children"),
        ("Govt_job",      "Government Job"),
        ("Never_worked",  "Never Worked"),
        ("Private",       "Private"),
        ("Self-employed", "Self-employed"),
    ])
    Residence_type = SelectField("Residence Type", validators=[DataRequired()], choices=[
        ("Rural", "Rural"), ("Urban", "Urban"),
    ])
    avg_glucose_level = FloatField("Avg Glucose Level (mg/dL)", validators=[
        DataRequired(), NumberRange(min=0, max=600),
    ])
    bmi = FloatField("BMI", validators=[
        Optional(), NumberRange(min=5, max=100),
    ])
    smoking_status = SelectField("Smoking Status", validators=[DataRequired()], choices=[
        ("formerly smoked", "Formerly Smoked"),
        ("never smoked",    "Never Smoked"),
        ("smokes",          "Smokes"),
        ("Unknown",         "Unknown"),
    ])
    stroke = SelectField("Stroke", validators=[DataRequired()], choices=[
        ("0", "No"), ("1", "Yes"),
    ])
    submit = SubmitField("Save Patient")


# ── Search Form ───────────────────────────────────────────────────────────────

class PatientSearchForm(FlaskForm):
    """Filter form for patient list — no CSRF needed (GET request)."""

    gender = SelectField("Gender", choices=[
        ("", "All Genders"), ("Male", "Male"),
        ("Female", "Female"), ("Other", "Other"),
    ])
    stroke = SelectField("Stroke", choices=[
        ("", "All"), ("1", "Had Stroke"), ("0", "No Stroke"),
    ])
    submit = SubmitField("Filter")
