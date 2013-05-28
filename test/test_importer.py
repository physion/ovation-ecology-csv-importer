from nose.tools import istest, assert_equals

import pandas as pd
import numpy as np
from ovation import DateTime
from ovation.core import *
from ovation.testing import TestBase

from field_data.importer import import_csv
from field_data.utils import read_csv

EXAMPLE_FIELD_DATA_CSV = "fixtures/example_field_data.csv"


class TestImporter(TestBase):

    @classmethod
    def make_experiment_fixture(cls):
        ctx = cls.dsc.getContext()
        project = ctx.insertProject("name", "description", DateTime())
        expt = project.insertExperiment("purose", DateTime())
        protocol = ctx.insertProtocol("protocol", "description")
        return ctx, expt, protocol

    @classmethod
    def setup_class(cls):
        TestBase.setup_class()

        cls.ctx, cls.expt, cls.protocol = cls.make_experiment_fixture()

        import_csv(cls.ctx,
                   container_id=str(cls.expt.getUuid()),
                   protocol_id=str(cls.protocol.getUuid()),
                   files=[EXAMPLE_FIELD_DATA_CSV])

    def setup(self):
        self.ctx = self.__class__.ctx
        self.expt = self.__class__.expt
        self.protocol = self.__class__.protocol

        self.df = read_csv(EXAMPLE_FIELD_DATA_CSV)

    @istest
    def should_add_sources(self):
        expected_source_names = np.unique(self.df.Site)

        sources = self.ctx.getTopLevelSources()
        src_map = {}
        for s in sources:
            src_map[s.getLabel()] = s

        for name in expected_source_names:
            assert(src_map.has_key(name))


    def group_sites(self):
        return self.df.groupby([lambda x: x, lambda y: self.df.loc[y]['Site']])

    @istest
    def should_add_one_epoch_group_for_each_day(self):
        number_of_days = np.unique(np.asarray(self.df.index)).size

        assert_equals(number_of_days, len(list(EpochGroupContainer.cast_(self.expt).getEpochGroups())))

    @istest
    def should_add_one_epoch_per_site(self):
        # One Epoch per site per day
        numer_of_sites = len(self.group_sites())

        n_epochs = 0
        for group in EpochGroupContainer.cast_(self.expt).getEpochGroups():
            n_epochs += len(list(EpochContainer.cast_(group).getEpochs()))

        assert_equals(numer_of_sites, n_epochs)


    @istest
    def should_tag_site_with_species(self):
        for (group, (i, df_group)) in zip(EpochGroupContainer.cast_(self.expt).getEpochGroups(),
                                          self.group_sites()):
            number_of_sites = len(df_group)

            assert_equals(number_of_sites, len(list(EpochContainer.cast_(group).getEpochs())))

    @istest
    def should_add_site_flower_measurements(self):
        raise NotImplementedError()

    @istest
    def should_add_individual_flowers_per_stalk_measurement(self):
        raise NotImplementedError()

    @istest
    def should_add_individual_stalks_measurement(self):
        raise NotImplementedError()

