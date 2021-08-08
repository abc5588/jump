# -*- coding: utf-8 -*-
#
import json
import uuid
from datetime import datetime
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from common.mixins.models import CommonModelMixin
from orgs.mixins.models import OrgModelMixin
from orgs.models import Organization
from orgs.utils import tmp_to_root_org, tmp_to_org, get_current_org
from tickets.const import TicketTypeChoices, TicketActionChoices, TicketStatusChoices, \
    TicketApproveLevelChoices, TicketApproveStrategyChoices
from tickets.signals import post_change_ticket_action, post_or_update_change_template_approve
from tickets.handler import get_ticket_handler

__all__ = ['Ticket', 'Template', 'TemplateApprove', 'ModelJSONFieldEncoder']


class ModelJSONFieldEncoder(json.JSONEncoder):
    """ 解决一些类型的字段不能序列化的问题 """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(settings.DATETIME_DISPLAY_FORMAT)
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, type(_("ugettext_lazy"))):
            return str(obj)
        else:
            return super().default(obj)


class Ticket(CommonModelMixin, OrgModelMixin):
    title = models.CharField(max_length=256, verbose_name=_("Title"))
    type = models.CharField(
        max_length=64, choices=TicketTypeChoices.choices,
        default=TicketTypeChoices.general.value, verbose_name=_("Type")
    )
    meta = models.JSONField(encoder=ModelJSONFieldEncoder, default=dict, verbose_name=_("Meta"))
    status = models.CharField(
        max_length=16, choices=TicketStatusChoices.choices,
        default=TicketStatusChoices.open.value, verbose_name=_("Status")
    )
    action = models.CharField(
        choices=TicketActionChoices.choices, max_length=16,
        default=TicketActionChoices.open.value, verbose_name=_("Action")
    )
    approve_level = models.SmallIntegerField(
        default=TicketApproveLevelChoices.one.value, verbose_name=_('Approve level')
    )
    # 申请人
    applicant = models.ForeignKey(
        'users.User', related_name='applied_tickets', on_delete=models.SET_NULL, null=True,
        verbose_name=_("Applicant")
    )
    applicant_display = models.CharField(max_length=256, default='', verbose_name=_("Applicant display"))
    # 受理人列表
    assignees = models.ManyToManyField(
        'users.User', related_name='assigned_tickets', verbose_name=_("Assignees"), through='TicketAssignee'
    )
    process = models.JSONField(encoder=ModelJSONFieldEncoder, default=list, verbose_name=_("Process"))
    # 评论
    comment = models.TextField(default='', blank=True, verbose_name=_('Comment'))

    template = models.ForeignKey(
        'Template', related_name='templated_tickets', on_delete=models.SET_NULL, null=True,
        verbose_name=_("Template")
    )

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return '{}({})'.format(self.title, self.applicant_display)

    # type
    @property
    def type_apply_asset(self):
        return self.type == TicketTypeChoices.apply_asset.value

    @property
    def type_apply_application(self):
        return self.type == TicketTypeChoices.apply_application.value

    @property
    def type_login_confirm(self):
        return self.type == TicketTypeChoices.login_confirm.value

    # status
    @property
    def status_closed(self):
        return self.status == TicketStatusChoices.closed.value

    @property
    def status_open(self):
        return self.status == TicketStatusChoices.open.value

    @property
    def action_open(self, action=None):
        return action == TicketActionChoices.open.value

    @property
    def cur_assignees(self):
        return self.m2m_ticket_users.filter(approve_level=self.approve_level)

    @property
    def processor(self, level=None):
        if not level:
            level = self.approve_level
        m2m_ticket_users = self.m2m_ticket_users.filter(approve_level=level, is_processor=True).first()
        return m2m_ticket_users.user if m2m_ticket_users else None

    def set_status_closed(self):
        self.status = TicketStatusChoices.closed.value

    def create_related_assignees(self):
        template_approve = self.get_template_approve(self.approve_level)
        ticket_assignee_list = []
        assignees = template_approve.assignees.all()
        ticket_assignee_model = self.assignees.through
        for assignee in assignees:
            ticket_assignee_list.append(ticket_assignee_model(
                ticket=self, user=assignee, approve_level=self.approve_level))
        ticket_assignee_model.objects.bulk_create(ticket_assignee_list)
        return assignees

    def create_process_node_info(self, assignees):
        return {
            'approve_level': self.approve_level,
            'action': TicketActionChoices.open.value,
            'assignees': [assignee.id for assignee in assignees],
            'assignees_display': [str(assignee) for assignee in assignees]
        }

    def change_action_and_processor(self, action, user):
        cur_assignees = self.cur_assignees
        cur_assignees.update(action=action)
        open = TicketActionChoices.open.value
        if action != open:
            cur_assignees.filter(user=user).update(is_processor=True)
        else:
            self.applicant = user

    # action changed
    def open(self, applicant):
        action = TicketActionChoices.open.value
        self._change_action(action, applicant)

    def approve(self, processor):
        action = TicketActionChoices.approve.value
        self._change_action(action, processor)

    def reject(self, processor):
        action = TicketActionChoices.reject.value
        self._change_action(action, processor)

    def close(self, processor):
        action = TicketActionChoices.close.value
        self._change_action(action, processor)

    def _change_action(self, action, user):
        self.change_action_and_processor(action, user)
        self.save()
        post_change_ticket_action.send(sender=self.__class__, ticket=self, action=action)

    # ticket
    # def has_assignee(self, assignee):
    #     return self.assignees.filter(id=assignee.id).exists()

    @classmethod
    def get_user_related_tickets(cls, user):
        queries = Q(applicant=user) | Q(assignees=user)
        tickets = cls.all().filter(queries).distinct()
        return tickets

    def get_template_approve(self, level):
        return self.template.templated_approves.filter(approve_level=level).first()

    @classmethod
    def all(cls):
        with tmp_to_root_org():
            return Ticket.objects.all()

    def save(self, *args, **kwargs):
        """ 确保保存的org_id的是自身的值 """
        with tmp_to_org(self.org_id):
            return super().save(*args, **kwargs)

    @property
    def handler(self):
        return get_ticket_handler(ticket=self)

    # body
    @property
    def body(self):
        _body = self.handler.get_body()
        return _body


class TicketAssignee(CommonModelMixin):
    ticket = models.ForeignKey(
        'Ticket', related_name='m2m_ticket_users', on_delete=models.CASCADE, verbose_name='Ticket'
    )
    user = models.ForeignKey(
        'users.User', related_name='m2m_user_tickets', on_delete=models.CASCADE, verbose_name='User'
    )
    approve_level = models.SmallIntegerField(
        default=TicketApproveLevelChoices.one.value, choices=TicketApproveLevelChoices.choices,
        verbose_name=_('Approve level')
    )
    is_processor = models.BooleanField(default=False)
    action = models.CharField(
        choices=TicketActionChoices.choices, max_length=16,
        default=TicketActionChoices.open.value, verbose_name=_("Action")
    )

    class Meta:
        verbose_name = _('Ticket assignee')

    def __str__(self):
        return '{0.user.name}({0.user.username})_{0.approve_level}'.format(self)


class Template(CommonModelMixin, OrgModelMixin):
    title = models.CharField(max_length=256, verbose_name=_("Title"))
    type = models.CharField(
        max_length=64, choices=TicketTypeChoices.choices,
        default=TicketTypeChoices.general.value, verbose_name=_("Type")
    )

    def save(self, *args, **kwargs):
        """ 确保保存的org_id的是自身的值 """
        with tmp_to_org(self.org_id):
            return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Ticket template')

    def __str__(self):
        return '{}({})'.format(self.title, self.type)

    def is_root(self):
        return self.org_id == Organization.ROOT_ID

    @property
    def get_level_all_count(self):
        return self.templated_approves.count()

    @classmethod
    def get_org_related_templates(cls):
        org = get_current_org()
        templates = cls.objects.filter(org_id=org.id)
        cur_template_types = templates.values_list('type', flat=True)
        diff_global_templates = cls.objects.filter(org_id=org.ROOT_ID).exclude(type__in=cur_template_types)
        return templates | diff_global_templates


class TemplateApprove(CommonModelMixin):
    approve_level = models.SmallIntegerField(
        default=TicketApproveLevelChoices.one.value, choices=TicketApproveLevelChoices.choices,
        verbose_name=_('Approve level')
    )
    approve_strategy = models.CharField(
        max_length=64, default=TicketApproveStrategyChoices.system.value,
        choices=TicketApproveStrategyChoices.choices,
        verbose_name=_('Approve strategy')
    )
    # 受理人列表
    assignees = models.ManyToManyField(
        'users.User', related_name='assigned_template_approve', verbose_name=_("Assignees")
    )
    assignees_display = models.JSONField(
        encoder=ModelJSONFieldEncoder, default=list, verbose_name=_('Assignees display')
    )
    ticket_template = models.ForeignKey(
        Template, related_name='templated_approves', on_delete=models.SET_NULL, null=True,
        verbose_name=_("Template")
    )

    class Meta:
        verbose_name = _('Ticket template approve level')

    def __str__(self):
        return '{}({})'.format(self.id, self.approve_level)

    @classmethod
    def change_assignees_display(cls, qs):
        post_or_update_change_template_approve.send(sender=cls, qs=qs)
