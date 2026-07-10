from django import forms
from django.contrib.auth.models import User
from . import models

class QuestionForm(forms.Form):

    courseID = forms.ModelChoiceField(
        queryset=models.Course.objects.all(),
        empty_label="Course Name",
        to_field_name="id"
    )

    pdf = forms.FileField(label="Choose PDF")