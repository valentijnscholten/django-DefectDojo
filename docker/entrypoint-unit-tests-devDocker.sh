#!/bin/sh
# Run available unittests with a simple setup
umask 0002
# Run available unittests with a setup for local dev:
# - Make migrations and apply any needed changes
# - Leave container up after running tests to allow debugging, rerunning tests, etc.
set -x
set -e
set -v

cd /app
# Unset the database URL so that we can force the DD_TEST_DATABASE_NAME (see django "DATABASES" configuration in settings.dist.py)
# unset DD_DATABASE_URL

# python3 manage.py makemigrations dojo
# python3 manage.py migrate

# python3 manage.py test dojo.unittests --keepdb -v 3
# python3 manage.py test dojo.unittests.test_deduplication_logic --keepdb -v 3 --parallel 1
python3 manage.py test dojo.unittests.test_import_reimport.DedupeTest --keepdb -v 3 --parallel 1
# python3 manage.py test dojo.unittests.test_import_reimport.DedupeTest.test_import_0_reimport_1_active_verified_reimport_0_active_verified --keepdb -v 3 --parallel 1
# python3 manage.py test dojo.unittests.test_import_reimport.DedupeTest.test_import_0_reimport_3_active_verified --keepdb -v 3 --parallel 1

# echo "End of tests. Leaving the container up"
# tail -f /dev/null
