from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div
from .models import ListeningModule, ModuleQA

class ListeningModuleForm(forms.ModelForm):
    class Meta:
        model = ListeningModule
        fields = ['title', 'youtube_url', 'audio_file', 'captions']



class ModuleQAForm(forms.ModelForm):
    class Meta:
        model = ModuleQA
        fields = ['question', 'answer', 'module', 'question_type', 'choices']
        widgets = {'module': forms.HiddenInput()}

    # You can customize form widgets or attributes here if needed
