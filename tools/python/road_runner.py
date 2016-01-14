#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import sys
import urllib2

from Queue import Queue
from threading import Thread

'''
World road map generation script.
It takes city points from omim intermediate data and calculates roads between them.
After all, it stores road features OSM way ids into csv text file.
'''

road_delta = 50
WORKERS = 16

def get_way_ids(point1, point2, server):
    url = "http://{0}/wayid?z=18&loc={1},{2}&loc={3},{4}".format(server, point1[0], point1[1], point2[0], point2[1])
    request = urllib2.urlopen(url)
    data = json.load(request)
    if "way_ids" in data:
        return data["way_ids"]
    return []

def each_to_each(points):
    result = []
    for i in range(len(points)):
        for j in range(len(points) - i - 1):
            result.append((points[i], points[j + i + 1]))
    return result

def load_towns(path):
    result = []
    if not os.path.isfile(path):
        print "WARNING! File with towns not found!"
        return result
    with open(path, "r") as f:
        for line in f:
            data = line.split(";")
            isCapital = (data[3][0] == "t")
            result.append((float(data[0]), float(data[1]), isCapital))
    return result

def parallel_worker(tasks, capitals_list, towns_list):
    while True:
        if not tasks.qsize() % 1000:
           print tasks.qsize()
        task = tasks.get()
        ids = get_way_ids(task[0], task[1], sys.argv[2])
        for id in ids:
            if task[0][2] and task[1][2]:
                capitals_list.add(id)
            else:
                towns_list.add(id)
        tasks.task_done()

if len(sys.argv) < 3:
    print "road_runner.py <intermediate_dir> <osrm_addr>"
    exit(1)

if not os.path.isdir(sys.argv[1]):
    print sys.argv[1], "is not a directory!"
    exit(1)

towns = load_towns(os.path.join(sys.argv[1], "towns.csv"))
print "Have {0} towns".format(len(towns))

tasks = each_to_each(towns)
filtered = []
for p1, p2 in tasks:
    if (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 < road_delta:
        filtered.append((p1,p2))
tasks = filtered

qtasks = Queue()
capitals_list = set()
towns_list = set()

for i in range(WORKERS):
    t=Thread(target=parallel_worker, args=(qtasks, capitals_list, towns_list))
    t.daemon = True
    t.start()

for task in tasks:
    qtasks.put(task)
qtasks.join()

with open(os.path.join(sys.argv[1], "ways.csv"),"w") as f:
    for way_id in capitals_list:
        print >> f, "{0};world_level".format(way_id)
    for way_id in towns_list:
        if way_id not in capitals_list:
            print >> f, "{0};world_towns_level".format(way_id)

print "All done."
