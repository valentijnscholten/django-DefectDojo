# Generated by Django 2.2.16 on 2020-11-08 08:01

from django.db import migrations, models
import logging

logger = logging.getLogger(__name__)


class Migration(migrations.Migration):

    dependencies = [
        ('dojo', '0062_jira_refactor'),
    ]

    def move_jira_creation_changed(apps, schema_editor):
        # We can't import models directly as it may be a newer
        # version than this migration expects. We use the historical version.
        logger.info('migrating finding.jira_creation and jira_change fields to JIRA_Issue model')
        Finding = apps.get_model('dojo', 'Finding')
        JIRA_Issue = apps.get_model('dojo', 'JIRA_Issue')
        for jira_issue in JIRA_Issue.objects.all().select_related('finding'):
            # try:
            if jira_issue.finding:
                logger.debug('populating jira_issue: %s', jira_issue.jira_key)
                jira_issue.jira_creation = jira_issue.finding.jira_creation
                jira_issue.jira_change = jira_issue.finding.jira_change
                jira_issue.save()
            else:
                logger.debug('no finding: skipping jira_issue: %s', jira_issue.jira_key)
            # except Finding.DoesNotExist:
            #     logger.info('exception: skipping jira_issue: %s', jira_issue.jira_key)

    def populate_jira_project(apps, schema_editor):
        # We can't import models directly as it may be a newer
        # version than this migration expects. We use the historical version.
        logger.info('populating jira_issue.jira_project to point to jira configuration of the product in defect dojo')
        JIRA_Issue = apps.get_model('dojo', 'JIRA_Issue')
        for jira_issue in JIRA_Issue.objects.all().select_related('jira_project').prefetch_related('finding__test__engagement__product'):
            # try:
            if not jira_issue.jira_project and jira_issue.finding:
                logger.info('populating jira_issue from finding: %s', jira_issue.jira_key)
                # jira_project = jira_helper.get_jira_project(jira_issue.finding) #  jira_helper will use wrong Finding model version
                jira_projects = jira_issue.finding.test.engagement.product.jira_project_set.all()
                jira_project = jira_projects[0] if len(jira_projects) > 0 else None

                logger.debug('jira_project: %s', jira_project)
                jira_issue.jira_project = jira_project
                jira_issue.save()
            elif not jira_issue.jira_project and jira_issue.engagement:
                logger.debug('populating jira_issue from engagement: %s', jira_issue.jira_key)
                jira_projects = jira_issue.engagement.product.jira_project_set.all()
                jira_project = jira_projects[0] if len(jira_projects) > 0 else None
                logger.debug('jira_project: %s', jira_project)
                jira_issue.jira_project = jira_project
                jira_issue.save()
            elif not jira_issue.jira_project:
                logger.info('skipping %s as there is no finding or engagment', jira_issue.jira_key)
            # except Exception as e:
            #     logger.exception(e)
            #     logger.debug('populating jira_project field: skipping jira_issue: %s', jira_issue.jira_key)
        # raise ValueError('bla')

    def populate_jira_instance_name_if_empty(apps, schema_editor):
        # We can't import models directly as it may be a newer
        # version than this migration expects. We use the historical version.
        logger.info('populating JIRA_Instance.configuration_name with url if empty')
        JIRA_Instance = apps.get_model('dojo', 'JIRA_Instance')
        for jira_instance in JIRA_Instance.objects.all():
            # try:
            if not jira_instance.configuration_name:
                jira_instance.configuration_name = jira_instance.url
                jira_instance.save()
            else:
                logger.debug('configuration_name already set for %i %s', jira_instance.id, jira_instance.url)
            # except Exception as e:
            #     logger.exception(e)
            #     logger.debug('populating name for jira_instance: skipping jira_instance: %s', jira_instance.name)
        logger.info('done with data migration, now removing some fields which may take a while depending on the amount of findings')

    def show_info(apps, schema_editor):
        logger.info('this migration should have run succesfully. if not, there is a Django Management command to manually run the data conversion')
        logger.info('for docker-compose execute: docker-compose exec uwsgi ./manage.py jira_refactor_data_migration')

    operations = [
        migrations.RunPython(move_jira_creation_changed),
        migrations.RunPython(populate_jira_project),
        migrations.RunPython(populate_jira_instance_name_if_empty),

        migrations.RemoveField(
            model_name='finding',
            name='jira_change',
        ),
        migrations.RemoveField(
            model_name='finding',
            name='jira_creation',
        ),
        migrations.AlterField(
            model_name='child_rule',
            name='match_field',
            field=models.CharField(choices=[('id', 'id'), ('title', 'title'), ('date', 'date'), ('cwe', 'cwe'), ('cve', 'cve'), ('cvssv3', 'cvssv3'), ('url', 'url'), ('severity', 'severity'), ('description', 'description'), ('mitigation', 'mitigation'), ('impact', 'impact'), ('steps_to_reproduce', 'steps_to_reproduce'), ('severity_justification', 'severity_justification'), ('references', 'references'), ('test', 'test'), ('is_template', 'is_template'), ('active', 'active'), ('verified', 'verified'), ('false_p', 'false_p'), ('duplicate', 'duplicate'), ('duplicate_finding', 'duplicate_finding'), ('out_of_scope', 'out_of_scope'), ('under_review', 'under_review'), ('review_requested_by', 'review_requested_by'), ('under_defect_review', 'under_defect_review'), ('defect_review_requested_by', 'defect_review_requested_by'), ('is_Mitigated', 'is_Mitigated'), ('thread_id', 'thread_id'), ('mitigated', 'mitigated'), ('mitigated_by', 'mitigated_by'), ('reporter', 'reporter'), ('numerical_severity', 'numerical_severity'), ('last_reviewed', 'last_reviewed'), ('last_reviewed_by', 'last_reviewed_by'), ('line_number', 'line_number'), ('sourcefilepath', 'sourcefilepath'), ('sourcefile', 'sourcefile'), ('param', 'param'), ('payload', 'payload'), ('hash_code', 'hash_code'), ('line', 'line'), ('file_path', 'file_path'), ('component_name', 'component_name'), ('component_version', 'component_version'), ('static_finding', 'static_finding'), ('dynamic_finding', 'dynamic_finding'), ('created', 'created'), ('scanner_confidence', 'scanner_confidence'), ('sonarqube_issue', 'sonarqube_issue'), ('unique_id_from_tool', 'unique_id_from_tool'), ('sast_source_object', 'sast_source_object'), ('sast_sink_object', 'sast_sink_object'), ('sast_source_line', 'sast_source_line'), ('sast_source_file_path', 'sast_source_file_path'), ('nb_occurences', 'nb_occurences')], max_length=200),
        ),
        migrations.AlterField(
            model_name='rule',
            name='applied_field',
            field=models.CharField(choices=[('id', 'id'), ('title', 'title'), ('date', 'date'), ('cwe', 'cwe'), ('cve', 'cve'), ('cvssv3', 'cvssv3'), ('url', 'url'), ('severity', 'severity'), ('description', 'description'), ('mitigation', 'mitigation'), ('impact', 'impact'), ('steps_to_reproduce', 'steps_to_reproduce'), ('severity_justification', 'severity_justification'), ('references', 'references'), ('test', 'test'), ('is_template', 'is_template'), ('active', 'active'), ('verified', 'verified'), ('false_p', 'false_p'), ('duplicate', 'duplicate'), ('duplicate_finding', 'duplicate_finding'), ('out_of_scope', 'out_of_scope'), ('under_review', 'under_review'), ('review_requested_by', 'review_requested_by'), ('under_defect_review', 'under_defect_review'), ('defect_review_requested_by', 'defect_review_requested_by'), ('is_Mitigated', 'is_Mitigated'), ('thread_id', 'thread_id'), ('mitigated', 'mitigated'), ('mitigated_by', 'mitigated_by'), ('reporter', 'reporter'), ('numerical_severity', 'numerical_severity'), ('last_reviewed', 'last_reviewed'), ('last_reviewed_by', 'last_reviewed_by'), ('line_number', 'line_number'), ('sourcefilepath', 'sourcefilepath'), ('sourcefile', 'sourcefile'), ('param', 'param'), ('payload', 'payload'), ('hash_code', 'hash_code'), ('line', 'line'), ('file_path', 'file_path'), ('component_name', 'component_name'), ('component_version', 'component_version'), ('static_finding', 'static_finding'), ('dynamic_finding', 'dynamic_finding'), ('created', 'created'), ('scanner_confidence', 'scanner_confidence'), ('sonarqube_issue', 'sonarqube_issue'), ('unique_id_from_tool', 'unique_id_from_tool'), ('sast_source_object', 'sast_source_object'), ('sast_sink_object', 'sast_sink_object'), ('sast_source_line', 'sast_source_line'), ('sast_source_file_path', 'sast_source_file_path'), ('nb_occurences', 'nb_occurences')], max_length=200),
        ),
        migrations.AlterField(
            model_name='rule',
            name='match_field',
            field=models.CharField(choices=[('id', 'id'), ('title', 'title'), ('date', 'date'), ('cwe', 'cwe'), ('cve', 'cve'), ('cvssv3', 'cvssv3'), ('url', 'url'), ('severity', 'severity'), ('description', 'description'), ('mitigation', 'mitigation'), ('impact', 'impact'), ('steps_to_reproduce', 'steps_to_reproduce'), ('severity_justification', 'severity_justification'), ('references', 'references'), ('test', 'test'), ('is_template', 'is_template'), ('active', 'active'), ('verified', 'verified'), ('false_p', 'false_p'), ('duplicate', 'duplicate'), ('duplicate_finding', 'duplicate_finding'), ('out_of_scope', 'out_of_scope'), ('under_review', 'under_review'), ('review_requested_by', 'review_requested_by'), ('under_defect_review', 'under_defect_review'), ('defect_review_requested_by', 'defect_review_requested_by'), ('is_Mitigated', 'is_Mitigated'), ('thread_id', 'thread_id'), ('mitigated', 'mitigated'), ('mitigated_by', 'mitigated_by'), ('reporter', 'reporter'), ('numerical_severity', 'numerical_severity'), ('last_reviewed', 'last_reviewed'), ('last_reviewed_by', 'last_reviewed_by'), ('line_number', 'line_number'), ('sourcefilepath', 'sourcefilepath'), ('sourcefile', 'sourcefile'), ('param', 'param'), ('payload', 'payload'), ('hash_code', 'hash_code'), ('line', 'line'), ('file_path', 'file_path'), ('component_name', 'component_name'), ('component_version', 'component_version'), ('static_finding', 'static_finding'), ('dynamic_finding', 'dynamic_finding'), ('created', 'created'), ('scanner_confidence', 'scanner_confidence'), ('sonarqube_issue', 'sonarqube_issue'), ('unique_id_from_tool', 'unique_id_from_tool'), ('sast_source_object', 'sast_source_object'), ('sast_sink_object', 'sast_sink_object'), ('sast_source_line', 'sast_source_line'), ('sast_source_file_path', 'sast_source_file_path'), ('nb_occurences', 'nb_occurences')], max_length=200),
        ),
        migrations.RunPython(show_info),

    ]