"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import json
import re
import requests
import pytz

from datetime import datetime, timedelta
from urllib.parse import urlparse
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from django.dispatch import receiver
from core.utils.params import get_env
from io_storages.base_models import ImportStorage, ImportStorageLink, ExportStorage, ExportStorageLink
from io_storages.utils import get_uri_via_regex
from io_storages.serializers import StorageAnnotationSerializer
from tasks.models import Annotation
from oci import signer,object_storage
from oci.object_storage.models import CreatePreauthenticatedRequestDetails
from oci._vendor import urllib3

logger = logging.getLogger(__name__)
logging.getLogger('oci').setLevel(logging.DEBUG)
url_scheme = 'objectstorage'

class OracleCloudStorageMixin(models.Model):
    tenancy = models.TextField(_('tenancy'),null=True,blank=True,help_text='Tenancy used for OCI-Cloud Object Storage')
    bucket_name = models.TextField(_('bucket_name'),null=True,blank=True,help_text='Bucket used for OCI-Cloud Object Storage')
    bucket_prefix = models.TextField(_('bucket_prefix'),null=True,blank=True,help_text='Bucket Prefix name for the OCI-Cloud Object Storage')
    region = models.TextField(_('region'),null=True,blank=True,help_text='Region name for the OCI-Cloud Object Storage')

    ocid = models.TextField(_('ocid'),null=True,blank=True,help_text='Oracle ID for OCI-Cloud user')
    finger_print = models.TextField(_('finger_print'),null=True,blank=True,help_text='Fingerprint for the OCI-Cloud Object Storage')
    private_key = models.TextField(_('private_key'),null=True,blank=True,help_text='Private Key for OCI-Cloud user')
    pass_phrase = models.TextField(_('pass_phrase'),null=True,blank=True,help_text='Pass Phrase for user key')
    
    regex_filter = models.TextField(_('regex_filter'), null=True, blank=True,help_text='Cloud storage regex for filtering objects')
    pre_authenticated_url = models.TextField(_('pre_authenticated_url'), null=True, blank=True,help_text='Cloud storage regex for filtering objects')
    use_blob_urls = models.BooleanField(_('use_blob_urls'), default=False,help_text='Interpret objects as BLOBs and generate URLs')
    
    def get_config(self):
        config = {
            "user": str(self.ocid),
            "fingerprint":str(self.finger_print),
            "tenancy":str(self.tenancy),
            "region":str(self.region),
            "pass_phrase":str(self.pass_phrase),
            "key_file":"None"
        }
        return config
    def get_private_key(self,private_key):
        private_key = private_key.split()
        end_part = private_key[-4:]
        first_part = private_key[:4]
        first_part = ' '.join(first_part)
        end_part = ' '.join(end_part)
        pkey = """"""
        pkey+=first_part
        for el in private_key[4:-4]:
            pkey+="\n"
            pkey+=el
        pkey+="\n"
        pkey+=end_part
        private_key=pkey
        return private_key

    def get_signer(self):
        config = self.get_config()
        private_key = self.get_private_key(str(self.private_key))
        signer_instance = signer.Signer(
                tenancy=config['tenancy'],
                user=config['user'],
                fingerprint=config['fingerprint'],
                pass_phrase=config['pass_phrase'],
                private_key_file_location=None,
                private_key_content=private_key)
        return signer_instance
    
    def get_object_storage(self):
        config = self.get_config()
        signer = self.get_signer()
        objectstorage = object_storage.ObjectStorageClient(config,signer=signer)
        return objectstorage
    def get_namespace(self):
        return self.get_object_storage().get_namespace().data

    def validate_connection(self):
        endpoint = f"https://console.{self.region}.oraclecloud.com/object-storage/buckets/{self.get_namespace()}/{self.bucket_name}"
        try:
            response = requests.get(endpoint,auth=self.get_signer())
            if response.status_code != 200:
                raise RuntimeError(f"Endpoint returned reponse code {response.status_code} instead of [200]")
        except:
            raise RuntimeError(f"Invalid config object provided please verify {endpoint} {self.get_config()}")

class OracleCloudImportStorage(OracleCloudStorageMixin, ImportStorage):
    
    def iterkeys(self):
        object_storage = self.get_object_storage()
        namespace = self.get_namespace()
        bucket_name = self.bucket_name
        prefix = str(self.bucket_prefix) if self.bucket_prefix else ''
        regex = re.compile(str(self.regex_filter)) if self.regex_filter else None
        response = object_storage.list_objects(namespace,bucket_name,delimiter='/',fields='name,timeCreated')
        while response is not None:
            for obj in response.data.objects:
                if obj.name == (prefix.rstrip('/') + '/'):
                    continue
                if regex and not regex.match(obj.name):
                    logger.debug(obj.name + ' is skipped by regex filter')
                    continue
                yield obj.name
            if response.data.next_start_with is not None:
                response = object_storage.list_objects(namespace, bucket_name,delimiter='/',fields='name,timeCreated',start=response.data.next_start_with)
            else:
                response = None
    
    def get_data(self, key):
        namespace = self.get_namespace()
        object_storage = self.get_object_storage()
        pre_authenticated_url = self.pre_authenticated_url
        endpoint = f"{pre_authenticated_url}{key}"
        if self.use_blob_urls:
            return {settings.DATA_UNDEFINED_NAME: endpoint}
        
        http = urllib3.PoolManager()
        object_blob_str = http.request('GET', endpoint).data.decode('utf-8')
        value = json.loads(object_blob_str)
        if not isinstance(value, dict):
            raise ValueError(f"Error on key {key}: For {self.__class__.__name__} your JSON file must be a dictionary with one task.")  # noqa
        return value

    def scan_and_create_links(self):
        return self._scan_and_create_links(OracleCloudImportStorageLink)
    
class OracleCloudExportStorage(OracleCloudStorageMixin, ExportStorage):
    def save_annotation(self, annotation):
        logger.debug(f'Creating new object on {self.__class__.__name__} Storage {self} for annotation {annotation}')
        ser_annotation = self._get_serialized_data(annotation)
        namespace = self.get_namespace()
        with transaction.atomic():
            # Create export storage link
            try:
                link = OracleCloudExportStorageLink.create(annotation, self)
                key = str(self.prefix) + '/' + link.key if self.prefix else link.key
                self.object_stroage.put_object(namespace,self.bucket,key,json.dumps(ser_annotation).encode())
            except Exception as exc:
                logger.error(f"Can't export annotation {annotation} to OCI storage {self}. Reason: {exc}", exc_info=True)

@receiver(post_save, sender=Annotation)
def export_annotation_to_oci_storages(sender, instance, **kwargs):
    project = instance.task.project
    if hasattr(project, 'io_storages_ociexportstorages'):
        for storage in project.io_storages_ociexportstorages.all():
            logger.debug(f'Export {instance} to OCI storage {storage}')
            storage.save_annotation(instance)


class OracleCloudImportStorageLink(ImportStorageLink):
    storage = models.ForeignKey(OracleCloudImportStorage, on_delete=models.CASCADE, related_name='links')


class OracleCloudExportStorageLink(ExportStorageLink):
    storage = models.ForeignKey(OracleCloudExportStorage, on_delete=models.CASCADE, related_name='links')
