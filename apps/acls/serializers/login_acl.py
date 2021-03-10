from django.utils.translation import ugettext as _
from django.db.models.functions import Concat
from django.db.models import F, Value
from rest_framework import serializers
from common.drf.serializers import BulkModelSerializer
from ..models import LoginACL
from .. import const


__all__ = ['LoginACLSerializer', 'LoginACLUserRelationSerializer']


class LoginACLSerializer(BulkModelSerializer):
    ip_group = serializers.ListField(
        default=['*'], child=serializers.CharField(max_length=1024), label=_('IP'),
        help_text=const.ip_group_help_text + _('Domain name support.')
    )

    class Meta:
        model = LoginACL
        fields = [
            'id', 'name', 'priority', 'ip_group', 'users', 'action', 'comment', 'created_by',
            'date_created', 'date_updated'
        ]


class LoginACLUserRelationSerializer(BulkModelSerializer):
    loginacl_display = serializers.ReadOnlyField(source='loginacl.name')
    user_display = serializers.ReadOnlyField()

    class Meta:
        model = LoginACL.users.through
        fields = [
            'id', 'loginacl', 'user', 'loginacl_display', 'user_display'
        ]

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('user').annotate(
            user_display=Concat(F('user__name'), Value('('), F('user__username'), Value(')')),
        )
        return queryset
