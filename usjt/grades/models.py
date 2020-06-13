from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.postgres.indexes import GinIndex


class Class(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    semester = models.CharField(max_length=10)
    name = models.CharField(max_length=256)
    professors = ArrayField(models.CharField(max_length=256))
    absences = models.IntegerField()
    grade = models.FloatField()
    A1 = models.FloatField(null=True)
    A2 = models.FloatField(null=True)
    D1 = models.FloatField(null=True)
    D2 = models.FloatField(null=True)
    D3 = models.FloatField(null=True)

    history = ArrayField(JSONField(), default=list)

    class Meta:
        indexes = [
            GinIndex(fields=['professors']),
            models.Index(fields=['name']),
            models.Index(fields=['semester']),
            models.Index(fields=['absences']),
            models.Index(fields=['grade']),
            models.Index(fields=['updated']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['semester', 'name'], name='course'),
        ]

    def to_dict(self):
        return {
            'pk': self.pk,
            'created': self.created,
            'updated': self.updated,
            'semester': self.semester,
            'name': self.name,
            'professors': self.professors,
            'absences': self.absences,
            'grade': self.grade,
            'A1': self.A1,
            'A2': self.A2,
            'D1': self.D1,
            'D2': self.D2,
            'D3': self.D3,
            'history': self.history,
        }
