# backend/api/serializers.py
"""
Django REST Framework serializers for converting model instances to JSON.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    """
    Serializer for Dataset model.
    Includes computed fields for raw_data and summary as Python objects.
    """
    
    raw_data_parsed = serializers.SerializerMethodField()
    summary_parsed = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id', 
            'name', 
            'uploaded_at', 
            'uploaded_by_name',
            'record_count',
            'raw_data_parsed', 
            'summary_parsed'
        ]
    
    def get_raw_data_parsed(self, obj):
        """Return raw data as list of dictionaries"""
        return obj.get_raw_data()
    
    def get_summary_parsed(self, obj):
        """Return summary as dictionary"""
        return obj.get_summary()
    
    def get_uploaded_by_name(self, obj):
        """Return username of uploader"""
        return obj.uploaded_by.username if obj.uploaded_by else 'Anonymous'


class DatasetListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing datasets (without full data).
    Used for the history endpoint to reduce payload size.
    """
    
    summary_parsed = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = ['id', 'name', 'uploaded_at', 'record_count', 'summary_parsed']
    
    def get_summary_parsed(self, obj):
        return obj.get_summary()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user