# coding: utf-8
#


from django import forms
from django.utils.translation import ugettext_lazy as _

from terminal.models import CommandStorage


__all__ = ['CommandStorageCreateUpdateForm']


class CommandStorageTypeESForm(forms.ModelForm):
    es_hosts = forms.CharField(
        max_length=128, label=_('Hosts'), required=False,
        help_text=_(
            """
            Tips: If there are multiple hosts, separate them with a comma (,) 
            <br>
            eg: http://www.jumpserver.a.com,http://www.jumpserver.b.com
            """
        )
    )
    es_index = forms.CharField(
        max_length=128, label=_('Index'), required=False
    )
    es_doc_type = forms.CharField(
        max_length=128, label=_('Doc type'), required=False
    )


class CommandStorageTypeForms(CommandStorageTypeESForm):
    pass


class CommandStorageCreateUpdateForm(CommandStorageTypeForms, forms.ModelForm):

    class Meta:
        model = CommandStorage
        fields = ['name', 'type']
