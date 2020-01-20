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
from dojo.utils import add_breadcrumb

from defectDojo_engagement_survey.models import Answered_Survey
from dateutil.relativedelta import relativedelta
from dojo.utils import get_system_setting
from django.utils.timezone import localdate
from math import pi, sqrt

"""
Author: Aaron Weaver
This script will update the hashcode and dedupe findings in DefectDojo:
"""


class Command(BaseCommand):

    def handle(self, *args, **options):

        now = timezone.now()
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

        #print(severities_all)

        by_month = list()

        # order_by is needed due to ordering being present in Meta of Findin
        severities_by_month=findings.filter(created__gte=now+relativedelta(months=-6)) \
                                    .values('created__year', 'created__month', 'severity').annotate(count=Count('severity')).order_by()
                                    # .annotate(year=created__year')).annotate(month=ExtractMonth('created')) 
        #print(severities_by_month)

        results = {}
        for ms in severities_by_month:
                year = str(ms['created__year'])
                month = str(ms['created__month']).zfill(2)
                key = year +'-' + month

                if key not in results:
                    sourcedata = {'y': key, 'a': 0, 'b': 0,
                            'c': 0, 'd': 0, 'e': 0}
                    results[key] = sourcedata

                month_stats = results[key]

                if ms['severity'] == 'Critical':
                    month_stats['a'] = ms['count']
                elif ms['severity'] == 'High':
                    month_stats['b'] = ms['count']
                elif ms['severity'] == 'Medium':
                    month_stats['c'] = ms['count']
                elif ms['severity'] == 'Low':
                    month_stats['d'] = ms['count']
                elif ms['severity'] == 'Info':
                    month_stats['e'] = ms['count']

        #print(results)
 
        by_month = [ v for k, v in sorted(results.items()) ]

#        print(by_month)



        start_date = now - timedelta(days=180)

        r = relativedelta(now, start_date)
        weeks_between = int(ceil((((r.years * 12) + r.months) * 4.33) + (r.days / 7)))
        if weeks_between <= 0:
            weeks_between += 2

        punchcard, ticks, highest_count = get_punchcard_data(findings, weeks_between, start_date)

        print(punchcard)
        print(ticks)
        print(highest_count)



def get_punchcard_data(findings, weeks_between, start_date):
    punchcard = list()
    ticks = list()
    highest_count = 0
    tick = 0
    week_count = 1

    # mon 0, tues 1, wed 2, thurs 3, fri 4, sat 5, sun 6
    # sat 0, sun 6, mon 5, tue 4, wed 3, thur 2, fri 1
    day_offset = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0, 6: 6}
    for x in range(-1, weeks_between):
        # week starts the monday before
        new_date = start_date + relativedelta(weeks=x, weekday=MO(1))
        end_date = new_date + relativedelta(weeks=1)
        append_tick = True
        days = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for finding in findings:
            try:
                if new_date < datetime.combine(finding.date, datetime.min.time(
                )).replace(tzinfo=timezone.get_current_timezone()) <= end_date:
                    # [0,0,(20*.02)]
                    # [week, day, weight]
                    days[day_offset[finding.date.weekday()]] += 1
                    if days[day_offset[finding.date.weekday()]] > highest_count:
                        highest_count = days[day_offset[
                            finding.date.weekday()]]
            except:
                if new_date < finding.date <= end_date:
                    # [0,0,(20*.02)]
                    # [week, day, weight]
                    days[day_offset[finding.date.weekday()]] += 1
                    if days[day_offset[finding.date.weekday()]] > highest_count:
                        highest_count = days[day_offset[
                            finding.date.weekday()]]
                pass

        if sum(days.values()) > 0:
            for day, count in list(days.items()):
                punchcard.append([tick, day, count])
                if append_tick:
                    ticks.append([
                        tick,
                        new_date.strftime(
                            "<span class='small'>%m/%d<br/>%Y</span>")
                    ])
                    append_tick = False
            tick += 1
        week_count += 1
    # adjust the size
    ratio = (sqrt(highest_count / pi))
    for punch in punchcard:
        punch[2] = (sqrt(punch[2] / pi)) / ratio

    return punchcard, ticks, highest_count