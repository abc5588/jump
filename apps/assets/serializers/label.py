# -*- coding: utf-8 -*-
#
from rest_framework import serializers

from common.serializers import AdaptedBulkListSerializer
from orgs.mixins import BulkOrgResourceModelSerializer

from ..models import Label


class LabelSerializer(BulkOrgResourceModelSerializer):
    asset_count = serializers.SerializerMethodField()

    class Meta:
        model = Label
        fields = [
            'id', 'name', 'value', 'category', 'is_active', 'comment',
            'date_created', 'asset_count', 'assets', 'get_category_display'
        ]
        extra_kwargs = {
            'category': {'read_only': True},
            'date_created': {'read_only': True},
            'asset_count': {'read_only': True},
            'get_category_display': {'read_only': True},
        }
        list_serializer_class = AdaptedBulkListSerializer

    @staticmethod
    def get_asset_count(obj):
        return obj.assets.count()

    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)
        fields.extend(['get_category_display'])
        return fields


class LabelDistinctSerializer(BulkOrgResourceModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = Label
        fields = ("name", "value")

    @staticmethod
    def get_value(obj):
        labels = Label.objects.filter(name=obj["name"])
        return ', '.join([label.value for label in labels])
