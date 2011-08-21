# -*- coding: utf-8 -*-

from django.db.models import Manager


class PublicManager(Manager):
    def published(self):
        return super(PublicManager, self).get_query_set().filter(estado=True)
