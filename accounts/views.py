from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import StoreUserCreationForm

class SignUpView(CreateView):
    form_class = StoreUserCreationForm
    success_url = reverse_lazy('base')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('base')
