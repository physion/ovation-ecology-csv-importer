"""Ovation Scientific Data Management System importer for CSV field data"""

# Copyright (c) 2013, Physion Consulting LLC

import logging

import pandas as pd

from ovation import *
from ovation.core import *

def import_csv(context, container_id=None, protocol_id=None, files=[]):

    assert(not protocol_id is None)
    assert(not container_id is None)

    container = EpochContainer.cast_(context.getObjectWithUuid(UUID.fromString(container_id)))
    protocol = Protocol.cast_(context.getObjectWithUuid(UUID.fromString(protocol_id)))

    for f in files:
        _import_file(context, container, protocol, f)

def _make_day_ends(d):
    return (d, d.plusDays(1).minusSeconds(1))

def _import_file(context, container, protocol, file_name):

    df = pd.read_csv(file_name)

    # Organize sources
    sites = {}
    for src in context.getSources():
        sites[src.getName()] = src

    for plot in df.SITE:
        if plot not in sites:
            logging.info("Adding site " + plot)
            sites[plot] = context.insertSource(plot, plot) #TODO better name?


    epoch_data = df.groupby(['DATE','SITE'])
    groups = {}
    for (name, group) in epoch_data:
        logging.info("Adding data for CSV group" + str(name))

        # Get the Source object corresponding to this site
        plot_name = name[1]
        plot = sites[plot_name]
        start,end = _make_day_ends(group.iloc[0]['DATE'])

        if start not in groups:
            group_name = "{}-{}-{}".format(start.getYear(), start.getMonthOfYear(), start.getDayOfMonth())
            print("Adding EpochGroup {}".format(group_name))
            groups[start] = EpochGroupContainer.cast_(experiment).insertEpochGroup(group_name, start, protocol, None, None) # No protocol, params, or deviceParams

        epoch_group = groups[start]

        srcMap = Maps.newHashMap()
        srcMap.put(plot_name, plot)
        outputMap = Maps.newHashMap()
        epoch = EpochContainer.cast_(epoch_group).insertEpoch(srcMap, outputMap, start, end, protocol, None, None)

        for (i, row) in group.iterrows():
            species = row['SPECIES']
            print("  {}".format(species))

            flower_count = row['COUNT']
            series = pd.Series(data=(flower_count,), index=(species,))
            tmp = tempfile.NamedTemporaryFile(prefix="{}-{}-{}-{}".format(start.getYear(), start.getMonthOfYear(), start.getDayOfMonth(), plot_name),
                                                suffix=".csv",
                                                delete=False)
            temp_data_frame = pd.DataFrame({'COUNT' : series })
            temp_data_frame.to_csv(tmp.name, index_label="Species")

            # Tag the Source with the species found there
            taggable(plot).addTag(species)

            srcNames = Sets.newHashSet()
            srcNames.add(plot_name)
            epoch.insertMeasurement(species,  srcNames, Sets.newHashSet(), URL("file://{}".format(tmp.name)), 'text/csv')


