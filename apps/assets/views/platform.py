# -*- coding: utf-8 -*-
from django.views import generic
from django.utils.translation import ugettext as _

from common.permissions import PermissionsMixin, IsSuperUser
from ..models import Platform
from ..forms import PlatformForm


class PlatformListView(PermissionsMixin, generic.TemplateView):
    template_name = 'assets/platform_list.html'
    permission_classes = (IsSuperUser,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app': _('Assets'),
            'action': _("Platform list"),
        })
        return context


class PlatformCreateView(PermissionsMixin, generic.CreateView):
    form_class = PlatformForm
    permission_classes = (IsSuperUser,)
    template_name = 'assets/platform_create_update.html'
    model = Platform

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app': _('Assets'),
            'action': _("Create platform"),
        })
        return context


class PlatformUpdateView(generic.UpdateView):
    form_class = PlatformForm
    permission_classes = (IsSuperUser,)
    model = Platform
    template_name = 'assets/platform_create_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app': _('Assets'),
            'action': _("Update platform"),
            'type': 'update',
        })
        return context
