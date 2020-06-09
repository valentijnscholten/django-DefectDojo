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

        logger.debug('getting findings for test: %s', payload)

        response = self.client.get(reverse('finding-list'), payload, format='json')
        self.assertEqual(200, response.status_code)
        # print('findings.content: ', response.content)
        return json.loads(response.content)

    def log_finding_summary(self, findings_content_json):
        # print('summary')
        # print(findings_content_json)
        # print(findings_content_json['count'])

        if not findings_content_json or findings_content_json['count'] == 0:
            logger.debug('no findings')

        for finding in findings_content_json['results']:
            logger.debug(str(finding['id']) + ': active: ' + str(finding['active']) + ': verified: ' + str(finding['verified']) + ': is_Mitigated: ' + str(finding['is_Mitigated']))
    
    def assert_finding_count(self, count, findings_content_json):
        self.assertEqual(findings_content_json['count'], count)

    # import zap scan, testing:
    # - import
    # - severity threshold
    # - active/verifed = True
    def import_zap_scan_original(self):
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


    # reimport zap scan, testing:
    # - reimport, findings stay the same, stay active
    # - severity threshold
    # - active = True
    # - verified = False (doesn't affect existing findings currently)
    def reimport_zap_scan_original(self, test_id):
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

        # Todo check reopened finding?!

    def reimport_zap_scan_updated(self, test_id):
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
        self.assert_finding_count(self.zap_sample1_count_above_threshold, findings)

    # reimport original zap scan, after the updated scan has closed 1 finding
    # - reimport, reactivating 1 finding (and mitigating another)
    # - severity threshold
    # - active = True
    # - verified = False (doesn't affect existing findings currently)
    def reimport_zap_scan_original_after_updated_after_original(self, test_id):
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
        self.assert_finding_count(4, findings)  # there are 4 unique findings, 2 are shared between the 2 reports, 1 is informational so below threshold

        # reimported count must match count in xml report
        # we set verified=False in this reimport, but currently DD does not update this flag, so it's still True from previous import
        findings = self.get_test_findings(test_id, verified=True)
        # print('logging summary1')
        self.log_finding_summary(findings)
        # print('asserting1')
        self.assert_finding_count(self.zap_sample1_count_above_threshold, findings)

        # 1 finding still remains from the original import as not verified, because the verified flag is not updated by DD when reactivating a finding.
        findings = self.get_test_findings(test_id, verified=False)
        # print('logging summary2')
        self.log_finding_summary(findings)
        # print('asserting2')
        self.assert_finding_count(1, findings)

    # test what happens if we import the same report, but with changed severities.
    # currently defect dojo sees them as different (new) findings.
    # the reimport process does not use the hash code based deduplication (yet)
    # this probably something that should change, but at least we have now captured current behaviour in a test
    def reimport_zap_scan_updated_severity(self, test_id):
        logger.debug('reimporting original zap xml report, but with changed severities')

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
        self.assert_finding_count(2 * self.zap_sample1_count_above_threshold, findings)

    def test_import(self):
        test_id = self.import_zap_scan_original()

    def test_import_reimport_same(self):
        test_id = self.import_zap_scan_original()
        self.reimport_zap_scan_original(test_id)

    def test_import_reimport_different(self):
        test_id = self.import_zap_scan_original()
        self.reimport_zap_scan_updated(test_id)

    def test_import_reimport_different_multiple(self):
        test_id = self.import_zap_scan_original()
        self.reimport_zap_scan_updated(test_id)
        self.reimport_zap_scan_original_after_updated_after_original(test_id)

    def test_import_reimport_different_severity(self):
        test_id = self.import_zap_scan_original()
        self.reimport_zap_scan_updated(test_id)

        # Observations:
        # - When reopening a mititgated finding, almost no fields are updated such as title, description, severity, impact, references, ....
        # - Basically fields (and req/resp) are only store on the initial import, reimporting only changes the active/mitigated/verified flags + some dates + notes


# req / resp?
# notes
# endpoints