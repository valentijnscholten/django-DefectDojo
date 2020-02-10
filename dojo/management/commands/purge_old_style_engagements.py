from django.core.management.base import BaseCommand
from pytz import timezone

from dojo.models import Product
from dojo.utils import get_system_setting
import logging
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.contrib.admin.utils import NestedObjects
from django.db import DEFAULT_DB_ALIAS

locale = timezone(get_system_setting('time_zone'))

logger = logging.getLogger(__name__)
deduplicationLogger = logging.getLogger("dojo.specific-loggers.deduplication")

"""
Author: Valentijn Scholten
This script will remove tests (scans) without findings. Tests younger than 2 weeks will not be removed.
"""

class Command(BaseCommand):
    help = 'This script will remove engs old style when new style engs are presen.'

    def handle(self, *args, **options):

        logger.info("######## Removing engs old style ########")
        prods = Product.objects.include(name__icontains='ingenico').include(name__icontains='qander').prefetch('engagement_set')

        count = 0
        for prod in prods:
            print(prod.id, prod.name)
            for eng in prod.engagement_set:
                print(eng.id, eng.name, eng.product)
                WIPPER DE WIP DEZE FILE
                
                logger.debug('removing eng %s:%s:%s.', eng.id, eng.name, eng.product)
                # test.delete()
                count += 1

        logger.info("######## Done Removing %i engs old style ########", count)
