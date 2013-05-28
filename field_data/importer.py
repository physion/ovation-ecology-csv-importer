"""Ovation Scientific Data Management System importer for CSV field data"""

# Copyright (c) 2013, Physion Consulting LLC

import logging

import pandas as pd
import numpy as np

from field_data.utils import read_csv

from ovation import *
from ovation.core import *

_CSV_HEADER_ROW = 2

def import_csv(context, container_id=None, protocol_id=None, files=[], timezone=None):

    assert(not protocol_id is None)
    assert(not container_id is None)

    container = EpochContainer.cast_(context.getObjectWithUuid(UUID.fromString(container_id)))
    protocol = Protocol.cast_(context.getObjectWithUuid(UUID.fromString(protocol_id)))

    for f in files:
        _import_file(context, container, protocol, f, _CSV_HEADER_ROW, timezone)

def _make_day_ends(python_datetime, tzone):
    """Makes a midnight,end-of-day DateTime pair from Python datetime and timezone ID"""

    d = DateTime(python_datetime.isoformat(), DateTimeZone.forID(tzone))
    return (d.toDateMidnight().toDateTime(), d.plusDays(1).minusSeconds(1))

def _import_file(context, container, protocol, file_name, header_row, timezone):

    df = read_csv(file_name, header_row=header_row)

    # Organize sources; this should be replaced with getSourceWithName() or a query
    sites = {}
    for src in context.getTopLevelSources():
        sites[src.getName()] = src

    for plot in df.Site:
        if plot not in sites:
            logging.info("Adding site " + plot)
            sites[plot] = context.insertSource(plot, plot) #TODO better name?


    # Group EpochData by (index, Site), i.e. (Date, Site)
    epoch_data = df.groupby([lambda x: x, lambda y: df.loc[y]['Site']])
    groups = {}
    for grp in EpochGroupContainer.cast_(container).getEpochGroups():
        groups[TimelineElement.cast_(grp).getStart()] = grp

    for (group_index, group) in epoch_data:
        logging.info("Adding data for CSV group" + str(group_index))

        # Get the Source object corresponding to this site
        plot_name = group_index[1]
        plot = sites[plot_name]
        pystart = group_index[0]
        start,end = _make_day_ends(pystart, timezone)

        if pystart not in groups:
            group_name = "{}-{}-{}".format(start.getYear(), start.getMonthOfYear(), start.getDayOfMonth())
            print("Adding EpochGroup {}".format(group_name))
            groups[pystart] = EpochGroupContainer.cast_(container).insertEpochGroup(group_name, start, protocol, None, None) # No protocol, params, or deviceParams

        epoch_group = groups[pystart]

        srcMap = Maps.newHashMap()
        srcMap.put(plot_name, plot)
        outputMap = Maps.newHashMap()

        # We should check if Epoch already exists
        epoch = EpochContainer.cast_(epoch_group).insertEpoch(srcMap, outputMap, start, end, protocol, None, None)

        for (i, row) in group.iterrows():
            species = row['Species']
            print("  {}".format(species))

            # flower_count = row['Count']
            # series = pd.Series(data=(flower_count,), index=(species,))
            # tmp = tempfile.NamedTemporaryFile(prefix="{}-{}-{}-{}".format(start.getYear(), start.getMonthOfYear(), start.getDayOfMonth(), plot_name),
            #                                     suffix=".csv",
            #                                     delete=False)
            # temp_data_frame = pd.DataFrame({'Count' : series })
            # temp_data_frame.to_csv(tmp.name, index_label="Species")
            #
            # # Tag the Source with the species found there
            # taggable(plot).addTag(species)
            #
            # srcNames = Sets.newHashSet()
            # srcNames.add(plot_name)
            # epoch.insertMeasurement(species,  srcNames, Sets.newHashSet(), URL("file://{}".format(tmp.name)), 'text/csv')


