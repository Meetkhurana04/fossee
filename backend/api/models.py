# backend/api/models.py
"""
Database models for storing uploaded datasets and their summaries.
The Dataset model stores CSV data and computed statistics.
"""

from django.db import models
from django.contrib.auth.models import User
import json


class Dataset(models.Model):
    """
    Stores information about each uploaded CSV file.
    - Keeps raw data as JSON for easy retrieval
    - Stores computed summary statistics
    - Tracks upload time for history ordering
    """
    
    name = models.CharField(max_length=255)  # Original filename
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    # Store the raw CSV data as JSON string
    raw_data = models.TextField()
    
    # Summary statistics stored as JSON
    summary = models.TextField()
    
    # Count of equipment records
    record_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-uploaded_at']  # Most recent first
    
    def __str__(self):
        return f"{self.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_raw_data(self):
        """Parse and return the raw data as Python list"""
        return json.loads(self.raw_data)
    
    def get_summary(self):
        """Parse and return the summary as Python dict"""
        return json.loads(self.summary)
    
    @classmethod
    def cleanup_old_records(cls, keep_count=5):
        """
        Keep only the last 'keep_count' datasets.
        Called after each new upload to maintain the limit.
        """
        datasets = cls.objects.all()
        if datasets.count() > keep_count:
            # Get IDs of records to keep
            ids_to_keep = datasets[:keep_count].values_list('id', flat=True)
            # Delete the rest
            cls.objects.exclude(id__in=list(ids_to_keep)).delete()