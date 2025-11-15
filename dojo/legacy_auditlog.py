"""
Legacy auditlog LogEntry model for backward compatibility.

This module contains a minimal copy of the django-auditlog LogEntry model
to maintain backward compatibility for displaying existing audit log entries
in the UI. New audit logging is handled by django-pghistory.

The model matches the django-auditlog LogEntry model structure exactly
to ensure it works with the existing auditlog_logentry database table.

Copied from django-auditlog version 3.2.1.
Source: https://github.com/jazzband/django-auditlog
"""
import logging

from django.db import connection, models
from django.db.models.query import QuerySet
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone as django_timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class LogEntryManager(models.Manager):

    """
    Custom manager that handles missing auditlog_logentry table gracefully.

    For fresh installations that never had django-auditlog, the table won't exist.
    This manager returns an empty queryset instead of raising an error.
    """

    _table_exists = None

    def table_exists(self):
        """Check if the auditlog_logentry table exists in the database."""
        if self._table_exists is None:
            try:
                with connection.cursor() as cursor:
                    table_name = self.model._meta.db_table
                    # Use Django's introspection API for portability
                    introspection = connection.introspection
                    table_names = introspection.table_names(cursor)
                    self._table_exists = table_name in table_names
            except (OperationalError, ProgrammingError) as e:
                logger.debug(f"Could not check if {self.model._meta.db_table} table exists: {e}")
                self._table_exists = False
        return self._table_exists

    def get_queryset(self):
        """Return an empty queryset if the table doesn't exist."""
        if not self.table_exists():
            # Return an empty queryset using the model's base queryset class
            # This avoids circular reference issues
            return QuerySet(self.model).none()
        return super().get_queryset()


class LogEntry(models.Model):

    """
    Represents an entry in the audit log. The content type is saved along with the textual and numeric
    (if available) primary key, as well as the textual representation of the object when it was saved.
    It holds the action performed and the fields that were changed in the transaction.

    This is a read-only model for displaying existing audit log entries.
    New audit logging is handled by django-pghistory.
    """

    class Action:

        """
        The actions that Auditlog distinguishes: creating, updating and deleting objects.

        The valid actions are CREATE, UPDATE, DELETE and ACCESS.
        """

        CREATE = 0
        UPDATE = 1
        DELETE = 2
        ACCESS = 3

        choices = (
            (CREATE, _("create")),
            (UPDATE, _("update")),
            (DELETE, _("delete")),
            (ACCESS, _("access")),
        )

    content_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("content type"),
    )
    object_pk = models.CharField(
        db_index=True, max_length=255, verbose_name=_("object pk"),
    )
    object_id = models.BigIntegerField(
        blank=True, db_index=True, null=True, verbose_name=_("object id"),
    )
    object_repr = models.TextField(verbose_name=_("object representation"))
    serialized_data = models.JSONField(null=True)
    action = models.PositiveSmallIntegerField(
        choices=Action.choices, verbose_name=_("action"), db_index=True,
    )
    changes_text = models.TextField(blank=True, verbose_name=_("change message"))
    changes = models.JSONField(null=True, verbose_name=_("change message"))
    actor = models.ForeignKey(
        to="dojo.Dojo_User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
        verbose_name=_("actor"),
    )
    cid = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_("Correlation ID"),
    )
    remote_addr = models.GenericIPAddressField(
        blank=True, null=True, verbose_name=_("remote address"),
    )
    remote_port = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=_("remote port"),
    )
    timestamp = models.DateTimeField(
        default=django_timezone.now,
        db_index=True,
        verbose_name=_("timestamp"),
    )
    additional_data = models.JSONField(
        blank=True, null=True, verbose_name=_("additional data"),
    )
    actor_email = models.CharField(
        blank=True, null=True, max_length=254, verbose_name=_("actor email"),
    )

    objects = LogEntryManager()

    class Meta:
        db_table = "auditlog_logentry"
        managed = False  # Table already exists from django-auditlog, Django should not manage it
        get_latest_by = "timestamp"
        ordering = ["-timestamp"]
        verbose_name = _("log entry")
        verbose_name_plural = _("log entries")

    def __str__(self):
        if self.action == self.Action.CREATE:
            fstring = _("Created {repr:s}")
        elif self.action == self.Action.UPDATE:
            fstring = _("Updated {repr:s}")
        elif self.action == self.Action.DELETE:
            fstring = _("Deleted {repr:s}")
        else:
            fstring = _("Logged {repr:s}")

        return fstring.format(repr=self.object_repr)
