from son.client.protocol import ClientFactory
from twisted.internet import reactor

import argparse
import logging
import sys

class HostNames(object):
    def __init__(self, hss, mme, sgw):
        self.hss = hss
        self.mme = mme
        self.sgw = sgw

class Ds(object):
    def __init__(self, ip):
        self.ip = ip

class Hss(object):
    def __init__(self, mgmt_ip, s11_ip, threads_count):
        self.threads_count = threads_count
        self.mgmt_ip = mgmt_ip
        self.s11_ip = s11_ip

class Mme(object):
    def __init__(self, mgmt_ip, s11_ip, s1_ip, threads_count, trafmon_ip):
        self.threads_count = thread_count
        self.mgmt_ip = mgmt_ip
        self.s11_ip = s11_ip
        self.s1_ip = s1_ip
        self.trafmon_ip = trafmon_ip

class Pgw(object):
    def __init__(self, mgmt_ip, s5_ip, sgi_ip, sink_ip,
                 s5_threads_count, sgi_threads_count,):
        self.mgmt_ip = mgmt_ip
        self.s5_ip = s5_ip
        self.sgi_ip = sgi_ip
        self.sink_ip = sink_ip
        self.s5_threads_count = s5_threads_count
        self.sgi_threads_count = sgi_threads_count

class Sgw(object):
    def __init__(self, mgmt_ip, s11_ip, s1_ip, s5_ip,
                 s11_threads_count, s1_threads_count,
                 s5_threads_count):
        self.mgmt_ip = mgmt_ip
        self.s11_ip = s11_ip
        self.s1_ip = s1_ip
        self.s5_ip = s5_ip
        self.s11_threads_count = s11_threads_count
        self.s1_threads_count = s1_threads_count
        self.s5_threads_count = s5_threads_count

class Lb(object):
    def __init__(self, mgmt_ip, s11_ip, s1_ip, s5_ip, s11_port, s1_port, s5_port):
        self.mgmt_ip = mgmt_ip
        self.s11_ip = s11_ip
        self.s1_ip = s1_ip
        self.s5_ip = s5_ip
        self.s11_port = s11_port
        self.s1_port = s1_port
        self.s5_port = s5_port

class Client(object):

    def __init__(self, hss, mme, sgw, hosts, pgw, ds, lb, isPp = False):
        self.hss = hss
        self.mme = mme
        self.sgw = sgw
        self.hosts = hosts
        self.pgw = pgw
        self.ds = ds
        self.lb = lb
        self.isPp = isPp
        self._init_configs()

    def _init_connection(self, isStopping = False):
        if self.isPp:
            sgw_mgmts = self.sgw.mgmt_ip.split(',')
            sgw_configs = zip(sgw_mgmts, self.sgw_config)
            self.factory = ClientFactory([
                (self.hss.mgmt_ip, self.hss_config),
                (self.mme.mgmt_ip, self.mme_config),
                (self.pgw.mgmt_ip, self.pgw_config),
                (self.lb.mgmt_ip, self.lb_config)
            ] + sgw_configs, isStopping = isStopping)
        else:
            self.factory = ClientFactory([
                (self.hss.mgmt_ip, self.hss_config),
                (self.mme.mgmt_ip, self.mme_config),
                (self.sgw.mgmt_ip, self.spgw_config)
            ], isStopping = isStopping)

    def _init_configs(self):
        self._init_hosts()
        self._init_hss_config()
        self._init_mme_config()
        self._init_spgw_config()
        self.__init_lb_config()

    def _init_lb_config(self):
        if self.isPp:
            self.lb_config = {
                'lb_s11_ip_addr': self.lb.s11_ip,
                'lb_s1_ip_addr': self.lb.s1_ip,
                'lb_s5_ip_addr': self.lb_s5_ip,
                'lb_s11_port': self.lb_s11_port,
                'lb_s1_port': self.lb_s1_port,
                'lb_s5_port': self.lb_s5_port,
                'sgw_s11_ip_addrs': self.sgw.s11_ip.split(','),
                'sgw_s1_ip_addrs': self.sgw.s1_ip.split(','),
                'sgw_s5_ip_addrs': self.sgw.s5_ip.split(',')
            }

    def _init_hosts(self):
        if not self.isPp:
            self.hosts = {
                'hss': {
                    'host_name': '%s.openair4G.eur' % self.hosts.hss,
                    'ip': self.hss.s11_ip
                },
                'mme': {
                    'host_name': '%s.openair4G.eur' % self.hosts.mme,
                    'ip': self.mme.s11_ip
                },
                'spgw': {
                    'host_name': '%s.openair4G.eur' % self.hosts.sgw,
                    'ip': self.sgw.s11_ip
                }
            }

    def _init_hss_config(self):
        if self.isPp:
            self.hss_config = {
                'threads_count': self.hss.thread_counts,
                'ip': self.hss.s11_ip,
                'ds_ip': self.ds.ip,
            }
        else:
            self.hss_config = {
                'hosts': self.hosts,
                'mysql': {
                    'user': 'root',
                    'pass': 'hurka'
                }
            }

    def _init_mme_config(self):
        if self.isPp:
            self.mme_config = {
                'threads_count': self.mme.thread_counts,
                'hss_ip': self.hss.s11_ip,
                'sgw_s1_ip': self.sgw.s1_ip,
                'sgw_s11_ip': self.sgw.s11_ip,
                'sgw_s5_ip': self.sgw.s5_ip,
                'ds_ip': self.ds.ip,
                'mme_s1_ip': self.mme.s1_ip,
                'mme_s11_ip': self.mme.s11_ip,
                'pgw_s5_ip': self.pgw.s5_ip,
                'trafmon_ip': self.mme.trafmon_ip
            }
        else:
            self.mme_config = {
                'hosts': self.hosts,
                's1_ip': self.mme.s1_ip
            }

    def _init_spgw_config(self):
        if self.isPp:
            self.pgw_config = {
                's5_threads_count': self.pgw.s5_threads_count,
                'sgi_threads_count': self.pgw.sgi_threads_count,
                'sgw_s5_ip': self.sgw.s5_ip,
                'pgw_s5_ip': self.pgw.s5_ip,
                'pgw_sgi_ip': self.pgw.sgi_ip,
                'ds_ip': self.ds.ip,
                'sink_ip_addr': self.pgw.sink_ip
            }
            mgmts = self.sgw.mgmt_ip.split(',')
            s11s = self.sgw.s11_ip.split(',')
            s1s = self.sgw.s1_ip.split(',')
            s5s = self.sgw.s5_ip.split(',')
            if len(mgmts) is not len(s11s) or \
                len(mgmts) is not len(s1s) or \
                len(mgmts) is not len(s5s):
                raise Exception('Comman separted list of IPs for'
                                'SGW-MGMT, SGW-S11, SGW-S5, SGW-S1'
                                'must be the same lenght')

            self.sgw_config = []
            for mgmt, s11, s1, s5 in zip(mgmts, s11s, s1s, s5s):
                config = {
                    's11_threads_count': self.sgw.s11_threads_count,
                    's1_threads_count': self.sgw.s1_threads_count,
                    's5_threads_count': self.sgw.s5_threads_count,
                    'sgw_s11_ip_addr': s11,
                    'sgw_s1_ip_addr': s1,
                    'sgw_s5_ip_addr':s5,
                    'ds_ip': self.ds.ip,
                    'pgw_s5_ip_addr': self.pgw.s5_ip,
                    'lb_s11_ip': self.lb.s11_ip,
                    'lb_s1_ip': self.lb.s1_ip,
                    'lb_s5_ip': self.lb.s5_ip
                }
                self.sgw_config.append(config)
        else:
            self.spgw_config = {
                'hosts': self.hosts,
                'sgi_ip': self.pgw.sgi_ip,
                's1u_ip': self.sgw.s1_ip
            }

    def start(self):
        self._init_connection()
        reactor.run()

    def stop(self):
        self._init_connection(isStopping = True)
        reactor.run()


def parseConfigArgs(argv):
    configArguments = argparse.ArgumentParser()
    configArguments.add_argument('--hss_mgmt', required=True,
                                 help='Management address for HSS')
    configArguments.add_argument('--hss_data', required=True,
                                 help='Data plane address for HSS')
    configArguments.add_argument('--hss_host', required=True,
                                 help='Hostname for HSS')
    configArguments.add_argument('--mme_mgmt', required=True,
                                 help='Management address for MME')
    configArguments.add_argument('--mme_data', required=True,
                                 help='Data plane address for MME')
    configArguments.add_argument('--mme_host', required=True,
                                 help='Hostname for MME')
    configArguments.add_argument('--spgw_mgmt', required=True,
                                 help='Management address for SPGW')
    configArguments.add_argument('--spgw_data', required=True,
                                 help='Data plane address for SPGW')
    configArguments.add_argument('--spgw_host', required=True,
                                 help='Hostname for SPGW')
    return configArguments.parse_args(argv)

def parseNetworkArgs(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--mme_s1_ip', required=True,
                                 help='Public IP of MME')
    parser.add_argument('--spgw_s1_ip', required=True,
                                 help='Public IP of SPGW')
    parser.add_argument('--spgw_sgi_ip', required=True,
                                 help='External IP of SPGW')
    return parser.parse_known_args(argv)

def parsePPScenarioSpecific(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--sgw_s5_ip', required=True,
                        help='S5 IP of SGW')
    parser.add_argument('--pgw_s5_ip', required=True,
                        help='S5 IP of PGW')
    parser.add_argument('--trafmon_ip', required=True,
                        help='IP of traffic monitor')
    parser.add_argument('--sink_ip', required=True,
                        help='IP of sink')
    parser.add_argument('--pgw_mgmt', required=True,
                        help='Management IP of PGW')
    parser.add_argument('--ds_ip', required=True,
                        help='IP of the common datastore')

    parser.add_argument('--lb_mgmt', required=True,
                        help='IP of the load balancer')
    parser.add_argument('--lb_s11_ip', required=True,
                        help='IP of the load balancer for SGW-S11')
    parser.add_argument('--lb_s11_port', required=True,
                        help='Port of the load balancer for SGW-S11')
    parser.add_argument('--lb_s1_ip', required=True,
                        help='IP of the load balancer for SGW-S1')
    parser.add_argument('--lb_s1_port', required=True,
                        help='Port of the load balancer for SGW-S1')
    parser.add_argument('--lb_s5_ip', required=True,
                        help='IP of the load balancer for SGW-S5')
    parser.add_argument('--lb_s5_port', required=True,
                        help='Port of the load balancer for SGW-S5')
    return parser.parse_known_args(argv)

def parseGeneralArgs(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose','-v', action='store_true', dest='verbose',
                        default=False, help='Verbose')
    parser.add_argument('--stop','-s', action='store_true', dest='stop',
                        default=False, help='Verbose')
    parser.add_argument('--oai', action='store_true', dest='oai',
                        default=False, help='OpenAirInterface')
    parser.add_argument('--pp', action='store_true', dest='pp',
                        default=False, help='Pratik Satapathy')
    return parser.parse_known_args(argv)


def main(argv = sys.argv[1:]):
    generalArgs, remaining_argv = parseGeneralArgs(argv)
    networkArgs, remaining_argv = parseNetworkArgs(remaining_argv)
    if generalArgs.pp:
        scenarioArgs, remaining_argv = parsePPScenarioSpecific(remaining_argv)
    configArgs = parseConfigArgs(remaining_argv)

    if generalArgs.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info('Got cli parameters:')
    configDict = vars(configArgs)
    for param in configDict:
        logger.info('%s -> %s', param, configDict[param])

    if scenarioArgs.oai:
        c = Client(
            hss = Hss(configArg.hss_mgmt, configArgs.hss_data, None),
            mme = Mme(configArgs.mme_mgmt, configArgs.mme_data,
                      networkArgs.mme_s1_ip, None, None),
            sgw = Sgw(configArgs.spgw_mgmt, configArgs.spgw_data,
                      networkArgs.spgw_s1_ip, None, None, None, None),
            pgw = Pgw(self, None, None, networkArgs.spgw_sgi_ip,
                      None, None, None),
            hosts = HostNames(configArgs.hss_host, configArgs.mme_host,
                              configArgs.spgw_host),
            ds = None,
            lb = None)
    elif scenarioArgs.pp:
        c = Client(
                hss = Hss(configArg.hss_mgmt, configArgs.hss_data, '2'),
                mme = Mme(configArgs.mme_mgmt, configArgs.mme_data,
                          networkArgs.mme_s1_ip, '2', scenarioArgs.trafmon_ip),
                sgw = Sgw(configArgs.spgw_mgmt, configArgs.spgw_data,
                          networkArgs.spgw_s1_ip, scenarioArgs.sgw_s5_ip,
                          '2', '2', '2'),
                pgw = Pgw(self, scenarioArgs.pgw_mgmt, scenarioArgs.pgw_s5_ip,
                          networkArgs.spgw_sgi_ip, scenarioArgs.sink_ip,
                          '2', '2'),
                ds = Ds(scenarioArgs.ds_ip),
                lb = Lb(scenarioArgs.lb_mgmt, scenarioArgs.lb_s11_ip,
                        scenarioArgs.lb_s1_ip, scenarioArgs.lb_s5_ip,
                        scenarioArgs.lb_s11_port, scenarioArgs.lb_s1_port,
                        scenarioArgs.lb_s5_port),
                hosts = None)
    else:
        logger.error('--oai or --pp must be specified to select EPC implementation')
        return


    if generalArgs.stop:
        c.stop()
    else:
        c.start()
