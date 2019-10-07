from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from .models import Client
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count
from .models import Category
from django.views.generic.detail import DetailView
from students.forms import ClientEnrollForm
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)

class OwnerClientMixin(OwnerMixin):
    model = Client
    fields = ['category', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_client_list')

class OwnerClientEditMixin(OwnerClientMixin, OwnerEditMixin):
    fields = ['category', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_client_list')
    template_name = 'clients/manage/client/form.html'

class ManageClientListView(ListView):
    model = Client
    template_name = 'clients/manage/client/list.html'

    def get_queryset(self):
        qs = super(ManageClientListView, self).get_queryset()
        return qs.filter(owner=self.request.user)

class ClientCreateView(PermissionRequiredMixin, OwnerClientEditMixin, CreateView):
    permission_required = 'clients.add_client'

class ClientUpdateView(PermissionRequiredMixin, OwnerClientEditMixin, UpdateView):
    permission_required = 'clients.change_client'

class ClientDeleteView(PermissionRequiredMixin, OwnerClientMixin, DeleteView):
    template_name = 'clients/manage/client/delete.html'
    success_url = reverse_lazy('manage_client_list')
    permission_required = 'clients.delete_client'

class ClientModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'clients/manage/module/formset.html'
    client = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.client, data=data)

    def dispatch(self, request, pk):
        self.client = get_object_or_404(Client, id=pk, owner=request.user)
        return super(ClientModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'client': self.client, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_client_list')
        return self.render_to_response({'client': self.client, 'formset': formset})

class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'clients/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['file']:
            return apps.get_model(app_label='clients', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module, id=module_id, client__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super(ContentCreateUpdateView,
           self).dispatch(request, module_id, model_name, id)
    
    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})
    
class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__client__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'clients/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, client__owner=request.user)
        return self.render_to_response({'module': module})

class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, client__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__client__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ClientListView(TemplateResponseMixin, View):
    model = Client
    template_name = 'clients/client/list.html'
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, category=None):
        categories = Category.objects.annotate(total_clients=Count('clients'))
        clients = Client.objects.annotate(total_modules=Count('modules'))
        if category:
            category = get_object_or_404(Category, slug=category)
            clients = clients.filter(category=category)
        return self.render_to_response({'categories': categories, 'category': category, 'clients': clients})

class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client/detail.html'

class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ClientDetailView,
                        self).get_context_data(**kwargs)
        context['enroll_form'] = ClientEnrollForm(
                                   initial={'client':self.object})
        return context

def login_success(request):
    """
    Redirects users based on whether they are in the admins group
    """
    if request.user.is_staff:
        # user is an admin
        return redirect("manage_client_list")
    else:
        return redirect("student_client_list")