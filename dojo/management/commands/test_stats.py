from django.core.management.base import BaseCommand
from pytz import timezone

from dojo.models import Finding
import logging
from calendar import monthrange
from datetime import datetime, timedelta
from math import ceil

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from dojo.models import Finding, Engagement, Risk_Acceptance
from django.db.models import Count
from dojo.utils import add_breadcrumb, get_punchcard_data

from defectDojo_engagement_survey.models import Answered_Survey
from dateutil.relativedelta import relativedelta


locale = timezone(get_system_setting('time_zone'))

"""
Author: Aaron Weaver
This script will update the hashcode and dedupe findings in DefectDojo:
"""


class Command(BaseCommand):

    def handle(self, *args, **options):

    findings = Finding.objects.filter(verified=True, duplicate=False)

    # order_by is needed due to ordering being present in Meta of Finding
    severities_all = findings.values('severity').annotate(count=Count('severity')).order_by()

    # make sure all keys are present
    sev_counts_all = {'Critical': 0,
                'High': 0,
                'Medium': 0,
                'Low': 0,
                'Info': 0}

    for s in severities_all:
        logger.error(s)
        sev_counts_all[s['severity']] = s['count']

    print(severities_all)
