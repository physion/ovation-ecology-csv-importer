"""Ovation Scientific Data Management System importer for CSV field data"""

# Copyright (c) 2013, Physion Consulting LLC

import logging
import datetime
import tempfile

import pandas as pd
import numpy as np

from ovation import *
from ovation.core import *
from ovation.wrapper import taggable
from ovation.conversion import to_dict

from field_data.utils import read_csv

FIRST_MEASUREMENT_COLUMN_NUMBER = 5
CSV_HEADER_ROW = 2
DATE_COLUMN_NUMBER = 1

MEASUREMENT_TYPE_SITE = 'Site'
MEASUREMENT_TYPE_INDIVIDUAL = 'Individual'


def import_csv(context,
               container_id=None,
               protocol_id=None,
               files=[],
               timezone=None,
               csv_header_row=CSV_HEADER_ROW,
               first_measurement_column=FIRST_MEASUREMENT_COLUMN_NUMBER,
               date_column=DATE_COLUMN_NUMBER):

    assert(not protocol_id is None)
    assert(not container_id is None)

    container = EpochContainer.cast_(context.getObjectWithUuid(UUID.fromString(container_id)))
    protocol = Protocol.cast_(context.getObjectWithUuid(UUID.fromString(protocol_id)))

    for f in files:
        _import_file(context,
                     container,
                     protocol,
                     f,
                     csv_header_row,
                     timezone,
                     first_measurement_column,
                     date_column)

def _make_day_ends(python_datetime, tzone):
    """Makes a midnight,end-of-day DateTime pair from Python datetime and timezone ID"""

    d = DateTime(python_datetime.isoformat(), DateTimeZone.forID(tzone))
    return (d.toDateMidnight().toDateTime(), d.plusDays(1).minusSeconds(1))


def insert_measurements(epoch, group, i, measurements, plot_name, species, srcNames, start):
    tmp = tempfile.NamedTemporaryFile(
        prefix="{}-{}-{}-{}".format(start.getYear(), start.getMonthOfYear(), start.getDayOfMonth(),
                                    plot_name.replace('#', '')),
        suffix=".csv",
        delete=False)
    temp_data_frame = pd.DataFrame({group['Counting'][i]: measurements})
    temp_data_frame.to_csv(tmp.name, index_label="Measurement")
    epoch.insertMeasurement(species, srcNames, Sets.newHashSet(), URL("file://{}".format(tmp.name)), 'text/csv')


def _import_file(context, container, protocol, file_name, header_row, timezone, first_measurement_column_number, date_column):

    df = read_csv(file_name, header_row=header_row, date_column=date_column)

    # Organize sources; this should be replaced with getSourceWithName() or a query
    sites = {}
    for src in context.getTopLevelSources():
        sites[src.getLabel()] = src

    for plot in df.Site:
        if plot not in sites:
            logging.info("Adding site " + plot)
            sites[plot] = context.insertSource(plot, plot) #TODO better name?


    # Group EpochData by (index, Site), i.e. (Date, Site)
    epoch_data = df.groupby([lambda x: x, lambda y: df.loc[y]['Site']])
    groups = {}
    for grp in EpochGroupContainer.cast_(container).getEpochGroups():
        d = TimelineElement.cast_(grp).getStart()
        ts = pd.Timestamp(datetime.datetime(d.getYear(), d.getMonthOfYear(), d.getDayOfMonth(), d.getHourOfDay(), d.getMinuteOfHour(), d.getSecondOfMinute()))
        groups[ts] = grp

    for (group_index, group) in epoch_data:
        logging.info("Adding data for CSV group" + str(group_index))

        # Get the Source object corresponding to this site
        plot_name = group_index[1]
        plot = sites[plot_name]
        ts = group_index[0]
        start,end = _make_day_ends(ts, timezone)

        if ts not in groups:
            group_name = "{}-{}-{}".format(start.getYear(), start.getMonthOfYear(), start.getDayOfMonth())
            print("Adding EpochGroup {}".format(group_name))
            groups[ts] = EpochGroupContainer.cast_(container).insertEpochGroup(group_name, start, protocol, None, None) # No protocol, params, or deviceParams

        epoch_group = groups[ts]

        # Epoch by site
        epochs = {}
        for epoch in EpochContainer.cast_(epoch_group).getEpochs():
            src_map = to_dict(epoch.getInputSources())
            for src in src_map.values():
                epochs[src.getLabel()] = epoch


        src_map = Maps.newHashMap()
        src_map.put(plot_name, plot)
        output_src_map = Maps.newHashMap()

        # We should check if Epoch already exists
        if not plot_name in epochs:
            epochs[plot_name] = EpochContainer.cast_(epoch_group).insertEpoch(start, end, protocol, None, None)

        epoch = epochs[plot_name]

        for i in xrange(len(group)):
            species = group['Species'][i]
            observer = group['Observer'][i]


            # Tag the Source with the species found there
            taggable(plot).addTag(species)

            measurements = group.iloc[i, first_measurement_column_number:].dropna()

            if group['Type'][i] == MEASUREMENT_TYPE_SITE:

                epoch.addInputSource(plot_name, plot)

                srcNames = Sets.newHashSet()
                srcNames.add(plot_name)

                insert_measurements(epoch, group, i, measurements, plot_name, species, srcNames, start)

            elif group['Type'][i] == MEASUREMENT_TYPE_INDIVIDUAL:
                individual = plot.insertSource(EpochGroupContainer.cast_(epoch_group),
                                               start,
                                               end,
                                               protocol,
                                               Maps.newHashMap(),
                                               Optional.absent(),
                                               "{}_{}".format(species, i+1),
                                               species)

                epoch.addInputSource(individual.getLabel(), individual)
                srcNames = Sets.newHashSet()
                srcNames.add(individual.getLabel())
                insert_measurements(epoch, group, i, measurements, plot_name, species, srcNames, start)


    return 0
