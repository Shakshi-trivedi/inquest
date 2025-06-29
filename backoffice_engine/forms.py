from django import forms
from backoffice_engine.models import User
from .models import Feedback, Profile

class userRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name","email","password","address","phone","location","dob"]
        

class PDFUploadForm(forms.ModelForm):
    file = forms.FileField(label="Upload a PDF file of your Resume")

    class Meta:
        model = Profile
        fields = ['file']


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your feedback...'})
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'resume']
