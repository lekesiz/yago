from django.db import models

class Project(models.Model):
    project_idea = models.CharField(max_length=255, null=False, blank=False)
    executive_summary = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.project_idea