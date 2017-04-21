from son.vmmanager.jsonserver import IJsonProcessor as P
from son.vmmanager.processors import utils

import tempfile
import logging
import os

class LB_MessageParser(object):

    MSG_LB_S11_IP_ADDR = 'lb_s11_ip_addr'
    MSG_LB_S1_IP_ADDR = 'lb_s1_ip_addr'
    MSG_LB_S5_IP_ADDR = 'lb_s5_ip_addr'
    MSG_LB_S11_PORT = 'lb_s11_port'
    MSG_LB_S1_PORT = 'lb_s1_port'
    MSG_LB_S5_PORT = 'lb_s5_port'

    MSG_SGW_S11_IP_ADDRS = 'sgw_s11_ip_addrs'
    MSG_SGW_S1_IP_ADDRS = 'sgw_s1_ip_addrs'
    MSG_SGW_S5_IP_ADDRS = 'sgw_s5_ip_addrs'
    MSG_SGW_S11_PORTS = 'sgw_s11_ports'
    MSG_SGW_S1_PORTS = 'sgw_s1_ports'
    MSG_SGW_S5_PORTS = 'sgw_s5_ports'

    MSG_CLEAR = 'clear'

    MSG = [MSG_SGW_S11_IP_ADDRS, MSG_SGW_S1_IP_ADDRS, MSG_SGW_S5_IP_ADDRS,
           MSG_LB_S11_IP_ADDR, MSG_LB_S1_IP_ADDR, MSG_LB_S5_IP_ADDR,
           MSG_SGW_S11_PORTS, MSG_SGW_S1_PORTS, MSG_SGW_S5_PORTS,
           MSG_LB_S11_PORT, MSG_LB_S1_PORT, MSG_LB_S5_PORT,
           MSG_CLEAR]

    def __init__(self, json_dict):
        self.logger = logging.getLogger(LB_MessageParser.__name__)
        self.msg_dict = json_dict
        self.command_parser = utils.CommandMessageParser(json_dict)

    def parse(self):
        arg_dict = {}
        for msg in self.MSG:
            arg_dict[msg] = self.msg_dict.get(msg, None)

        sc = LB_Config(**arg_dict)
        self.command_parser.parse(sc)
        return sc


class LB_Config(object):

    def __init__(self, sgw_s11_ip_addrs = None, sgw_s1_ip_addrs = None, sgw_s5_ip_addrs = None,
                 lb_s11_ip_addr = None, lb_s1_ip_addr = None, lb_s5_ip_addr = None,
                 sgw_s11_ports = None, sgw_s1_ports = None, sgw_s5_ports = None,
                 lb_s11_port = None, lb_s1_port = None, lb_s5_port = None, clear = None, **kwargs):
        self.sgw_s11_ip_addrs = sgw_s11_ip_addrs
        self.sgw_s1_ip_addrs = sgw_s1_ip_addrs
        self.sgw_s5_ip_addrs = sgw_s5_ip_addrs
        self.lb_s11_ip_addr = lb_s11_ip_addr
        self.lb_s1_ip_addr = lb_s1_ip_addr
        self.lb_s5_ip_addr = lb_s5_ip_addr
        self.sgw_s11_ports = sgw_s11_ports
        self.sgw_s1_ports = sgw_s1_ports
        self.sgw_s5_ports = sgw_s5_ports
        self.lb_s11_port = lb_s11_port
        self.lb_s1_port = lb_s1_port
        self.lb_s5_port = lb_s5_port
        self.clear = clear is not None


class LB_Processor(P):

    CMD_IPVSADM = 'ipvsadm'
    ADD_SERVICE = '-A -u %s:%s -s rr'
    ADD_REPLICA = '-a -u %s:%s -r %s:%s -g -w 1'
    CLEAR = '-C'

    def __init__(self):
        self.logger = logging.getLogger(LB_Processor.__name__)

        self._log_dir = tempfile.TemporaryDirectory(prefix='lb.processor')
        self._log_dir_name = self._log_dir.name

    def process(self, json_dict):
        parser = LB_MessageParser(json_dict)
        lb_config = parser.parse()

        if lb_config.clear:
            self._clear()

        self._addService(lb_config.lb_s11_ip_addr, lb_config.lb_s11_port)
        self._addService(lb_config.lb_s1_ip_addr, lb_config.lb_s1_port)
        self._addService(lb_config.lb_s5_ip_addr, lb_config.lb_s5_port)

        self._addReplicas(lb_config.lb_s11_ip_addr, lb_config.lb_s11_port,
                          lb_config.sgw_s11_ip_addrs, lb_config.sgw_s11_ports,
                          'SGW-S11')
        self._addReplicas(lb_config.lb_s1_ip_addr, lb_config.lb_s1_port,
                          lb_config.sgw_s1_ip_addrs, lb_config.sgw_s1_ports,
                          'SGW-S1')
        self._addReplicas(lb_config.lb_s5_ip_addr, lb_config.lb_s5_port,
                          lb_config.sgw_s5_ip_addrs, lb_config.sgw_s5_ports,
                          'SGW-S5')

    def _clear(self):
        r = utils.Runner(self.CMD_IPVSADM,
                         log_dir=self._log_dir_name,
                         append_log = True)
        r.setArguments(self.CLEAR)
        r.start()

    def _addService(self, ip, port):
        if ip is not None and port is not None:
            r = utils.Runner(self.CMD_IPVSADM,
                             log_dir=self._log_dir_name,
                             append_log = True)
            r.setArguments(self.ADD_SERVICE % (ip, port))
            r.start()
            r.join()

    def _addReplicas(self, lb_ip, lb_port, server_ips, server_ports, interface):
        if lb_ip is None or lb_port is None:
            msg = 'No %s loadbalancer parameters given.'
            self.logger.error(msg, interface)
            return P.Result.fail(msg, interface)

        if server_ips is None:
            msg = 'No %s parameters given.'
            self.logger.error(msg, interface)
            return P.Result.fail(msg, interface)

        if not isinstance(server_ips, list):
            msg = 'Invalid %s parameters given. A list of IPs and ports are required'
            self.logger.error(msg, interface)
            return P.Result.fail(msg, interface)

        if server_ports is None:
            server_ports = [None] * len(server_ips)

        if len(server_ips) is not len(server_ports):
            msg = 'Invalid %s parameters given. A list of IPs and ports must be the same length'
            self.logger.error(msg)
            return P.Result.fail(msg)

        for ip, port in zip(server_ips, server_ports):
            self._addReplica(lb_ip, lb_port, ip, port)

    def _addReplica(self, lb_ip, lb_port, server_ip, server_port):
        r = utils.Runner(self.CMD_IPVSADM,
                         log_dir=self._log_dir_name,
                         append_log = True)
        if server_port is None:
            r.setArguments(self.ADD_REPLICA % (lb_ip, lb_port,
                                               server_ip, lb_port))
        else:
            r.setArguments(self.ADD_REPLICA % (lb_ip, lb_port,
                                               server_ip, server_port))
        r.start()
        r.join()

