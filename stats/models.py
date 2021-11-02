from django.db import models, connection, transaction
from django.http import HttpRequest

from looper.utils import clean_ip_address


class _StaticAssetVisitMixin(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=('static_asset_id', 'user_id', 'ip_address')),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=('static_asset_id', 'ip_address'),
                name='%(app_label)s_%(class)s_ip_address_uniq_key',
                # Unique constraint can only be enforced on non-null values
                condition=models.Q(ip_address__isnull=False),
            ),
            models.UniqueConstraint(
                fields=('static_asset_id', 'user_id'),
                name='%(app_label)s_%(class)s_user_id_uniq_key',
                # Unique constraint can only be enforced on non-null values
                condition=models.Q(user_id__isnull=False),
            ),
        ]
        abstract = True

    # While IP address certainly doesn't represent a unique visitor,
    # it is a good enough compromise between being able to count unique anonymous visits and
    # having to sacrifice a lot of storage space for it.
    ip_address = models.GenericIPAddressField(protocol='both', null=True)
    user_id = models.PositiveIntegerField(null=True)
    static_asset = models.ForeignKey(
        'static_assets.StaticAsset', null=False, on_delete=models.CASCADE
    )

    @classmethod
    def create_from_request(cls, request: HttpRequest, static_asset_id: int):
        """Create a new record for the given StaticAsset ID based on the given request."""
        ip_address = clean_ip_address(request) if request.user.is_anonymous else None
        user_id = request.user.pk if request.user.is_authenticated else None
        cls.objects.bulk_create(
            [cls(ip_address=ip_address, user_id=user_id, static_asset_id=static_asset_id)],
            ignore_conflicts=True,
        )

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {} CASCADE'.format(cls._meta.db_table))

    @classmethod
    @transaction.atomic
    def update_counters_and_truncate(cls, to_field: str):
        from static_assets.models import StaticAsset

        static_asset_id_count = (
            cls.objects.all()
            .values('static_asset_id')
            .annotate(count=models.Count('static_asset_id'))
        )
        all_static_asset_ids = {_['static_asset_id'] for _ in static_asset_id_count}
        affected_static_assets = {
            _.pk: _ for _ in StaticAsset.objects.filter(id__in=all_static_asset_ids)
        }
        to_update = []
        for row in static_asset_id_count:
            static_asset_id = row['static_asset_id']
            count = row['count']
            static_asset = affected_static_assets[static_asset_id]
            setattr(static_asset, to_field, getattr(static_asset, to_field) + count)
            to_update.append(static_asset)
        StaticAsset.objects.bulk_update(
            to_update, batch_size=500, fields={to_field, 'date_updated'}
        )
        cls.objects.all().delete()

    def __str__(self) -> str:
        ip_address_f = f', IP {self.ip_address}' if self.ip_address else ''
        user_id_f = f', user ID {self.user_id}' if self.user_id else ''
        return f'{self.__class__.__name__} #{self.static_asset_id}{ip_address_f}{user_id_f}'


class Sample(models.Model):
    class Meta:
        ordering = ['timestamp']
        db_table = 'stats'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['timestamp', 'slug', 'value']),
        ]

    timestamp = models.DateTimeField(auto_now_add=True)
    # Should not be null, but was required by the migration
    slug = models.SlugField(null=True, blank=True)
    value = models.PositiveIntegerField(default=0)
    legacy_id = models.SlugField(null=True, blank=True)


class StaticAssetView(_StaticAssetVisitMixin, models.Model):
    pass


class StaticAssetDownload(_StaticAssetVisitMixin, models.Model):
    pass
