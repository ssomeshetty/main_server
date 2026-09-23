from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_add_timestamp_to_publicrecord_and_clean_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialdeclaration',
            name='source_organization',
            field=models.CharField(blank=True, max_length=255, verbose_name='Source Organization'),
        ),
        migrations.AddField(
            model_name='financialdeclaration',
            name='source_retrieved_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Source Retrieved At'),
        ),
        migrations.AddField(
            model_name='financialdeclaration',
            name='verification_notes',
            field=models.TextField(blank=True, verbose_name='Verification Notes'),
        ),
        migrations.AddField(
            model_name='financialdeclaration',
            name='verification_status',
            field=models.CharField(
                choices=[
                    ('unknown', 'Unknown'),
                    ('scraped', 'Scraped'),
                    ('validated', 'Validated'),
                    ('human_verified', 'Human Verified'),
                    ('stale', 'Stale'),
                    ('rejected', 'Rejected'),
                ],
                db_index=True,
                default='unknown',
                max_length=20,
                verbose_name='Verification Status',
            ),
        ),
    ]