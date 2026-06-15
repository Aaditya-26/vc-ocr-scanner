from rest_framework import serializers
from .models import ContactMaster


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMaster
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_duplicate',
                            'raw_text', 'confidence_score', 'image_path']


class ContactUpdateSerializer(serializers.ModelSerializer):
    """Used for PUT — allows editing extracted fields manually."""

    class Meta:
        model = ContactMaster
        fields = ['name', 'designation', 'company_name', 'mobile',
                  'email', 'website', 'address']
