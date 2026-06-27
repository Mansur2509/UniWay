# Generated migration for structured profile items

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile_service', '0003_studentprofile_activities_studentprofile_essay_stage_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('role', models.CharField(blank=True, max_length=150)),
                ('organization', models.CharField(blank=True, max_length=150)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('hours_per_week', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('weeks_per_year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('scale', models.CharField(blank=True, choices=[('school', 'School-level'), ('city', 'City-level'), ('regional', 'Regional-level'), ('national', 'National-level'), ('international', 'International-level')], default='school', max_length=20)),
                ('impact_number', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True, max_length=1500)),
                ('proof_link', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_activities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Honor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('issuing_organization', models.CharField(blank=True, max_length=150)),
                ('level', models.CharField(blank=True, max_length=100)),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('result_rank', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True, max_length=1500)),
                ('proof_link', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_honors', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Olympiad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('subject', models.CharField(blank=True, max_length=100)),
                ('level', models.CharField(blank=True, max_length=100)),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('result', models.CharField(blank=True, max_length=100)),
                ('rank_percentile', models.CharField(blank=True, max_length=50)),
                ('description', models.TextField(blank=True, max_length=1500)),
                ('proof_link', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_olympiads', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Sport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sport_name', models.CharField(max_length=150)),
                ('level', models.CharField(blank=True, max_length=100)),
                ('years_trained', models.CharField(blank=True, max_length=100)),
                ('peak_result', models.CharField(blank=True, max_length=150)),
                ('competition_name', models.CharField(blank=True, max_length=150)),
                ('description', models.TextField(blank=True, max_length=1500)),
                ('proof_link', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_sports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ResearchProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('field', models.CharField(blank=True, max_length=150)),
                ('research_question', models.TextField(blank=True, max_length=500)),
                ('sample_size', models.CharField(blank=True, max_length=100)),
                ('countries_region', models.CharField(blank=True, max_length=150)),
                ('methods_used', models.CharField(blank=True, max_length=150)),
                ('current_stage', models.CharField(blank=True, choices=[('planning', 'Planning'), ('active', 'Active'), ('completed', 'Completed'), ('published', 'Published')], default='active', max_length=20)),
                ('manuscript_link', models.URLField(blank=True)),
                ('publication_status', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True, max_length=1500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_research_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PortfolioProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('project_type', models.CharField(blank=True, max_length=100)),
                ('link', models.URLField(blank=True)),
                ('tech_stack', models.CharField(blank=True, max_length=150)),
                ('users_impact', models.CharField(blank=True, max_length=150)),
                ('status', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True, max_length=1500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_portfolio_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EssayDraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('essay_type', models.CharField(blank=True, max_length=100)),
                ('school_program', models.CharField(blank=True, max_length=150)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('in_progress', 'In Progress'), ('submitted', 'Submitted'), ('reviewed', 'Reviewed')], default='draft', max_length=20)),
                ('word_limit', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('draft_status', models.CharField(blank=True, max_length=100)),
                ('last_reviewed_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_essays', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
