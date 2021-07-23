"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import os
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from io_storages.serializers import ImportStorageSerializer, ExportStorageSerializer
from io_storages.oci.models import OracleCloudImportStorage, OracleCloudExportStorage


class OracleCloudImportStorageSerializer(ImportStorageSerializer):
    type = serializers.ReadOnlyField(default=os.path.basename(os.path.dirname(__file__)))
    class Meta:
        model = OracleCloudImportStorage
        fields = '__all__'

    def validate(self, data):
        data = super(OracleCloudImportStorageSerializer, self).validate(data)
        storage = OracleCloudImportStorage(**data)
        try:
            storage.validate_connection()
        except Exception as exc:
            raise ValidationError(exc)
        return data


class OracleCloudExportStorageSerializer(ExportStorageSerializer):
    type = serializers.ReadOnlyField(default=os.path.basename(os.path.dirname(__file__)))

    class Meta:
        model = OracleCloudExportStorage
        fields = '__all__'
