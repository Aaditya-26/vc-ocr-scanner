from django.db import models


class ContactMaster(models.Model):
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    raw_text = models.TextField()
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    image_path = models.CharField(max_length=500)
    is_duplicate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contact_master'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.company_name or 'N/A'}"
