# Copyright (c) 2013 Shiv Shankar Dayal
# This file is part of Kunjika.
#
# Kunjika is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Kunjika is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

from flask_wtf import Form, RecaptchaField
from wtforms import (BooleanField, StringField, PasswordField, validators, TextAreaField,
                        RadioField, SelectField)


class RegistrationForm(Form):
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Length(min=8, max=32)
    ])
    confirm = PasswordField('Confirm Password')
    fname = StringField('First Name', [validators.Length(min=2, max=32), validators.DataRequired()])
    lname = StringField('Last Name', [validators.Length(min=2, max=32), validators.DataRequired()])
    email1 = StringField('Email', [validators.Length(min=5, max=48), validators.DataRequired(),
                                 validators.Email(message='Either email is invalid or already registered.')])
    recaptcha = RecaptchaField(validators.DataRequired())


class LoginForm(Form):
    email = StringField('Email', [validators.Length(min=4, max=64), validators.DataRequired(),
                                validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=8, max=32)
    ])


class OpenIDForm(Form):
    googleid = StringField('GoogleID', [validators.Length(min=2, max=64), validators.Optional()])
    yahooid = StringField('YahooID', [validators.Length(min=2, max=64), validators.Optional()])


class QuestionForm(Form):
    question = StringField('Question', [validators.Length(min=4, max=200), validators.DataRequired()])
    description = TextAreaField('', [validators.Length(min=20, max=50000), validators.DataRequired()])
    tags = StringField('Tags', [validators.Length(min=1, max=100), validators.DataRequired()])


class AnswerForm(Form):
    answer = TextAreaField('', [validators.Length(min=20, max=50000), validators.DataRequired()])


class CommentForm(Form):
    comment = TextAreaField('', [validators.Length(min=20, max=5000), validators.DataRequired()])


class ProfileForm(Form):
    fname = StringField('First Name', [validators.Length(min=2, max=32), validators.DataRequired()])
    lname = StringField('Last Name', [validators.Length(min=2, max=32), validators.DataRequired()])
    email1 = StringField('Email', [validators.Length(min=5, max=48), validators.DataRequired(),
                                 validators.Email(message='Either email is invalid or already registered.')])
    recaptcha = RecaptchaField(validators.DataRequired())


class TagForm(Form):
    info = TextAreaField('', [validators.Length(min=20, max=5000), validators.DataRequired()])


class PasswordResetForm(Form):
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Length(min=8, max=32)
    ])
    confirm = PasswordField('Confirm Password')


class EmailForm(Form):
    email = StringField('Email', [validators.Length(min=5, max=48),validators.DataRequired(),
                                 validators.Email(message='Email is invalid')])


class PollForm(Form):
    poll_answers = SelectField('How many choices do you want?' , choices=[('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), \
                                                                    ('6', '6'), ('7', '7'),  ('8', '8'), ('9', '9'), \
                                                                    ('10', '10')])

class OQForm(Form):
    oq_answers = SelectField('How many choices do you want?' , choices=[('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), \
                                                                    ('6', '6')])

class SearchForm(Form):
    query = TextAreaField('', [validators.Length(min=20, max=1000), validators.DataRequired()])


class EditProfileForm(Form):
    fname = StringField('First Name', [validators.Length(min=2, max=32), validators.DataRequired()])
    lname = StringField('Last Name', [validators.Length(min=2, max=32), validators.DataRequired()])
    website = StringField('Website', [validators.Length(min=2, max=160), validators.optional()])
    location = StringField('Location', [validators.Length(min=2, max=60), validators.optional()])
    about_me = TextAreaField('', [validators.Length(min=20, max=5000), validators.optional()])
    skills = StringField('Skills', [validators.Length(min=1, max=100), validators.optional()])


class BulkEmailForm(Form):
    subject = StringField('Subject', [validators.Length(min=2, max=200), validators.optional()])
    bulk_mail = TextAreaField('Body', [validators.Length(min=20, max=10000), validators.optional()])


class BOQForm(Form):
    tech = SelectField('Technology:', choices=[('c', 'C'), ('cpp', 'C++'), ('java', 'Java'), ('perl', 'Perl'), \
        ('python', 'Python')])
    cat = SelectField('Category:', choices=[('arrays', 'Arrays'), ('basics', 'Basics'), ('bitop', 'Bitwise Operators'),
            ('cli', 'Command Line Arguments'), ('const', 'Const'), ('control_flow', 'Control Flow'),
            ('funcs', 'Functions'), ('io', 'IO'), ('lib', 'Library Functions'), ('memalloc', 'Memory Allocation'),
            ('oae', 'Operators and Expressions'), ('pointers', 'Pointers'), ('strings', 'Strings'),
            ('sue', 'Structures, Unions and Eums'), ('threading', 'Multithreading'), ('typedef', 'Typedef'),
            ('vararg', 'Variable Arguments')])


class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=4, max=200), validators.DataRequired()])
    content = TextAreaField('', [validators.Length(min=20, max=4000000), validators.DataRequired()])
    tags = StringField('Tags', [validators.Length(min=1, max=100), validators.DataRequired()])


class ContactForm(Form):
    name = StringField('', [validators.Length(min=2, max=32), validators.DataRequired()])
    email = StringField('', [validators.Length(min=5, max=48), validators.DataRequired(),
                                 validators.Email(message='Either email is invalid or already registered.')])
    recaptcha = RecaptchaField(validators.DataRequired())
    message = TextAreaField('', [validators.Length(min=20, max=5000), validators.DataRequired()])