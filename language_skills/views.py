# language_skills/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import ListeningModule, ModuleQA, UserAnswer, SpeakingModule
from .forms import ListeningModuleForm, ModuleQAForm
from django import forms
import re

def main_page(request):
    return render(request, 'main.html', {})

def build_listening_skills(request):
    listening_modules = ListeningModule.objects.all()
    return render(request, 'build_listening_skills.html', {'listening_modules': listening_modules})

def build_speaking_skills(request):
    speaking_modules = SpeakingModule.objects.all()
    return render(request, 'build_speaking_skills.html', {'speaking_modules': speaking_modules})

class CreateListeningModuleView(CreateView):
    model = ListeningModule
    form_class = ListeningModuleForm
    template_name = 'create_listening_module.html'

    def form_valid(self, form):
        instance = form.save(commit=False)

        audio_file = self.request.FILES.get('audio_file')
        if audio_file:
            instance.audio_file = audio_file

        captions_file = self.request.FILES.get('captions')
        if captions_file:
            instance.captions = captions_file

        instance.save()

        module_id = instance.pk
        self.success_url = reverse_lazy('add_qeustion', kwargs={'module_id': module_id})

        return super().form_valid(form)
    
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.forms import ValidationError

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from .forms import ModuleQAForm
from .models import ListeningModule, ModuleQA

class AddQuestionsView(View):
    template_name = 'add_question.html'

    def get(self, request, module_id):
        module = get_object_or_404(ListeningModule, pk=module_id)
        qa_form = ModuleQAForm(initial={'module': module})
        context = {'module': module, 'qa_form': qa_form}
        return render(request, self.template_name, context)
    
    def post(self, request, module_id):
        module = get_object_or_404(ListeningModule, pk=module_id)

        # Create a mutable copy of the QueryDict
        mutable_data = request.POST.copy()
        
        # Explicitly set the module before saving the form
        qa_form = ModuleQAForm(mutable_data)
        qa_form.data['module'] = module.pk  # Set the module ID in the form data

        if qa_form.is_valid():
            qa = qa_form.save()
            return HttpResponseRedirect(reverse('add_question', args=[module_id]))
        else:
            # Print form errors to console for debugging
            print("Form Errors:", qa_form.errors)
            return HttpResponseBadRequest("Invalid form data")


def process_user_answers(post_data, module, user):
    user_answers = post_data.getlist('user_answer')

    for index, answer in enumerate(user_answers):
        question_id = post_data.get(f'question_{index + 1}_id')
        if question_id:
            question_id = int(question_id)
            question = get_object_or_404(ModuleQA, pk=question_id)
            UserAnswer.objects.update_or_create(
                user=user,
                module=module,
                question=question,
                defaults={'answer': answer}
            )

    return user_answers

def get_module_questions(module_id):
    try:
        module = ListeningModule.objects.get(id=module_id)
        return module.moduleqa_set.all()
    except ListeningModule.DoesNotExist:
        return []

# language_skills/views.py

# ... (other imports)

def get_module_audio_url(module_id):
    try:
        module = ListeningModule.objects.get(id=module_id)
        return module.audio_file.url
    except ListeningModule.DoesNotExist:
        return None

# ... (other functions and views)
# language_skills/views.py

# ... (other imports)

def get_module_script(module_id):
    try:
        module = ListeningModule.objects.get(id=module_id)
        return module.captions.read() if module.captions else None
    except ListeningModule.DoesNotExist:
        return None

# ... (other functions and views)




def module_learning(request, module_id):
    module = get_object_or_404(ListeningModule, pk=module_id)

    if not module:
        return redirect('home')

    module_questions = get_module_questions(module_id)
    module_audio = get_module_audio_url(module_id)
    module_script = get_module_script(module_id)
      # Split choices for multiple-choice questions
    for question in module_questions:
        if question.question_type == 'multiple_choice':
            question.choices = question.choices.split(',')

    context = {
        'module': module,
        'module_questions': module_questions,
        'module_audio': module_audio,
        'module_script': module_script,
    }
    return render(request, 'module_learning.html', context)

def format_script(script):
    # Decode the bytes object to a string
    script_str = script.decode('utf-8', errors='ignore')

    return script_str

def get_user_score(user_answers, module_qa_answers):
    # Calculate the score by counting correct answers
    correct_answers = sum(user_answer.lower() == module_answer.lower() for user_answer, module_answer in zip(user_answers, module_qa_answers))
    total_questions = len(module_qa_answers)
    score = (correct_answers / total_questions) * 100
    return score


from django.http import Http404
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import ListeningModule, ModuleQA, UserAnswer
from .forms import ModuleQAForm
from django.http import HttpResponseRedirect

class SubmitAnswersView(View):
    template_name = 'module_result.html'
    form_class = ModuleQAForm

    def get_context_data(self, module_id):
        module = get_object_or_404(ListeningModule, pk=module_id)
        module_questions = get_module_questions(module_id)
        module_audio = get_module_audio_url(module_id)
        module_script = get_module_script(module_id)

        module_qa_answers = ModuleQA.objects.filter(module=module_id).values_list('answer', flat=True)
        module_qa_questions = ModuleQA.objects.filter(module=module_id).values_list('question', flat=True)
        user_answers = UserAnswer.objects.filter(module=module_id, user=self.request.user).values_list('answer', flat=True)
        user_answers_stripped = [answer.strip() for answer in user_answers]
        matching_results = [user_answer.lower() == module_answer.lower() for user_answer, module_answer in zip(user_answers_stripped, module_qa_answers)]

        module_qa_data = zip(module_qa_questions, module_qa_answers, user_answers, matching_results)
        formatted_script = format_script(module_script)

        score = get_user_score(user_answers_stripped, module_qa_answers)

        context = {
            'module': module,
            'module_questions': module_questions,
            'module_audio': module_audio,
            'module_script': formatted_script,
            'module_qa_data': module_qa_data,
            'score' : score,
        }

        return context


    def get(self, request, module_id):
        context = self.get_context_data(module_id)
        return render(request, self.template_name, context)
    
    def post(self, request, module_id):
        # Retrieve the module for the user to answer
        module = get_object_or_404(ListeningModule, pk=module_id)

        # Iterate through the questions and save the user answers
        for key, value in request.POST.items():
            if key.startswith('user_answer_'):
                # Extract question_id from the key
                question_id = int(key[len('user_answer_'):])
                
                # Get the corresponding question
                question = get_object_or_404(ModuleQA, pk=question_id)

                # Save the user answer for the current question
                UserAnswer.objects.update_or_create(
                    user=request.user,
                    module=module,
                    question=question,
                    defaults={'answer': value}
                )

        return redirect('submit_answers', module_id=module_id)


from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy
from .models import ListeningModule

class PreviousModuleView(View):
    def get(self, request, module_id):
        current_module = get_object_or_404(ListeningModule, pk=module_id)
        previous_module = ListeningModule.objects.filter(order__lt=current_module.order).last()
        
        if previous_module:
            return redirect('module_learning', module_id=previous_module.pk)
        else:
            # If there is no previous module, redirect to the first module
            return redirect('module_learning', module_id=ListeningModule.objects.order_by('order').first().pk)

class NextModuleView(View):
    def get(self, request, module_id):
        current_module = get_object_or_404(ListeningModule, pk=module_id)
        next_module = ListeningModule.objects.filter(order__gt=current_module.order).first()
        
        if next_module:
            return redirect('module_learning', module_id=next_module.pk)
        else:
            # If there is no next module, redirect to the last module
            return redirect('module_learning', module_id=ListeningModule.objects.order_by('-order').first().pk)