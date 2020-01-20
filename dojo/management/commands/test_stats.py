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


#[{'a': 0, 'd': 22, 'e': 0, 'b': 70, 'c': 40, 'y': '2019-7'}, {'a': 0, 'd': 22, 'e': 0, 'b': 70, 'c': 40, 'y': '2019-7'}, {'a': 0, 'd': 22, 'e': 0, 'b': 70, 'c': 40, 'y': '2019-7'}, {'a': 7, 'd': 19, 'e': 0, 'b': 199, 'c': 560, 'y': '2019-8'}, {'a': 7, 'd': 19, 'e': 0, 'b': 199, 'c': 560, 'y': '2019-8'}, {'a': 7, 'd': 19, 'e': 0, 'b': 199, 'c': 560, 'y': '2019-8'}, {'a': 7, 'd': 19, 'e': 0, 'b': 199, 'c': 560, 'y': '2019-8'}, {'a': 4, 'd': 26, 'e': 10, 'b': 186, 'c': 486, 'y': '2019-9'}, {'a': 4, 'd': 26, 'e': 10, 'b': 186, 'c': 486, 'y': '2019-9'}, {'a': 4, 'd': 26, 'e': 10, 'b': 186, 'c': 486, 'y': '2019-9'}, {'a': 4, 'd': 26, 'e': 10, 'b': 186, 'c': 486, 'y': '2019-9'}, {'a': 4, 'd': 26, 'e': 10, 'b': 186, 'c': 486, 'y': '2019-9'}, {'a': 0, 'd': 26, 'e': 505, 'b': 346, 'c': 423, 'y': '2019-10'}, {'a': 0, 'd': 26, 'e': 505, 'b': 346, 'c': 423, 'y': '2019-10'}, {'a': 0, 'd': 26, 'e': 505, 'b': 346, 'c': 423, 'y': '2019-10'}, {'a': 0, 'd': 26, 'e': 505, 'b': 346, 'c': 423, 'y': '2019-10'}, {'a': 1, 'd': 22, 'e': 667, 'b': 222, 'c': 186, 'y': '2019-11'}, {'a': 1, 'd': 22, 'e': 667, 'b': 222, 'c': 186, 'y': '2019-11'}, {'a': 1, 'd': 22, 'e': 667, 'b': 222, 'c': 186, 'y': '2019-11'}, {'a': 1, 'd': 22, 'e': 667, 'b': 222, 'c': 186, 'y': '2019-11'}, {'a': 1, 'd': 22, 'e': 667, 'b': 222, 'c': 186, 'y': '2019-11'}, {'a': 0, 'd': 26, 'e': 7, 'b': 148, 'c': 260, 'y': '2019-12'}, {'a': 0, 'd': 26, 'e': 7, 'b': 148, 'c': 260, 'y': '2019-12'}, {'a': 0, 'd': 26, 'e': 7, 'b': 148, 'c': 260, 'y': '2019-12'}, {'a': 0, 'd': 26, 'e': 7, 'b': 148, 'c': 260, 'y': '2019-12'}, {'a': 4, 'd': 86, 'e': 82, 'b': 122, 'c': 152, 'y': '2020-1'}, {'a': 4, 'd': 86, 'e': 82, 'b': 122, 'c': 152, 'y': '2020-1'}, {'a': 4, 'd': 86, 'e': 82, 'b': 122, 'c': 152, 'y': '2020-1'}, {'a': 4, 'd': 86, 'e': 82, 'b': 122, 'c': 152, 'y': '2020-1'}, {'a': 4, 'd': 86, 'e': 82, 'b': 122, 'c': 152, 'y': '2020-1'}]

#{'2019-8': {'a': 7, 'y': '2019-8', 'b': 199, 'd': 19, 'c': 560, 'e': 0}, '2019-10': {'a': 0, 'y': '2019-10', 'b': 346, 'd': 26, 'c': 423, 'e': 505}, '2019-7': {'a': 0, 'y': '2019-7', 'b': 70, 'd': 22, 'c': 40, 'e': 0}, '2019-12': {'a': 0, 'y': '2019-12', 'b': 148, 'd': 26, 'c': 260, 'e': 7}, '2019-9': {'a': 4, 'y': '2019-9', 'b': 186, 'd': 26, 'c': 486, 'e': 10}, '2019-11': {'a': 1, 'y': '2019-11', 'b': 222, 'd': 22, 'c': 186, 'e': 667}, '2020-1': {'a': 4, 'y': '2020-1', 'b': 122, 'd': 86, 'c': 152, 'e': 82}}

#[{'a': 7, 'y': '2019-8', 'b': 199, 'd': 19, 'c': 560, 'e': 0}, {'a': 0, 'y': '2019-10', 'b': 346, 'd': 26, 'c': 423, 'e': 505}, {'a': 0, 'y': '2019-7', 'b': 70, 'd': 22, 'c': 40, 'e': 0}, {'a': 0, 'y': '2019-12', 'b': 148, 'd': 26, 'c': 260, 'e': 7}, {'a': 4, 'y': '2019-9', 'b': 186, 'd': 26, 'c': 486, 'e': 10}, {'a': 1, 'y': '2019-11', 'b': 222, 'd': 22, 'c': 186, 'e': 667}, {'a': 4, 'y': '2020-1', 'b': 122, 'd': 86, 'c': 152, 'e': 82}]



        by_month = list()

        # order_by is needed due to ordering being present in Meta of Findin
        severities_by_month=findings.filter(created__gte=timezone.now()+relativedelta(months=-6)) \
                                    .values('created__year', 'created__month', 'severity').annotate(count=Count('severity')).order_by()
                                    # .annotate(year=created__year')).annotate(month=ExtractMonth('created')) 
        print(severities_by_month)

        results = {}
        for ms in severities_by_month:
                year = str(ms['created__year'])
                month = str(ms['created__month'],2).zfill(2)
                key = year +'-' + month

                if key not in results:
                    sourcedata = {'y': key, 'a': 0, 'b': 0,
                            'c': 0, 'd': 0, 'e': 0}
                    results[key] = sourcedata

                month_stats = results[key]

                if ms['severity'] == 'Critical':
                    sourcedata['a'] = ms['count']
                elif ms['severity'] == 'High':
                    sourcedata['b'] = ms['count']
                elif ms['severity'] == 'Medium':
                    sourcedata['c'] = ms['count']
                elif ms['severity'] == 'Low':
                    sourcedata['d'] = ms['count']
                elif ms['severity'] == 'Info':
                    sourcedata['e'] = ms['count']

        print(results)
 
        by_month = [ v for k, v in sorted(results.items()) ]

        print(by_month)

