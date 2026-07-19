# Generated migration for adding Category model and updating Novel model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("novels", "0002_initial"),
    ]

    operations = [
        # Create Category model
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=30, unique=True)),
                ("description", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name_plural": "Categories",
                "ordering": ["name"],
            },
        ),
        # Remove the old category CharField and add the new ForeignKey
        migrations.RemoveField(
            model_name="novel",
            name="category",
        ),
        migrations.AddField(
            model_name="novel",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="novels",
                to="novels.category",
            ),
        ),
        # Add index for category ForeignKey
        migrations.AddIndex(
            model_name="novel",
            index=models.Index(
                fields=["category"], name="novels_nove_categor_e3fd04_idx"
            ),
        ),
    ]
