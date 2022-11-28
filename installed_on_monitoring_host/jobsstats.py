#!/usr/bin/env python3
#Copyright (c) 2022 Genome Research Ltd.
#
#Author: James Beal <James.Beal@sanger.ac.uk> , Dave Holland <dh3@sanger.ac.uk>
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#

import argparse
import json
import requests
import pwd
import grp
import time
import socket
import copy
from typing import Dict, Iterable, Callable, Any
from collections import defaultdict

STATS_PORT = 8080
GRAPHITE_SERVER = "node-3-5-7.internal.sanger.ac.uk"
GRAPHITE_PORT = "2003"
GRAPHITE_PREFIX = "jobstats-lustre"

proxies = {
    "http": None,
    "https": None,
}

StoreType = Dict[str, Dict[str, Dict[str, int]]]
RecordType = Dict[str, Dict[str, Any]]
# These are the metrics we send to graphana and how to read them.
metrics = {
    "read_bytes": "sum",
    "write_bytes": "sum",
    "close": "samples",
    "crossdir_rename": "samples",
    "getattr": "samples",
    "getxattr": "samples",
    "link": "samples",
    "mkdir": "samples",
    "mknod": "samples",
    "open": "samples",
    "punch": "samples",
    "rename": "samples",
    "rmdir": "samples",
    "samedir_rename": "samples",
    "setattr": "samples",
    "setxattr": "samples",
    "statfs": "samples",
    "sync": "samples",
    "unlink": "samples",
}


def accumulate_record(
    store: StoreType, record: RecordType, hash_name: str, data_label: str
):
    # This accumalates each metric in a hash
    for metric_name, lustre_kind in metrics.items():
        metric_value = record.get(metric_name, {}).get(lustre_kind, 0)
        value = record.get(data_label) or "unknown"
        if value not in store[hash_name]:
            store[hash_name][value] = defaultdict(lambda: 0)
        store[hash_name][value][metric_name] += metric_value


def consolidate_data(store: StoreType, data: Iterable[RecordType]):
    # Here we sort it by the metadata the web server on the
    # lustre server has added
    for record in data:
        accumulate_record(store, record, "byuid", "uid")
        accumulate_record(store, record, "byfarm", "farm")
        accumulate_record(store, record, "bygroup", "gid")
        accumulate_record(store, record, "bylsf_project", "project")


def uid_to_name(uid: str) -> str:
    try:
        return pwd.getpwuid(int(uid)).pw_name
    except (KeyError, ValueError):
        return "unknown"


def gid_to_name(gid: str) -> str:
    try:
        return grp.getgrgid(gid)[0]
    except (KeyError, ValueError):
        return "unknown"


def replace_with(dic: Dict[str, Any], map_func: Callable[[str], str]) -> Dict[str, Any]:
    # Apply a function to a set of keys in a hash and return a hash
    # this is used to map uid to username for example
    new_hash = {}
    for key, value in dic.items():
        new_key = "unknown"
        if key != "unknown":
            new_key = map_func(key)
        # The map function can duplicate keys throwing data away
        # so we end up accumatating again
        if new_key in new_hash:
            for copy_key, copy_value in new_hash[new_key].items():
                new_hash[new_key][copy_key] += copy_value
        else:
            new_hash[new_key] = copy.deepcopy(value)
    return new_hash


def send_to_graphite(socket: socket, field: str, dic: Dict[str, Any], debug: bool):
    now = int(time.time())
    for record in dic.keys():
        # We want the operation at the end
        kind, operation = field.split(".", 1)
        data_to_send = f"{GRAPHITE_PREFIX}.{lustre}.{kind}.{record}.{operation} {dic[record]} {now}\r\n"
        if debug:
            print(data_to_send)
        else:
            socket.sendall(data_to_send.encode())


# Parse the arguments
parser = argparse.ArgumentParser(
    description="Add statistics for a collection of lustre servers"
)
parser.add_argument("-lustre", required=True, help="Filesystem to store statistics to")
parser.add_argument(
    "-server",
    action="append",
    help="used to scan a lustre server, add for each server ost and mdt",
)
parser.add_argument(
    "-file",
    action="append",
    help="used to scan a lustre server, add for each server ost and mdt",
)
parser.add_argument(
    "-debug", action="store_const", const=True, help="Run in debug mode"
)
args = parser.parse_args()
debug = args.debug
servers = args.server or []
files = args.file or []
lustre = args.lustre

consolidated = {"byuid": {}, "bygroup": {}, "byfarm": {}, "bylsf_project": {}}
for data_source in servers + files:
    if data_source in servers:
        # contact each server and pull the stats from it in json
        try:
            response = requests.get(
                f"http://{data_source}:{STATS_PORT}", proxies=proxies
            )
            data = response.content
        except requests.exceptions.ConnectionError:
            pass
    else:
        with open(data_source, "r") as file:
            data = file.read()
    try:
        if len(data) == 0:
            parsed_data = {}
        else:
            parsed_data = json.loads(data)
    except ValueError as e:
        print(f"Invalid JSON {e}")
    for v in parsed_data.values():
        consolidate_data(consolidated, v)

# Replace uids,gids with the names of the equiverlents
consolidated_human = {
    "byusername": replace_with(consolidated["byuid"], uid_to_name),
    "bygroup": replace_with(consolidated["bygroup"], gid_to_name),
    "byfarm": consolidated["byfarm"],
    "bylsf_project": consolidated["bylsf_project"],
}

# rearranage the data how we want to send it to graphite
prepare_for_graphite = {}
for field in consolidated_human:
    for metric_name, lustre_kind in metrics.items():
        prepare_for_graphite[f"{field}.{metric_name}"] = {
            k: v[metric_name] for k, v in consolidated_human[field].items()
        }

graphite = socket.create_connection((GRAPHITE_SERVER, GRAPHITE_PORT))
for field in prepare_for_graphite:
    send_to_graphite(graphite, field, prepare_for_graphite[field], debug)
