from datetime import datetime
from rest_framework import serializers


class MetaListdata(object):
    def __init__(self, status='ok', data=None, message=None, total=0):
        self.status = status
        self.data = data
        self.message = message
        self.total = total

    def serialized_data(self):
        return MetadataListSerializer(self).data


class Metadata(object):
    def __init__(self, status='ok', data=None, message=None):
        self.status = status
        self.data = data
        self.message = message
        self.time = datetime.now()

    def serialized_data(self):
        return MetadataSerializer(self).data

    def serialized_list_data(self):
        return MetadataListSerializer(self).data


class MetadataSerializer(serializers.Serializer):
    data = serializers.DictField()
    status = serializers.CharField(default='ok', max_length=10)
    message = serializers.CharField(max_length=100)
    time = serializers.DateTimeField(default=datetime.now())


class MetadataListSerializer(serializers.Serializer):
    data = serializers.ListField()
    status = serializers.CharField(default='ok', max_length=10)
    message = serializers.CharField(max_length=100)
    time = serializers.DateTimeField(default=datetime.now())
    total = serializers.IntegerField(default=0)
