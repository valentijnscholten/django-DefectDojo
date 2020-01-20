from django.core.management.base import BaseCommand
from pytz import timezone

from dojo.models import Finding
from django.db.models.functions import ExtractMonth, ExtractYear
import logging
from calendar import monthrange
from datetime import date, datetime, timedelta
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
from dojo.utils import get_system_setting
from django.utils.timezone import localdate

"""
Author: Aaron Weaver
This script will update the hashcode and dedupe findings in DefectDojo:
"""


class Command(BaseCommand):

    def handle(self, *args, **options):

        # locale = timezone(get_system_setting('time_zone'))

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
            sev_counts_all[s['severity']] = s['count']

        print(severities_all)

# valentijn: bymonth: [{'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2020-01'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-12'}, {$
# valentijn2: punchard: [[0, 0, 0.0], [0, 1, 0.14560705143488703], [0, 2, 0.10295973345818704], [0, 3, 0.1879778950992281], [0, 4, 0.1627936$
# valentijn2: ticks: [[0, "<span class='small'>07/22<br/>2019</span>"], [1, "<span class='small'>07/29<br/>2019</span>"], [2, "<span class='$
# valentijn2: highest_count: 566

        by_month = list()

        # order_by is needed due to ordering being present in Meta of Findin
        severities_by_month=findings.filter(created__gte=timezone.make_aware(localdate()+relativedelta(months=-6))) \
                                    .annotate(year=ExtractYear('created')).annotate(month=ExtractMonth('created')) \
                                    .values('year', 'month', 'severity').annotate(count=Count('severity')).order_by()

        print(severities_by_month)

