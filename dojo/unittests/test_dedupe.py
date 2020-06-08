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
        self.zap_sample1_count_above_threshold = 3
        self.zap_sample2_count_above_threshold = 3

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

    def get_test_findings(self, test_id, active=None, verified=None):
        payload = {'test': test_id}
        if active is not None:
            payload['active'] = active
        if verified is not None:
            payload['verified'] = verified

        logger.debug(payload)

        response = self.client.get(reverse('finding-list'), payload, format='json')
        self.assertEqual(200, response.status_code)
        # print('findings.content: ', response.content)
        return json.loads(response.content)

    def log_finding_summary(self, findings_content_json):
        for finding in findings_content_json['results']:
            logger.debug(str(finding['id']) + ': active: ' + str(finding['active']) + ': verified: ' + str(finding['verified']) + ': is_Mitigated: ' + str(finding['is_Mitigated']))
    
    def assert_finding_count(self, count, findings_content_json):
        self.assertEqual(findings_content_json['count'], count)

    def import_scan1(self):
        logger.debug('importing original zap xml report')
        import1 = self.import_scan(
            {
                "scan_date": '2020-06-04',
                "minimum_severity": 'Low', # skip the 1 information finding
                "active": True,
                "verified": True,
                "scan_type": 'ZAP Scan',
                "file": open(self.zap_sample1_filename),
                "engagement": 1,
                "version": "1.0.1",
            })

        test_id = import1['test']
        findings = self.get_test_findings(test_id)
        self.log_finding_summary(findings)

        # imported count must match count in xml report
        self.assert_finding_count(self.zap_sample1_count_above_threshold, findings)
        return test_id

    def reimport_scan1(self, test_id):
        logger.debug('reimporting exact same original zap xml report again, verified=False')

        # reimport exact same report
        reimport1 = self.reimport_scan(
            {
                "test": test_id,
                "scan_date": '2020-06-04',
                "minimum_severity": 'Low',
                "active": True,
                "verified": False,
                "scan_type": 'ZAP Scan',
                "file": open(self.zap_sample1_filename),
                "engagement": 1,
                "version": "1.0.1",
            })

        test_id = reimport1['test']
        self.assertEqual(test_id, test_id)

        findings = self.get_test_findings(test_id)
        self.log_finding_summary(findings)

        # reimported count must match count in xml report
        # we set verified=False in this reimport, but currently DD does not update this flag, so it's still True from previous import
        findings = self.get_test_findings(test_id, verified=True)
        self.assert_finding_count(self.zap_sample1_count_above_threshold, findings)

        # inversely, we should see no findings with verified=False
        findings = self.get_test_findings(test_id, verified=False)
        self.assert_finding_count(0, findings)

    def reimport_scan2(self, test_id):
        logger.debug('reimporting updated zap xml report, 1 new finding and 1 no longer present, verified=True')

        # reimport updated report
        reimport1 = self.reimport_scan(
            {
                "test": test_id,
                "scan_date": '2020-06-04',
                "minimum_severity": 'Low',
                "active": True,
                "verified": True,
                "scan_type": 'ZAP Scan',
                "file": open(self.zap_sample2_filename),
                "engagement": 1,
                "version": "1.0.1",
            })

        test_id = reimport1['test']
        self.assertEqual(test_id, test_id)

        test = self.get_test(test_id)
        findings = self.get_test_findings(test_id)
        self.log_finding_summary(findings)

        # active findings must be equal to those in the report
        findings = self.get_test_findings(test_id, active=True, verified=True)
        self.assert_finding_count(self.zap_sample2_count_above_threshold, findings)

        # 1 finding must be mitigated as it is no longer in the updated xml report, verified still True
        findings = self.get_test_findings(test_id, active=False, verified=True)
        self.assert_finding_count(1, findings)

    def reimport_scan3(self, test_id):
        logger.debug('reimporting original zap xml report again to reopen 1 mitigated, and close 1 no longer in report, verified=True')

        # reimport exact same report
        reimport1 = self.reimport_scan(
            {
                "test": test_id,
                "scan_date": '2020-06-04',  # use today?
                "minimum_severity": 'Low',
                "active": True,
                "verified": True,
                "scan_type": 'ZAP Scan',
                "file": open(self.zap_sample1_filename),
                "engagement": 1,
                "version": "1.0.1",
            })

        test_id = reimport1['test']
        self.assertEqual(test_id, test_id)

        findings = self.get_test_findings(test_id)
        self.log_finding_summary(findings)
        # reimported count must match count in xml report
        findings = self.get_test_findings(test_id, active=True, verified=True)
        self.assert_finding_count(self.zap_sample1_count_above_threshold, findings)

        # 1 finding must be mitigated as it is not in the original xml report
        findings = self.get_test_findings(test_id, active=False, verified=True)
        self.assert_finding_count(1, findings)

        findings = self.get_test_findings(test_id, verified=False)
        self.assert_finding_count(0, findings)

    def test_import_reimport_reimport(self):
        # import initial zap file with 3 findings
        test_id = self.import_scan1()

        # reimport exact same zap file with 3 findings        
        self.reimport_scan1(test_id)

        # reimport updated zap file with 1 new finding and 1 finding removed
        self.reimport_scan2(test_id)

        # reimport original zap file again to reopen mitigated findings
        self.reimport_scan3(test_id)

        # Observations:
        # - When reopening a mititgated finding, almost no fields are updated such as title, description, severity, impact, references, ....
        # - Basically fields (and req/resp) are only store on the initial import, reimporting only changes the active/mitigated/verified flags + some dates + notes


# req / resp?
# notes