"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from io_storages.oci.models import OracleCloudImportStorage, OracleCloudExportStorage
from io_storages.oci.serializers import OracleCloudImportStorageSerializer, OracleCloudExportStorageSerializer
from io_storages.api import (
    ImportStorageListAPI, ImportStorageDetailAPI, ImportStorageSyncAPI, ExportStorageListAPI, ExportStorageDetailAPI,
    ImportStorageValidateAPI, ExportStorageValidateAPI, ImportStorageFormLayoutAPI, ExportStorageFormLayoutAPI
)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Get all import storage',
    operation_description='Get a list of all OracleCloud import storage connections.'
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Create import storage',
    operation_description='Create a new OracleCloud import storage connection.'
))
class OracleCloudImportStorageListAPI(ImportStorageListAPI):
    queryset = OracleCloudImportStorage.objects.all()
    serializer_class = OracleCloudImportStorageSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Get import storage',
    operation_description='Get a specific OracleCloud import storage connection.'
))
@method_decorator(name='patch', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Update import storage',
    operation_description='Update a specific OracleCloud import storage connection.'
))
@method_decorator(name='delete', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Delete import storage',
    operation_description='Delete a specific OracleCloud import storage connection.'
))
class OracleCloudImportStorageDetailAPI(ImportStorageDetailAPI):
    queryset = OracleCloudImportStorage.objects.all()
    serializer_class = OracleCloudImportStorageSerializer


@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Sync import storage',
    operation_description='Sync tasks from an OracleCloud import storage connection.'
))
class OracleCloudImportStorageSyncAPI(ImportStorageSyncAPI):
    serializer_class = OracleCloudImportStorageSerializer


@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Validate import storage',
    operation_description='Validate a specific OracleCloud import storage connection.'
))
class OracleCloudImportStorageValidateAPI(ImportStorageValidateAPI):
    serializer_class = OracleCloudImportStorageSerializer


@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Validate export storage',
    operation_description='Validate a specific OracleCloud export storage connection.'
))
class OracleCloudExportStorageValidateAPI(ExportStorageValidateAPI):
    serializer_class = OracleCloudExportStorageSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Get all export storage',
    operation_description='Get a list of all OracleCloud export storage connections.'
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Create export storage',
    operation_description='Create a new OracleCloud export storage connection to store annotations.'
))
class OracleCloudExportStorageListAPI(ExportStorageListAPI):
    queryset = OracleCloudExportStorage.objects.all()
    serializer_class = OracleCloudExportStorageSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Get export storage',
    operation_description='Get a specific OracleCloud export storage connection.'
))
@method_decorator(name='patch', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Update export storage',
    operation_description='Update a specific OracleCloud export storage connection.'
))
@method_decorator(name='delete', decorator=swagger_auto_schema(
    tags=['Storage'],
    operation_summary='OracleCloud: Delete export storage',
    operation_description='Delete a specific OracleCloud export storage connection.'
))
class OracleCloudExportStorageDetailAPI(ExportStorageDetailAPI):
    queryset = OracleCloudExportStorage.objects.all()
    serializer_class = OracleCloudExportStorageSerializer


class OracleCloudImportStorageFormLayoutAPI(ImportStorageFormLayoutAPI):
    pass


class OracleCloudExportStorageFormLayoutAPI(ExportStorageFormLayoutAPI):
    pass
