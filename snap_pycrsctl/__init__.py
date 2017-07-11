import io
import socket
import re
import time
import subprocess as sp
import snap_plugin.v1 as snap
from crsctl import parser, checker
import logging

LOG = logging.getLogger(__name__)

class CrsctlCollector(snap.Collector):

    initialized = False
    config = None

    def __init__(self, *args, **kwargs):
        self.hostname = socket.gethostname().lower()
        super(CrsctlCollector, self).__init__(*args, **kwargs)

    def update_catalog(self, config):
        metrics = []

        metric = self.create_metric()
        metrics.append(metric)

        return metrics

    def collect(self, metrics):
        outmetrics = []
        retmetrics = []
        allresults = {}
        ts_now = time.time()

        if not self.initialized:
            self.config = metrics[0].config
            self.initialized = True

        output = self.get_crsctl_status_resource_output()
        che = checker.StatusResourceChecker()
        allresults['status_resource'] = che.check(self.config, output)
        output = self.get_crsctl_check_crs_output()
        che = checker.CheckCrsChecker()
        allresults['check_crs'] = che.check(output)
        for res in allresults:
            results = allresults[res]
            for result in results:
                items = results[result]
                for item in items:
                    metric = self.create_metric(item)
                    metric.data = int(result == 'True')
                    metric.timestamp = ts_now
                    outmetrics.append(metric)

        for mt in metrics:
            matching = self.lookup_metric_by_namespace(mt, outmetrics)
            if len(matching):
                retmetrics.extend(matching)

        return retmetrics

    def get_config_policy(self):
        return snap.ConfigPolicy()

    def get_crsctl_status_resource_output(self):
        proc = sp.Popen(['crsctl', 'status', 'resource'], stdout=sp.PIPE) #TODO: check 'crsctl' availability
        out = proc.stdout.read()
        stdout = out.encode('utf-8')
        # stdout = io.open('crsctl_output_2.txt', 'r').read()

        par = parser.StatusResourceParser()
        output = par.parse(stdout)
        return output

    def get_crsctl_check_crs_output(self):
        proc = sp.Popen(['crsctl', 'check', 'crs'], stdout=sp.PIPE) #TODO: check 'crsctl' availability
        out = proc.stdout.read()
        stdout = out.encode('utf-8')
        # stdout = io.open('crsctl_output_3.txt', 'r').read()

        par = parser.CheckCrsParser()
        output = par.parse(stdout)
        return output

    def create_metric(self, item = ''):
        metric = snap.Metric()
        metric.namespace.add_static_element('mfms')
        metric.namespace.add_static_element('crsctl')
        metric.namespace.add_dynamic_element('resource', 'resource name')
        metric.namespace.add_static_element('available')
        if item:
            metric.namespace[2].value = item
        return metric

    def namespace2str(self, ns, verb = False):
        st = ''
        for e in ns:
            if verb:
                st = (st + '/' + "[" + e.name + "]") if e.name else (st + '/' + e.value)
            else:
                st = st + '/' + e.value
        return st


    def lookup_metric_by_namespace(self, lookupmetric, metrics):
        ret = []
        lookupns = self.namespace2str(lookupmetric.namespace)
        lookupns = lookupns.replace('/', '\/').replace('*', '.*') + '$'
        nsre = re.compile(lookupns)
        for met in metrics:
            ns = self.namespace2str(met.namespace)
            match = nsre.search(ns)
            if match:
                ret.append(met)
        return ret
