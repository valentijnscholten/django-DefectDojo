from dojo.models import Product, Engagement, Test, Finding, \
    JIRA_Issue, Tool_Product_Settings, Tool_Configuration, Tool_Type, \
    User, ScanSettings, Scan, Stub_Finding, Endpoint, JIRA_PKey, JIRA_Conf, \
    Finding_Template, Note_Type

from dojo.api_v2.views import EndPointViewSet, EngagementViewSet, \
    FindingTemplatesViewSet, FindingViewSet, JiraConfigurationsViewSet, \
    JiraIssuesViewSet, JiraViewSet, ProductViewSet, ScanSettingsViewSet, \
    ScansViewSet, StubFindingsViewSet, TestsViewSet, \
    ToolConfigurationsViewSet, ToolProductSettingsViewSet, ToolTypesViewSet, \
    UsersViewSet, ImportScanView, NoteTypeViewSet

from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
import json
from defusedxml import ElementTree
import logging


logger = logging.getLogger(__name__)

class DedupeTest(APITestCase):
    fixtures = ['dojo_testdata.json']

    def __init__(self, *args, **kwargs):
        # TODO remove __init__ if it does nothing...
        APITestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        testuser = User.objects.get(username='admin')
        token = Token.objects.get(user=testuser)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        # self.url = reverse(self.viewname + '-list')

        self.scans_path = 'dojo/unittests/scans/zap/'
        self.zap_sample1_filename = self.scans_path + 'zap_sample.xml'
        self.zap_sample2_filename = self.scans_path + 'zap_sample_updated.xml'
        self.zap_sample1_xml = ElementTree.parse(open(self.zap_sample1_filename))
        self.zap_sample2_xml = ElementTree.parse(open(self.zap_sample2_filename))

    def import_scan(self, payload):
        response = self.client.post(reverse('importscan-list'), payload)
        self.assertEqual(201, response.status_code)
        return json.loads(response.content)

    def reimport_scan(self, payload):
        response = self.client.post(reverse('reimportscan-list'), payload)
        self.assertEqual(201, response.status_code)
        return json.loads(response.content)

    def get_test(self, test_id):
        response = self.client.get(reverse('test-list') + '%s/' % test_id, format='json')
        self.assertEqual(200, response.status_code)
        # print('test.content: ', response.content)
        return json.loads(response.content)

    def get_test_findings(self, test_id, active=None):
        payload = {'test': test_id}
        if active is not None:
            payload['active'] = active

        response = self.client.get(reverse('finding-list'), payload, format='json')
        self.assertEqual(200, response.status_code)
        # print('findings.content: ', response.content)
        return json.loads(response.content)

    def log_finding_summary(self, findings_content_json):
        for finding in findings_content_json['results']:
            logger.debug(str(finding['id']) + ':' + str(finding['active']))

    def import_scan1(self):
        logger.debug('importing original zap xml report')
        import1 = self.import_scan(
            {
                "scan_date": '2020-06-04',  # use today?
                "minimum_severity": 'Low',  # test threshold?
                "active": True,
                "verified": True,
                "scan_type": 'ZAP Scan',
                "file": open(self.zap_sample1_filename),
                "engagement": 1,
                "version": "1.0.1",
            })

        test1_id = import1['test']
        test1 = self.get_test(test1_id)
        findings1 = self.get_test_findings(test1_id)

        self.log_finding_summary(findings1)

        # imported count must match count in xml report
        self.assertEqual(findings1['count'], len(self.zap_sample1_xml.findall('site/alerts/alertitem')))
        return test1_id

    def reimport_scan1(self, test_id):
        logger.debug('reimporting exact same original zap xml report again')
        test1_finding_count = Test.objects.get(id=test_id).finding_set.count()

        # reimport exact same report
        reimport1 = self.reimport_scan(
            {
                "test": test_id,
                "scan_date": '2020-06-04',  # use today?
                "minimum_severity": 'Low',  # test threshold?
                "active": True,
                "verified": True,
                "scan_type": 'ZAP Scan',
                "file": open(self.zap_sample1_filename),
                "engagement": 1,
                "version": "1.0.1",
                "close_old_findings": False,                
            })

        test1_id = reimport1['test']
        self.assertEqual(test1_id, test_id)

        test1 = self.get_test(test1_id)
        findings1 = self.get_test_findings(test1_id)

        self.log_finding_summary(findings1)

        # reimported count must match count in xml report
        self.assertEqual(findings1['count'], len(self.zap_sample1_xml.findall('site/alerts/alertitem')))
        # finding count in db must match count in db before reimport
        self.assertEqual(test1_finding_count, Test.objects.get(id=test_id).finding_set.count())

        test1 = self.get_test(test_id)
        findings1 = self.get_test_findings(test1_id)

        # print(test1)

        # double check finding count
        self.assertEqual(findings1['count'], len(self.zap_sample1_xml.findall('site/alerts/alertitem')))

        # TODO check dates updated?

    def reimport_scan2(self, test_id):
        logger.debug('reimporting updated zap xml report, close_old_findings=False')

        # reimport updated report
        reimport2 = self.reimport_scan(
            {
                "test": test_id,
                "scan_date": '2020-06-04',  # use today?
                "minimum_severity": 'Low',  # test threshold?
                "active": True,
                "verified": True,
                "scan_type": 'ZAP Scan',
                "file": open(self.zap_sample2_filename),
                "engagement": 1,
                "version": "1.0.1",
                "close_old_findings": False,
            })

        test2_id = reimport2['test']
        self.assertEqual(test2_id, test_id)

        test2 = self.get_test(test2_id)
        findings2 = self.get_test_findings(test2_id, active=True)

        self.log_finding_summary(findings2)
        self.assertEqual(findings2['count'], len(self.zap_sample2_xml.findall('site/alerts/alertitem')))

    def test_import_reimport_reimport(self):
        # import initial zap file with 3 findings
        test_id = self.import_scan1()
        # reimport exact same zap file with 3 findings        
        self.reimport_scan1(test_id)
        # reimport updated zap file with 1 new finding and 1 finding removed
        self.reimport_scan2(test_id)

        # TODO add another reimport of the original to reopen mitigated finding?

        # Questions:
        # - What if on reimport the description in the report is different from initial import? Currently reimport does not overwrite it, also for dedupe.
        # - What if on reimport the severity in the report is different from initial import? Currently for ZAP and most scanners it is seen as a different issue, also for dedupe

