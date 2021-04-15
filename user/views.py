from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.contrib.auth.forms import UserCreationForm

class RegisterView(CreateView):
    model = User
    template_name = 'user/register.html'
    form_class = UserCreationForm

    def get_success_url(self):
        return reverse('user:login')