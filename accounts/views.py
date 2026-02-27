from django.views.generic import FormView, TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from .forms import LoginForm, RegisterForm
from .models import UserProfile


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('accounts:regular')

    def form_valid(self, form):
        email, password = form.cleaned_data['email'], form.cleaned_data['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, "Email or password incorrect")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        form.clean()
        return super().form_invalid(form)

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = "register.html"
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        email, password = form.cleaned_data['email'], form.cleaned_data['password']
        first_name, last_name = form.cleaned_data['first_name'], form.cleaned_data['last_name']
        phone = form.cleaned_data['phone']
        profile_type = form.cleaned_data['type']
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        UserProfile.objects.create(
            user=user,
            phone=phone,
            profile_type=profile_type
        )
        print(email, password, phone, first_name, last_name)
        return super().form_valid(form)

    def form_invalid(self, form):
        form.clean()
        return super().form_invalid(form)


class RegularProfileView(TemplateView):
    template_name = 'regular_user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        userdata = User.objects.get(id=self.request.user.id)
        profiledata = UserProfile.objects.get(user=self.request.user.id)
        context['profiledata'] = {'user': userdata, 'profile': profiledata}
        return context
