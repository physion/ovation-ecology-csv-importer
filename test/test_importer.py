import datetime
from nose.tools import istest, assert_equals, assert_true

import pandas as pd
import numpy as np
from ovation import DateTime
from ovation.conversion import to_dict, iterable
from ovation.testing import TestBase

from field_data.importer import import_csv, \
    MEASUREMENT_TYPE_SITE, \
    FIRST_MEASUREMENT_COLUMN_NUMBER, \
    MEASUREMENT_TYPE_INDIVIDUAL
from field_data.utils import read_csv
from field_data.__main__ import main


EXAMPLE_FIELD_DATA_CSV = "fixtures/example_field_data.csv"


class TestImporter(TestBase):

    @classmethod
    def make_experiment_fixture(cls):
        ctx = cls.dsc.getContext()
        project = ctx.insertProject("name", "description", DateTime())
        expt = project.insertExperiment("purpose", DateTime())
        protocol = ctx.insertProtocol("protocol", "description")
        return ctx, expt, protocol

    @classmethod
    def setup_class(cls):
        TestBase.setup_class()

        cls.ctx, cls.expt, cls.protocol = cls.make_experiment_fixture()

        print("Importing example field data: {}".format(EXAMPLE_FIELD_DATA_CSV))
        import_csv(cls.ctx,
                   container_uri=str(cls.expt.getURI().toString()),
                   protocol_uri=str(cls.protocol.getURI().toString()),
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
        for s in iterable(sources):
            src_map[s.getLabel()] = s

        for name in expected_source_names:
            assert(src_map.has_key(name))


    def group_sites(self):
        return self.df.groupby([self.df.index, 'Site'])

    @istest
    def should_add_one_epoch_group_for_each_day(self):
        number_of_days = np.unique(np.asarray(self.df.index)).size

        assert_equals(number_of_days, len(list(iterable(self.expt.getEpochGroups()))))

    def check_epoch_per_site(self, container):
        # One Epoch per site per day
        num_sites = len(self.group_sites())
        n_epochs = 0
        for group in iterable(container.getEpochGroups()):
            # Skip Epochs specifically for producing Sources
            n_epochs += len([e for e in list(iterable(group.getEpochs())) if e.getOutputSources().size() == 0])
        assert_equals(num_sites, n_epochs)

    @istest
    def should_add_one_epoch_per_site(self):
        self.check_epoch_per_site(self.expt)

    @istest
    def should_use_existing_sources(self):
        expt2 = self.ctx.insertProject("project2","project2",DateTime()).insertExperiment("purpose", DateTime())
        protocol2 = self.ctx.insertProtocol("protocol", "description")

        import_csv(self.ctx,
                   container_uri=expt2.getURI().toString(),
                   protocol_uri=protocol2.getURI().toString(),
                   files=[EXAMPLE_FIELD_DATA_CSV])

        expected_source_names = np.unique(self.df.Site)

        sources = self.ctx.getTopLevelSources()

        assert_equals(len(expected_source_names), len(list(iterable(sources))))

    @istest
    def should_use_existing_site_epoch_when_present(self):
        expt2 = self.ctx.insertProject("project2","project2",DateTime()).insertExperiment("purpose", DateTime())
        protocol2 = self.ctx.insertProtocol("protocol", "description")

        import_csv(self.ctx,
                   container_uri=expt2.getURI().toString(),
                   protocol_uri=protocol2.getURI().toString(),
                   files=[EXAMPLE_FIELD_DATA_CSV])

        import_csv(self.ctx,
                   container_uri=expt2.getURI().toString(),
                   protocol_uri=protocol2.getURI().toString(),
                   files=[EXAMPLE_FIELD_DATA_CSV])

        self.check_epoch_per_site(expt2)

    @istest
    def should_tag_site_with_species(self):
        species = set(self.df.Species)

        for group in iterable(self.expt.getEpochGroups()):
            for epoch in iterable(group.getEpochs()):
                src_map = to_dict(epoch.getInputSources())
                for src in src_map.values():
                    if len(list(iterable(src.getParentSources()))) == 0:
                        tags = set(iterable(src.getAllTags()))
                        assert(len(tags) > 0)
                        for tag in tags:
                            assert(tag in species)


    def epoch_groups_by_timestamp(self):
        epoch_groups = {}
        for grp in iterable(self.expt.getEpochGroups()):
            d = grp.getStart()
            ts = pd.Timestamp(
                datetime.datetime(d.getYear(), d.getMonthOfYear(), d.getDayOfMonth(), d.getHourOfDay(),
                                  d.getMinuteOfHour(),
                                  d.getSecondOfMinute()))
            epoch_groups[ts] = grp
        return epoch_groups

    @istest
    def should_add_repeated_site_measurements(self):
        epoch_groups = self.epoch_groups_by_timestamp()

        for ((ts,site), group) in self.group_sites():
            epochs = self.collect_epochs_by_site(epoch_groups, ts)

            e = epochs[site]
            for i in xrange(len(group)):
                if group['Type'][i] == MEASUREMENT_TYPE_SITE:
                    m = e.getMeasurement(group['Species'][i])
                    csv_path = m.getLocalDataPath().get()
                    data = pd.read_csv(csv_path)
                    expected_measurements = group.iloc[i, FIRST_MEASUREMENT_COLUMN_NUMBER:].dropna()
                    assert(np.all(data[group['Counting'][i]] == expected_measurements))



    @istest
    def should_add_individual_measurements(self):
        epoch_groups = self.epoch_groups_by_timestamp()

        for ((ts,site), group) in self.group_sites():
            epochs = self.collect_epochs_by_site(epoch_groups, ts)
            e = epochs[site]

            for i in xrange(len(group)):
                if group['Type'][i] == MEASUREMENT_TYPE_INDIVIDUAL:
                    for m in iterable(e.getMeasurements()):
                        if m.getName().startswith(u"{}_{}".format(group['Species'][i],i+1)):
                            csv_path = m.getLocalDataPath().get()
                            data = pd.read_csv(csv_path)
                            expected_measurements = group.iloc[i, FIRST_MEASUREMENT_COLUMN_NUMBER:].dropna()
                            assert(np.all(data[group['Counting'][i]] == expected_measurements))

    def collect_epochs_by_site(self, epoch_groups, ts):
        epochs = {}
        for e in iterable(epoch_groups[ts].getEpochs()):
            sources = to_dict(e.getInputSources())
            for s in sources.values():
                if s.getLabel() in self.df.Site.base:
                    epochs[s.getLabel()] = e
        return epochs

    @istest
    def should_add_individual_measurement_sources(self):
        epoch_groups = self.epoch_groups_by_timestamp()

        for ((ts,site), group) in self.group_sites():
            epochs = self.collect_epochs_by_site(epoch_groups, ts)

            e = epochs[site]
            if 'individual' in list(iterable(e.getAllTags())):
                for i in xrange(len(group)):
                    if group['Type'][i] == MEASUREMENT_TYPE_INDIVIDUAL:
                        print(e.getInputSources(), group['Species'][i], i)
                        assert_true(e.getInputSources().containsKey(u"{} {}".format(group['Species'][i],i+1)))



    @istest
    def should_annotate_measurements_with_observer(self):
        epoch_groups = self.epoch_groups_by_timestamp()

        for ((ts,site), group) in self.group_sites():
            epochs = self.collect_epochs_by_site(epoch_groups, ts)

            e = epochs[site]

            for i in xrange(len(group)):
                if len(list(iterable(e.getMeasurements()))) > 0:
                    m = e.getMeasurement(group['Species'][i])
                    assert_equals(group['Observer'][i], str(m.getUserProperty(self.ctx.getAuthenticatedUser(), 'Observer')))

    @istest
    def should_call_via_main(self):
        expt2 = self.ctx.insertProject("project2","project2",DateTime()).insertExperiment("purpose", DateTime())
        protocol2 = self.ctx.insertProtocol("protocol", "description")

        number_of_days = np.unique(np.asarray(self.df.index)).size

        args = ['--timezone=America/New_York',
                '--container={}'.format(str(expt2.getURI().toString())),
                '--protocol={}'.format(str(protocol2.getURI().toString())),
                EXAMPLE_FIELD_DATA_CSV,
                ]

        main(args, dsc=self.dsc)

        assert_equals(number_of_days, len(list(iterable(expt2.getEpochGroups()))))
