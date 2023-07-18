from typing import Callable

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from common.utils import get_logger, reverse
from common.utils import lazyproperty
from common.utils.timezone import local_now_display
from notifications.backends import BACKEND
from notifications.models import SystemMsgSubscription
from notifications.notifications import SystemMessage, UserMessage
from terminal.models import Session, Command
from acls.models import CommandFilterACL, CommandGroup
from users.models import User

logger = get_logger(__name__)

__all__ = (
    'CommandAlertMessage', 'CommandExecutionAlert', 'StorageConnectivityMessage',
    'CommandWarningMessage'
)

CATEGORY = 'terminal'
CATEGORY_LABEL = _('Sessions')


class CommandAlertMixin:
    command: dict
    _get_message: Callable
    message_type_label: str

    def __str__(self):
        return str(self.message_type_label)

    @lazyproperty
    def subject(self):
        _input = self.command['input']
        if isinstance(_input, str):
            _input = _input.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')

        subject = self.message_type_label + ": %(cmd)s" % {
            'cmd': _input
        }
        return subject

    @classmethod
    def post_insert_to_db(cls, subscription: SystemMsgSubscription):
        """
        兼容操作，试图用 `settings.SECURITY_INSECURE_COMMAND_EMAIL_RECEIVER` 的邮件地址
        assets_systemuser_assets找到用户，把用户设置为默认接收者
        """
        from settings.models import Setting
        db_setting = Setting.objects.filter(
            name='SECURITY_INSECURE_COMMAND_EMAIL_RECEIVER'
        ).first()
        if db_setting:
            emails = db_setting.value
        else:
            emails = settings.SECURITY_INSECURE_COMMAND_EMAIL_RECEIVER
        emails = emails.split(',')
        emails = [email.strip().strip('"') for email in emails]

        users = User.objects.filter(email__in=emails)
        if users:
            subscription.users.add(*users)
            subscription.receive_backends = [BACKEND.EMAIL]
            subscription.save()


class CommandWarningMessage(CommandAlertMixin, UserMessage):
    message_type_label = _('Danger command warning')

    def __init__(self, user, command):
        super().__init__(user)
        self.command = command

    def get_html_msg(self) -> dict:
        command = self.command

        command_input = command['input']
        user = command['user']
        user_id = command.get('_user_id', '')
        asset = command['asset']
        asset_id = command.get('_asset_id', '')
        account = command['_account']
        account_id = command.get('_account_id', '')
        cmd_acl = command.get('_cmd_filter_acl')
        cmd_group = command.get('_cmd_group')
        session_id = command['session']
        org_id = command['org_id']
        org_name = command.get('_org_name') or org_id

        user_url = asset_url = account_url = session_url = ''
        if user_id:
            user_url = reverse(
                'users:user-detail', kwargs={'pk': user_id},
                api_to_ui=True, external=True, is_console=True
            ) + '?oid={}'.format(org_id)
        if asset_id:
            asset_url = reverse(
                'assets:asset-detail', kwargs={'pk': asset_id},
                api_to_ui=True, external=True, is_console=True
            ) + '?oid={}'.format(org_id)
        if account_id:
            account_url = reverse(
                'accounts:account-detail', kwargs={'pk': account_id},
                api_to_ui=True, external=True, is_console=True
            ) + '?oid={}'.format(org_id)
        if session_id:
            session_url = reverse(
                'api-terminal:session-detail', kwargs={'pk': session_id},
                external=True, api_to_ui=True
            ) + '?oid={}'.format(org_id)
            session_url = session_url.replace('/terminal/sessions/', '/audit/sessions/sessions/')

        # Command ACL
        cmd_acl_url = cmd_group_url = ''
        cmd_acl_name = cmd_group_name = ''
        if cmd_acl:
            cmd_acl_name = cmd_acl.name
            cmd_acl_url = settings.SITE_URL + f'/ui/#/console/perms/cmd-acls/{cmd_acl.id}/'
        if cmd_group:
            cmd_group_name = cmd_group.name
            cmd_group_url = settings.SITE_URL + f'/ui/#/console/perms/cmd-groups/{cmd_group.id}/'

        context = {
            'command': command_input,
            'user': user,
            'user_url': user_url,
            'asset': asset,
            'asset_url': asset_url,
            'account': account,
            'account_url': account_url,
            'cmd_filter_acl': cmd_acl_name,
            'cmd_filter_acl_url': cmd_acl_url,
            'cmd_group': cmd_group_name,
            'cmd_group_url': cmd_group_url,
            'session_url': session_url,
            'org': org_name,
        }

        message = render_to_string('terminal/_msg_command_warning.html', context)
        return {
            'subject': self.subject,
            'message': message
        }


class CommandAlertMessage(CommandAlertMixin, SystemMessage):
    category = CATEGORY
    category_label = CATEGORY_LABEL
    message_type_label = _('Danger command alert')

    def __init__(self, command):
        self.command = command

    @classmethod
    def gen_test_msg(cls):
        command = Command.objects.first()
        if not command:
            command = Command(user='test', asset='test', input='test', session='111111111')
        else:
            command['session'] = Session.objects.first().id
        return cls(command)

    def get_html_msg(self) -> dict:
        command = self.command
        session_detail_url = reverse(
            'api-terminal:session-detail', kwargs={'pk': command['session']},
            external=True, api_to_ui=True
        ) + '?oid={}'.format(self.command['org_id'])
        session_detail_url = session_detail_url.replace(
            '/terminal/sessions/', '/audit/sessions/sessions/'
        )
        level = Command.get_risk_level_str(command['risk_level'])
        items = {
            _("Asset"): command['asset'],
            _("User"): command['user'],
            _("Level"): level,
            _("Date"): local_now_display(),
        }
        context = {
            'items': items,
            'session_url': session_detail_url,
            "command": command['input'],
        }
        message = render_to_string('terminal/_msg_command_alert.html', context)
        return {
            'subject': self.subject,
            'message': message
        }


class CommandExecutionAlert(CommandAlertMixin, SystemMessage):
    category = CATEGORY
    category_label = CATEGORY_LABEL
    message_type_label = _('Batch danger command alert')

    def __init__(self, command):
        self.command = command

    @classmethod
    def gen_test_msg(cls):
        from assets.models import Asset
        from users.models import User
        cmd = {
            'input': 'ifconfig eth0',
            'assets': Asset.objects.all()[:10],
            'user': str(User.objects.first()),
            'risk_level': 5,
        }
        return cls(cmd)

    def get_html_msg(self) -> dict:
        command = self.command
        assets_with_url = []
        for asset in command['assets']:
            url = reverse(
                'assets:asset-detail', kwargs={'pk': asset.id},
                api_to_ui=True, external=True, is_console=True
            ) + '?oid={}'.format(asset.org_id)
            assets_with_url.append([asset, url])

        level = Command.get_risk_level_str(command['risk_level'])
        items = {
            _("User"): command['user'],
            _("Level"): level,
            _("Date"): local_now_display(),
        }

        context = {
            'items': items,
            'assets_with_url': assets_with_url,
            'command': command['input'],
        }
        message = render_to_string('terminal/_msg_command_execute_alert.html', context)
        return {
            'subject': self.subject,
            'message': message
        }


class StorageConnectivityMessage(SystemMessage):
    category = 'storage'
    category_label = _('Command and replay storage')
    message_type_label = _('Connectivity alarm')

    def __init__(self, errors):
        self.errors = errors

    @classmethod
    def post_insert_to_db(cls, subscription: SystemMsgSubscription):
        subscription.receive_backends = [b for b in BACKEND if b.is_enable]
        subscription.save()

    @classmethod
    def gen_test_msg(cls):
        from terminal.models import ReplayStorage
        replay = ReplayStorage.objects.first()
        errors = [{
            'msg': str(_("Test failure: Account invalid")),
            'type': replay.get_type_display(),
            'name': replay.name
        }]
        return cls(errors)

    def get_html_msg(self) -> dict:
        context = {
            'items': self.errors,
        }
        subject = str(_("Invalid storage"))
        message = render_to_string(
            'terminal/_msg_check_command_replay_storage_connectivity.html', context
        )
        return {
            'subject': subject,
            'message': message
        }
