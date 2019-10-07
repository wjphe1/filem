from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ClientEnrollForm, CustomUserCreationForm
from django.views.generic.list import ListView
from clients.models import Client
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect
from django.contrib import messages

class StudentClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'students/client/list.html'

    def get_queryset(self):
        qs = super(StudentClientListView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        result = super(StudentRegistrationView,
                       self).form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result

class StudentEnrollClientView(LoginRequiredMixin, FormView):
    client = None
    form_class = ClientEnrollForm

    def form_valid(self, form):
        self.client = form.cleaned_data['client']
        self.client.students.add(self.request.user)
        return super(StudentEnrollClientView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_client_detail', args=[self.client.id])

class StudentClientDetailView(DetailView):
    model = Client
    template_name = 'students/client/detail.html'

    def get_queryset(self):
        qs = super(StudentClientDetailView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super(StudentClientDetailView,
                        self).get_context_data(**kwargs)
        # get client object
        client = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = client.modules.get(id=self.kwargs['module_id'])
        else:
            # get first module
            context['module'] = client.modules.all().first()
        return context

def staff_register(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')
 
    else:
        f = CustomUserCreationForm()
 
    return render(request, 'students/student/registration.html', {'form': f})