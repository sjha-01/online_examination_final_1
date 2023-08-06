from django.forms import ModelForm
from .models import *
from django import forms


class PaperForm(ModelForm):
    class Meta:
        model = Paper
        fields = ['code', 'name', 'count', 'marks_per_cq',
                  'marks_per_wq', 'fm', 'modified_fm', 'duration', 'grace_time']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'count': forms.NumberInput(attrs={'class': 'form-control'}),
            'marks_per_cq': forms.NumberInput(attrs={'class': 'form-control'}),
            'marks_per_wq': forms.NumberInput(attrs={'class': 'form-control'}),
            'fm': forms.NumberInput(attrs={'class': 'form-control'}),
            'modified_fm': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM:SS'}),
            'grace_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM:SS'}),

        }

        labels = {
            'code': 'PAPER CODE',
            'name': 'PAPER NAME',
            'count': 'NO. OF QUESTIONS',
            'marks_per_cq': 'MARKS PER CORRECT ANSWER',
            'marks_per_wq': 'MARKS PER WRONG ANSWER',
            'fm': 'FULL MARKS',
            'modified_fm': ' MODIFIED FULL MARKS',
            'duration': 'DURATION OF EXAM',
            'grace_time': 'GRACE TIME',
        }
        help_texts = {
            'duration': 'Enter the duration in [HH:MM:SS] this format',
            'grace_time': 'Enter the grace time in [HH:MM:SS] this format',
        }


class PaperForm_unlocked(ModelForm):
    class Meta:
        model = Paper
        fields = ['modified_fm', 'grace_time']
        widgets = {
            'modified_fm': forms.NumberInput(attrs={'class': 'form-control'}),
            'grace_time': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'modified_fm': ' MODIFIED FULL MARKS',
            'grace_time': 'GRACE TIME',
        }
        help_texts = {
            'grace_time': 'Enter the grace time in [HH:MM:SS] this format',
        }


class Question_answerForm(ModelForm):
    class Meta:
        model = Question_answer
        fields = ['desc', 'img_path', 'op1', 'op2', 'op3',
                  'op4', 'correct_option']
        widgets = {
            'desc': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'img_path': forms.FileInput(attrs={'class': 'form-control'}),
            'op1': forms.TextInput(attrs={'class': 'form-control'}),
            'op2': forms.TextInput(attrs={'class': 'form-control'}),
            'op3': forms.TextInput(attrs={'class': 'form-control'}),
            'op4': forms.TextInput(attrs={'class': 'form-control'}),
            'correct_option': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'desc': 'QUESTION DESCRIPTION',
            'img_path': 'UPLOAD RELATED PICTURE(IF ANY)',
            'op1': 'OPTION NO.:1',
            'op2': 'OPTION NO.:2',
            'op3': 'OPTION NO.:3',
            'op4': 'OPTION NO.:4',
            'correct_option': 'CORRECT OPTION'
        }


class Question_answerForm_unlocked(ModelForm):
    class Meta:
        model = Question_answer
        fields = ['correct_option']
        widgets = {'correct_option': forms.Select(
            attrs={'class': 'form-control'}), }
        labels = {'correct_option': 'CORRECT OPTION'}
