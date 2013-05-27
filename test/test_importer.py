from nose.tools import istest

from ovation.testing import TestBase


class TestImporter(TestBase):

    @istest
    def should_add_sources(self):
        raise NotImplementedError()


    @istest
    def should_add_one_epoch_group_for_each_day(self):
        raise NotImplementedError()

    @istest
    def should_add_one_epoch_per_site(self):
        raise NotImplementedError()

    @istest
    def should_tag_site_with_species(self):
        raise NotImplementedError()

