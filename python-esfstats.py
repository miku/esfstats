#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from elasticsearch import Elasticsearch
import json
from pprint import pprint
import argparse

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='return field statistics of an ElasticSearch Search Index')
    parser.add_argument('-host',type=str,help='hostname or IP-Address of the ElasticSearch-node to use, default is localhost.')
    parser.add_argument('-port',type=int,help='Port of the ElasticSearch-node to use, default is 9200.')
    parser.add_argument('-index',type=str,help='ElasticSearch Search Index to use')
    parser.add_argument('-type',type=str,help='ElasticSearch Search Index Type to use')
    args=parser.parse_args()
    
    if args.port is None:
        args.port=9200
    es=Elasticsearch([{'host':args.host}],port=args.port)  
    page = es.search(
      index = args.index,
      doc_type = args.type,
      scroll = '2m',
      size = 1000,
      body = {},
      _source=True)
    sid = page['_scroll_id']
    scroll_size = page['hits']['total']
    
    # Start scrolling
    stats = {}
    while (scroll_size > 0):
      pages = es.scroll(scroll_id = sid, scroll='2m')
      sid = pages['_scroll_id']
      scroll_size = len(pages['hits']['hits'])
      hitcount=0
      for hits in pages['hits']['hits']:
        hitcount+=1
        for field in hits['_source']:
            if field not in stats:
                stats[field]=0
            if field in stats:
                stats[field]+=1
    print '{:50s}|{:14s}|{:14s}'.format("field name","exist-count","notexistcount")
    print "--------------------------------------------------|--------------|-------------"
    for key, value in stats.iteritems():
        print '{:50s}|{:14s}|{:14s}'.format(str(key),str(value),str(hitcount-int(value)))