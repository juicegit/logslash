# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
import json
import urllib2
import base64

import logging
import logging.config
import time

logging.config.fileConfig('logging.conf')

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
LOG = logging.getLogger(__name__)

from jinja2 import Environment, PackageLoader

if __name__ == '__main__':

    env = Environment(loader=PackageLoader('logslash', 'templates'))
    template = env.get_template('elastisearch_query.tmpl')
    prev_day_of_month = None
    #for i in range(1, 30):
    day_of_month = "%02d" % 1

    begin_datetime = '%s.09.2013 00:00:00' % day_of_month
    end_datetime = '15.09.2013 23:59:59'
    pattern = '%d.%m.%Y %H:%M:%S'

    range_beg = int(time.mktime(time.strptime(begin_datetime, pattern))) * 1000 - (8640000 * 2)
    range_end = int(time.mktime(time.strptime(end_datetime, pattern))) * 1000 + (8640000 * 2)
    query = template.render(source_host="<host>",
                            range_beg=range_beg,
                            range_end=range_end,
                            extra_params="")
    LOG.info("Getting log for %s to %s" % (begin_datetime, end_datetime))
    LOG.info("Query is %s" % query)
    date_range = 'logstash-2013.09.%s' % day_of_month
    for i in range(1, 1):
        date_range = date_range + (',logstash-2013.09.%02d' % i)
    LOG.info("URL Date Range is %s" % date_range)
    request = urllib2.Request(("https://<logstash_server>:8080/"
                              "%s/_search?pretty" % date_range),
                              data=query)
    base64string = base64.encodestring(
        '%s:%s' % ('<user>', '<password>')).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(request)
    search_result = result.read()
    result_dict = json.loads(search_result)
    results = result_dict['hits']['hits']
    for log_event in results:
        source = log_event['_source']
        LOG.info("@tags: %s, @timestamp: %s, @source_host: %s" %
                 (source['@tags'], source['@timestamp'], source['@source_host']))
