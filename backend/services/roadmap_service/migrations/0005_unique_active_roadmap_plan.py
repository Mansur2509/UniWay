from django.db import migrations, models


def deactivate_duplicate_active_plans(apps, schema_editor):
    roadmap_plan = apps.get_model("roadmap_service", "RoadmapPlan")
    user_ids = (
        roadmap_plan.objects.filter(active=True)
        .values_list("user_id", flat=True)
        .distinct()
    )
    for user_id in user_ids.iterator():
        active_ids = list(
            roadmap_plan.objects.filter(user_id=user_id, active=True)
            .order_by("-last_refreshed_at", "-id")
            .values_list("id", flat=True)
        )
        if len(active_ids) > 1:
            roadmap_plan.objects.filter(id__in=active_ids[1:]).update(active=False)


class Migration(migrations.Migration):
    dependencies = [("roadmap_service", "0004_roadmaptask_estimated_effort_and_more")]

    operations = [
        migrations.RunPython(
            deactivate_duplicate_active_plans,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="roadmapplan",
            constraint=models.UniqueConstraint(
                condition=models.Q(("active", True)),
                fields=("user",),
                name="unique_active_roadmap_plan_per_user",
            ),
        ),
    ]
