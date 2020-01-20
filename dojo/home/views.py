# #  dojo home pages
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

logger = logging.getLogger(__name__)


def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return HttpResponseRedirect(reverse('dashboard'))
    return HttpResponseRedirect(reverse('product'))


@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    if request.user.is_superuser:
        engagement_count = Engagement.objects.filter(active=True).count()
        finding_count = Finding.objects.filter(verified=True,
                                               mitigated=None,
                                               duplicate=False,
                                               date__range=[seven_days_ago,
                                                            now]).count()
        mitigated_count = Finding.objects.filter(mitigated__range=[seven_days_ago,
                                                                   now]).count()

        accepted_count = len([finding for ra in Risk_Acceptance.objects.filter(
            reporter=request.user, created__range=[seven_days_ago, now]) for finding in ra.accepted_findings.all()])

        # forever counts
        findings = Finding.objects.filter(verified=True, duplicate=False)
    else:
        engagement_count = Engagement.objects.filter(lead=request.user,
                                                     active=True).count()
        finding_count = Finding.objects.filter(reporter=request.user,
                                               verified=True,
                                               duplicate=False,
                                               mitigated=None,
                                               date__range=[seven_days_ago,
                                                            now]).count()
        mitigated_count = Finding.objects.filter(mitigated_by=request.user,
                                                 mitigated__range=[seven_days_ago,
                                                                   now]).count()

        accepted_count = len([finding for ra in Risk_Acceptance.objects.filter(
            reporter=request.user, created__range=[seven_days_ago, now]) for finding in ra.accepted_findings.all()])

        # forever counts
        findings = Finding.objects.filter(reporter=request.user,
                                          verified=True, duplicate=False)

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

# valentijn: bymonth: [{'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2020-01'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-12'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-11'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-10'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-09'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-08'}, {'a': 0, 'd': 0, 'b': 0, 'e': 0, 'c': 0, 'y': '2019-07'}]
# valentijn2: punchard: [[0, 0, 0.0], [0, 1, 0.14560705143488703], [0, 2, 0.10295973345818704], [0, 3, 0.1879778950992281], [0, 4, 0.16279363250585785], [0, 5, 0.0], [0, 6, 0.0], [1, 0, 0.0], [1, 1, 0.08406627034183971], [1, 2, 0.0], [1, 3, 0.2788162762484645], [1, 4, 0.08406627034183971], [1, 5, 0.24867138120497237], [1, 6, 0.0], [2, 0, 0.07280352571744352], [2, 1, 0.05944382982777641], [2, 2, 0.23403059206266477], [2, 3, 0.19715287964047098], [2, 4, 0.41183893383274817], [2, 5, 0.18321818849022486], [2, 6, 0.15727359070153984], [3, 0, 0.11888765965555281], [3, 1, 0.042033135170919854], [3, 2, 0.4009705539799782], [3, 3, 0.15727359070153984], [3, 4, 0.05944382982777641], [3, 5, 0.042033135170919854], [3, 6, 0.0], [4, 0, 0.0], [4, 1, 0.042033135170919854], [4, 2, 0.47740464424457557], [4, 3, 0.05944382982777641], [4, 4, 0.23777531931110563], [4, 5, 0.5448116995677184], [4, 6, 0.13292044433783765], [5, 0, 0.09398894754961405], [5, 1, 0.21432777645400353], [5, 2, 0.05944382982777641], [5, 3, 0.10295973345818704], [5, 4, 0.1783314894833292], [5, 5, 0.14560705143488703], [5, 6, 0.18321818849022486], [6, 0, 0.0], [6, 1, 0.05944382982777641], [6, 2, 0.13292044433783765], [6, 3, 0.12609940551275958], [6, 4, 0.15727359070153984], [6, 5, 0.13940813812423225], [6, 6, 0.11888765965555281], [7, 0, 0.0], [7, 1, 0.0], [7, 2, 0.08406627034183971], [7, 3, 0.11120922248661635], [7, 4, 0.19262002361705083], [7, 5, 0.526673674119564], [7, 6, 0.042033135170919854], [8, 0, 0.0], [8, 1, 0.05944382982777641], [8, 2, 0.23777531931110563], [8, 3, 0.7280352571744351], [8, 4, 0.3566629789666584], [8, 5, 0.1733070560855672], [8, 6, 0.11120922248661635], [9, 0, 0.0], [9, 1, 0.0], [9, 2, 0.12609940551275958], [9, 3, 0.08406627034183971], [9, 4, 0.11888765965555281], [9, 5, 0.08406627034183971], [9, 6, 0.05944382982777641], [10, 0, 0.09398894754961405], [10, 1, 0.19262002361705083], [10, 2, 0.08406627034183971], [10, 3, 0.5300176675500491], [10, 4, 0.11120922248661635], [10, 5, 0.16813254068367942], [10, 6, 0.19715287964047098], [11, 0, 0.13292044433783765], [11, 1, 0.201583834676362], [11, 2, 0.4203313517091985], [11, 3, 0.48292395643950015], [11, 4, 0.3782982165382787], [11, 5, 0.16813254068367942], [11, 6, 0.1879778950992281], [12, 0, 0.09398894754961405], [12, 1, 0.0], [12, 2, 0.18321818849022486], [12, 3, 0.7908487188540386], [12, 4, 0.12609940551275958], [12, 5, 0.15727359070153984], [12, 6, 0.12609940551275958], [13, 0, 0.0], [13, 1, 0.0], [13, 2, 0.08406627034183971], [13, 3, 0.19715287964047098], [13, 4, 0.6191867457790178], [13, 5, 0.20591946691637408], [13, 6, 0.0], [14, 0, 0.0], [14, 1, 1.0], [14, 2, 0.0], [14, 3, 0.0], [14, 4, 0.09398894754961405], [14, 5, 0.13292044433783765], [14, 6, 0.10295973345818704], [15, 0, 0.0], [15, 1, 0.05944382982777641], [15, 2, 0.0], [15, 3, 0.21016567585459925], [15, 4, 0.1783314894833292], [15, 5, 0.10295973345818704], [15, 6, 0.042033135170919854], [16, 0, 0.0], [16, 1, 0.15155262412726034], [16, 2, 0.3201148203898338], [16, 3, 0.2556775796486315], [16, 4, 0.5670579955507383], [16, 5, 0.07280352571744352], [16, 6, 0.0], [17, 0, 0.0], [17, 1, 0.201583834676362], [17, 2, 0.11888765965555281], [17, 3, 0.28196684264884214], [17, 4, 0.24146197821975007], [17, 5, 0.2224184449732327], [17, 6, 0.0], [18, 0, 0.0], [18, 1, 0.0], [18, 2, 0.0], [18, 3, 0.10295973345818704], [18, 4, 0.2224184449732327], [18, 5, 0.05944382982777641], [18, 6, 0.11888765965555281], [19, 0, 0.0], [19, 1, 0.0], [19, 2, 0.11888765965555281], [19, 3, 0.13292044433783765], [19, 4, 0.0], [19, 5, 0.08406627034183971], [19, 6, 0.0], [20, 0, 0.08406627034183971], [20, 1, 0.0], [20, 2, 0.10295973345818704], [20, 3, 0.7170315722605068], [20, 4, 0.1879778950992281], [20, 5, 0.2302249629577657], [20, 6, 0.042033135170919854], [21, 0, 0.0], [21, 1, 0.16813254068367942], [21, 2, 0.042033135170919854], [21, 3, 0.22635536025596517], [21, 4, 0.042033135170919854], [21, 5, 0.0], [21, 6, 0.0], [22, 0, 0.0], [22, 1, 0.0], [22, 2, 0.0], [22, 3, 0.0], [22, 4, 0.07280352571744352], [22, 5, 0.11120922248661635], [22, 6, 0.0], [23, 0, 0.0], [23, 1, 0.0], [23, 2, 0.0], [23, 3, 0.0], [23, 4, 0.0], [23, 5, 0.042033135170919854], [23, 6, 0.0], [24, 0, 0.0], [24, 1, 0.5639336852976843], [24, 2, 0.11888765965555281], [24, 3, 0.13940813812423225], [24, 4, 0.0], [24, 5, 0.49377753535064867], [24, 6, 0.12609940551275958], [25, 0, 0.30017662645039134], [25, 1, 0.16813254068367942], [25, 2, 0.13940813812423225], [25, 3, 0.08406627034183971], [25, 4, 0.16813254068367942], [25, 5, 0.0], [25, 6, 0.042033135170919854]]
# valentijn2: ticks: [[0, "<span class='small'>07/22<br/>2019</span>"], [1, "<span class='small'>07/29<br/>2019</span>"], [2, "<span class='small'>08/05<br/>2019</span>"], [3, "<span class='small'>08/12<br/>2019</span>"], [4, "<span class='small'>08/19<br/>2019</span>"], [5, "<span class='small'>08/26<br/>2019</span>"], [6, "<span class='small'>09/02<br/>2019</span>"], [7, "<span class='small'>09/09<br/>2019</span>"], [8, "<span class='small'>09/16<br/>2019</span>"], [9, "<span class='small'>09/23<br/>2019</span>"], [10, "<span class='small'>09/30<br/>2019</span>"], [11, "<span class='small'>10/07<br/>2019</span>"], [12, "<span class='small'>10/14<br/>2019</span>"], [13, "<span class='small'>10/21<br/>2019</span>"], [14, "<span class='small'>10/28<br/>2019</span>"], [15, "<span class='small'>11/04<br/>2019</span>"], [16, "<span class='small'>11/11<br/>2019</span>"], [17, "<span class='small'>11/18<br/>2019</span>"], [18, "<span class='small'>11/25<br/>2019</span>"], [19, "<span class='small'>12/02<br/>2019</span>"], [20, "<span class='small'>12/09<br/>2019</span>"], [21, "<span class='small'>12/16<br/>2019</span>"], [22, "<span class='small'>12/23<br/>2019</span>"], [23, "<span class='small'>12/30<br/>2019</span>"], [24, "<span class='small'>01/06<br/>2020</span>"], [25, "<span class='small'>01/13<br/>2020</span>"]]
# valentijn2: highest_count: 566

    # order_by is needed due to ordering being present in Meta of Findin
    severities_by_month=findings.filter(created__gte=timezone.now()+relativedelta(months=-6)) \
                                .values('created__year', 'created__month', 'severity').annotate(count=Count('severity')).order_by()

#    print(severities_by_month)

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
                sourcedata['a'] = ms['count']
            elif ms['severity'] == 'High':
                sourcedata['b'] = ms['count']
            elif ms['severity'] == 'Medium':
                sourcedata['c'] = ms['count']
            elif ms['severity'] == 'Low':
                sourcedata['d'] = ms['count']
            elif ms['severity'] == 'Info':
                sourcedata['e'] = ms['count']

#    print(results)

    by_month = [ v for k, v in sorted(results.items()) ]

    print(by_month)


    start_date = now - timedelta(days=180)

    r = relativedelta(now, start_date)
    weeks_between = int(ceil((((r.years * 12) + r.months) * 4.33) + (r.days / 7)))
    if weeks_between <= 0:
        weeks_between += 2

    unassigned_surveys = Answered_Survey.objects.all().filter(
        assignee_id__isnull=True, completed__gt=0)

    punchcard, ticks, highest_count = get_punchcard_data(findings, weeks_between, start_date)

    logger.error("valentijn2: punchard: %s", punchcard)
    logger.error("valentijn2: ticks: %s", ticks)
    logger.error("valentijn2: highest_count: %s", highest_count)
    
    add_breadcrumb(request=request, clear=True)
    return render(request,
                  'dojo/dashboard.html',
                  {'engagement_count': engagement_count,
                   'finding_count': finding_count,
                   'mitigated_count': mitigated_count,
                   'accepted_count': accepted_count,
                   'critical': sev_counts_all['Critical'],
                   'high': sev_counts_all['High'],
                   'medium': sev_counts_all['Medium'],
                   'low': sev_counts_all['Low'],
                   'info': sev_counts_all['Info'],
                   'by_month': by_month,
                   'punchcard': punchcard,
                   'ticks': ticks,
                   'surveys': unassigned_surveys,
                   'highest_count': highest_count})
