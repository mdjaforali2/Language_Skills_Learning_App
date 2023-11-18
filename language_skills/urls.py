from django.urls import path
from . import views
from .views import build_listening_skills, build_speaking_skills, main_page, CreateListeningModuleView, AddQuestionsView, SubmitAnswersView, PreviousModuleView, NextModuleView

urlpatterns = [
    path('', main_page, name='main_page'),
    path('build-listening-skills/', build_listening_skills, name='build_listening_skills'),
    path('build-speaking-skills/', build_speaking_skills, name='build_speaking_skills'),
    path('create-listening-module/', CreateListeningModuleView.as_view(), name='create-listening-module'),
    path('add-question/<int:module_id>/', AddQuestionsView.as_view(), name='add_question'),
    path('module_learning/<int:module_id>/', views.module_learning, name='module_learning'),
    path('submit_answers/<int:module_id>/', SubmitAnswersView.as_view(), name='submit_answers'),
    path('previous_module/<int:module_id>/', PreviousModuleView.as_view(), name='previous_module'),
    path('next_module/<int:module_id>/', NextModuleView.as_view(), name='next_module'),
    # Add other URLs as needed
]