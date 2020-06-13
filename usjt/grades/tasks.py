from celery import task

from .scrapers import usjt
from . import models


@task(
    autoretry_for=[Exception],
    max_retries=5,
    retry_backoff=True,
)
def get_grades():
    data = usjt.scrape()

    changes = []
    for semester, classes in data.items():
        for name, info in classes.items():
            new_info = {
                'professors': info['Professors'],
                'absences': info['Absences'],
                'grade': info['Total'],
                'A1': info['A1'],
                'A2': info['A2'],
                'D1': info['D1'],
                'D2': info['D2'],
                'D3': info['D3'],
            }
            class_, created = models.Class.objects.get_or_create(
                semester=semester,
                name=name,
                defaults=new_info
            )
            if not created:
                anything_has_changed = False
                old_values = class_.to_json()
                for k, v in new_info.items():
                    if old_values[k] != v:
                        anything_has_changed = True
                        break
                if anything_has_changed:
                    class_.history.append(old_values)
                    class_.save()
                    class_.update(**new_info)
                    changes.append(class_.id)
            else:
                changes.append(class_.id)

    notify_changes.delay(classes_id=changes)


def notify_changes(classes_id):
    classes = [models.Class.objects.get(pk=i).to_json() for i in classes_id]

    # Custom code here
