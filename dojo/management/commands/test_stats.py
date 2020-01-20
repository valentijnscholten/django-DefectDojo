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

#valentijn: bymonth: [{'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2020-01'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-12'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-11'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-10'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-09'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-08'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-07'}]

#<QuerySet [{'count': 22, 'created__year': 2019, 'severity': 'Low', 'created__month': 7}, {'count': 70, 'created__year': 2019, 'severity': 'High', 'created__month': 7}, {'count': 40, 'created__year': 2019, 'severity': 'Medium', 'created__month': 7}, {'count': 560, 'created__year': 2019, 'severity': 'Medium', 'created__month': 8}, {'count': 199, 'created__year': 2019, 'severity': 'High', 'created__month': 8}, {'count': 19, 'created__year': 2019, 'severity': 'Low', 'created__month': 8}, {'count': 7, 'created__year': 2019, 'severity': 'Critical', 'created__month': 8}, {'count': 186, 'created__year': 2019, 'severity': 'High', 'created__month': 9}, {'count': 26, 'created__year': 2019, 'severity': 'Low', 'created__month': 9}, {'count': 4, 'created__year': 2019, 'severity': 'Critical', 'created__month': 9}, {'count': 486, 'created__year': 2019, 'severity': 'Medium', 'created__month': 9}, {'count': 10, 'created__year': 2019, 'severity': 'Info', 'created__month': 9}, {'count': 346, 'created__year': 2019, 'severity': 'High', 'created__month': 10}, {'count': 26, 'created__year': 2019, 'severity': 'Low', 'created__month': 10}, {'count': 423, 'created__year': 2019, 'severity': 'Medium', 'created__month': 10}, {'count': 505, 'created__year': 2019, 'severity': 'Info', 'created__month': 10}, {'count': 667, 'created__year': 2019, 'severity': 'Info', 'created__month': 11}, {'count': 222, 'created__year': 2019, 'severity': 'High', 'created__month': 11}, {'count': 186, 'created__year': 2019, 'severity': 'Medium', 'created__month': 11}, {'count': 22, 'created__year': 2019, 'severity': 'Low', 'created__month': 11}, '...(remaining elements truncated)...']>




        by_month = list()

        # order_by is needed due to ordering being present in Meta of Findin
        severities_by_month=findings.filter(created__gte=timezone.now()+relativedelta(months=-6)) \
                                    .values('created__year', 'created__month', 'severity').annotate(count=Count('severity')).order_by()
                                    # .annotate(year=created__year')).annotate(month=ExtractMonth('created')) 
        print(severities_by_month)

        results = {}
        for ms in severities_by_month:
                key = str(ms['created__year'])+'-'+str(ms['created__month'])

                if key not in results:
                    sourcedata = {'y': str(ms['created__year'])+'-'+str(ms['created__month']), 'a': 0, 'b': 0,
                            'c': 0, 'd': 0, 'e': 0}
                    result[key] = sourcedata

                month_stats = results[key]

                if ms.severity == 'Critical':
                    sourcedata['a'] = ms['count']
                elif ms.severity == 'High':
                    sourcedata['b'] = ms['count']
                elif ms.severity == 'Medium':
                    sourcedata['c'] = ms['count']
                elif ms.severity == 'Low':
                    sourcedata['d'] = ms['count']
                elif ms.severity == 'Info':
                    sourcedata['e'] = ms['count']

                by_month.append(month_stats)

        print(by_month)
