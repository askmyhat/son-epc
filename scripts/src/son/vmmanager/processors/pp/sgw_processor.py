from son.vmmanager.jsonserver import IJsonProcessor as P
from son.vmmanager.processors import utils

import tempfile
import logging
import os

class SGW_MessageParser(object):

    MSG_S11_THREADS_COUNT = 's11_threads_count'
    MSG_S1_THREADS_COUNT = 's1_threads_count'
    MSG_S5_THREADS_COUNT = 's5_threads_count'
    MSG_SGW_S11_IP_ADDR = 'sgw_s11_ip_addr'
    MSG_SGW_S1_IP_ADDR = 'sgw_s1_ip_addr'
    MSG_SGW_S5_IP_ADDR = 'sgw_s5_ip_addr'
    MSG_PGW_S5_IP_ADDR = 'pgw_s5_ip_addr'
    MSG_LB_S11_IP_ADDR = 'lb_s11_ip_addr'
    MSG_LB_S1_IP_ADDR = 'lb_s1_ip_addr'
    MSG_LB_S5_IP_ADDR = 'lb_s5_ip_addr'
    MSG_DS_IP = 'ds_ip'
    MSG_DS_PORT = 'ds_port'
    MSG_SGW_S11_PORT = 'sgw_s11_port'
    MSG_SGW_S1_PORT = 'sgw_s1_port'
    MSG_SGW_S5_PORT = 'sgw_s5_port'
    MSG_PGW_S5_PORT = 'pgw_s5_port'

    MSG = [MSG_S11_THREADS_COUNT, MSG_S1_THREADS_COUNT, MSG_S5_THREADS_COUNT,
           MSG_SGW_S11_IP_ADDR, MSG_SGW_S1_IP_ADDR, MSG_SGW_S5_IP_ADDR,
           MSG_LB_S11_IP_ADDR, MSG_LB_S1_IP_ADDR, MSG_LB_S5_IP_ADDR,
           MSG_PGW_S5_IP_ADDR,
           MSG_DS_IP, MSG_DS_PORT, MSG_SGW_S11_PORT, MSG_SGW_S1_PORT,
           MSG_SGW_S5_PORT, MSG_PGW_S5_PORT]

    def __init__(self, json_dict):
        self.logger = logging.getLogger(SGW_MessageParser.__name__)
        self.msg_dict = json_dict
        self.command_parser = utils.CommandMessageParser(json_dict)

    def parse(self):
        arg_dict = {}
        for msg in self.MSG:
            arg_dict[msg] = self.msg_dict.get(msg, None)

        sc = SGW_Config(**arg_dict)
        self.command_parser.parse(sc)
        return sc


class SGW_Config(utils.CommandConfig):

    def __init__(self, s11_threads_count = None, s1_threads_count = None,
                 s5_threads_count = None, sgw_s11_ip_addr = None,
                 sgw_s1_ip_addr = None, sgw_s5_ip_addr = None,
                 lb_s11_ip_addr = None,
                 lb_s1_ip_addr = None, lb_s5_ip_addr = None,
                 pgw_s5_ip_addr = None, ds_ip = None, ds_port = None,
                 sgw_s11_port = None, sgw_s1_port = None, sgw_s5_port = None,
                 pgw_s5_port = None, **kwargs):
        self.s11_threads_count = s11_threads_count
        self.s1_threads_count = s1_threads_count
        self.s5_threads_count = s5_threads_count
        self.sgw_s11_ip_addr = sgw_s11_ip_addr
        self.sgw_s1_ip_addr = sgw_s1_ip_addr
        self.sgw_s5_ip_addr = sgw_s5_ip_addr
        self.lb_s11_ip_addr = lb_s11_ip_addr
        self.lb_s1_ip_addr = lb_s1_ip_addr
        self.lb_s5_ip_addr = lb_s5_ip_addr
        self.pgw_s5_ip_addr = pgw_s5_ip_addr
        self.ds_ip = ds_ip
        self.ds_port = ds_port
        self.sgw_s11_port = sgw_s11_port
        self.sgw_s1_port = sgw_s1_port
        self.sgw_s5_port = sgw_s5_port
        self.pgw_s5_port = pgw_s5_port

        super(self.__class__, self).__init__(**kwargs)

    def update(self, sgw_config):
        if not isinstance(sgw_config, SGW_Config):
            return

        if sgw_config.s11_threads_count is not None:
          self.s11_threads_count = sgw_config.s11_threads_count
        if sgw_config.s1_threads_count is not None:
          self.s1_threads_count = sgw_config.s1_threads_count
        if sgw_config.s5_threads_count is not None:
          self.s5_threads_count = sgw_config.s5_threads_count
        if sgw_config.sgw_s11_ip_addr is not None:
          self.sgw_s11_ip_addr = sgw_config.sgw_s11_ip_addr
        if sgw_config.sgw_s1_ip_addr is not None:
          self.sgw_s1_ip_addr = sgw_config.sgw_s1_ip_addr
        if sgw_config.sgw_s5_ip_addr is not None:
          self.sgw_s5_ip_addr = sgw_config.sgw_s5_ip_addr
        if sgw_config.lb_s11_ip_addr is not None:
          self.lb_s11_ip_addr = sgw_config.lb_s11_ip_addr
        if sgw_config.lb_s1_ip_addr is not None:
          self.lb_s1_ip_addr = sgw_config.lb_s1_ip_addr
        if sgw_config.lb_s5_ip_addr is not None:
          self.lb_s5_ip_addr = sgw_config.lb_s5_ip_addr
        if sgw_config.pgw_s5_ip_addr is not None:
          self.pgw_s5_ip_addr = sgw_config.pgw_s5_ip_addr
        if sgw_config.ds_ip is not None:
          self.ds_ip = sgw_config.ds_ip
        if sgw_config.ds_port is not None:
          self.ds_port = sgw_config.ds_port
        if sgw_config.sgw_s11_port is not None:
          self.sgw_s11_port = sgw_config.sgw_s11_port
        if sgw_config.sgw_s1_port is not None:
          self.sgw_s1_port = sgw_config.sgw_s1_port
        if sgw_config.sgw_s5_port is not None:
          self.sgw_s5_port = sgw_config.sgw_s5_port
        if sgw_config.pgw_s5_port is not None:
          self.pgw_s5_port = sgw_config.pgw_s5_port


class SGW_Processor(P):

    SGW_EXECUTABLE = '~/NFV_LTE_EPC/NFV_LTE_EPC-1.1/src/sgw.out'
    CMD_IPTABLES = 'iptables'
    ADD_IPTABLES = '-t nat -A PREROUTING -d %s -j REDIRECT'
    DEL_IPTABLES = '-t nat -D PREROUTING -d %s -j REDIRECT'

    def __init__(self):
        self.logger = logging.getLogger(SGW_Processor.__name__)

        self._log_dir = tempfile.TemporaryDirectory(prefix='sgw.processor')
        self._log_dir_name = self._log_dir.name
        self._iptables_log_dir_name = os.path.join(self._log_dir_name, 'iptables.out')
        os.mkdir(self._iptables_log_dir_name)
        self._runner = utils.Runner(self.SGW_EXECUTABLE,
                                    log_dir=self._log_dir_name)
        self._sgw_config = SGW_Config()

    def process(self, json_dict):
        parser = SGW_MessageParser(json_dict)
        sgw_config = parser.parse()
        self._handle_loadbalancing(sgw_config)
        self._sgw_config.update(sgw_config)

        if sgw_config.command == utils.CommandConfig.START:
            argset_res = self._setArguments()
            if argset_res.status is not P.Result.OK:
                return argset_res

            return self._runner.start()
        elif sgw_config.command == utils.CommandConfig.STOP:
            return self._runner.stop()
        elif sgw_config.command == utils.CommandConfig.RESTART:
            argset_res = self._setArguments()
            if argset_res.status is not P.Result.OK:
                return argset_res

            return self._runner.restart()
        elif sgw_config.command == utils.CommandConfig.STATUS:
            status = 'Running' if self._runner.isRunning() else 'Stopped'
            stdout = self._runner.getOutput()
            stderr = self._runner.getOutput(stderr=True)
            return P.Result.ok('Status', task_status = status,
                               stderr = stderr, stdout = stdout)
        elif sgw_config.command is None:
            return P.Result.warn('No command is given')
        else:
            return P.Result.fail('Invalid command is given %s',
                                 sgw_config.command)

    def _handle_loadbalancing(self, new_sgw_config):
        self.logger.debug('Handle loadbalancing setup (iptables)')
        isLb = new_sgw_config.lb_s11_ip_addr is not None
        isLb = isLb and new_sgw_config.lb_s1_ip_addr is not None
        isLb = isLb and new_sgw_config.lb_s5_ip_addr is not None

        if isLb:
            self._del_iptables(self._sgw_config.lb_s11_ip_addr)
            self._del_iptables(self._sgw_config.lb_s1_ip_addr)
            self._del_iptables(self._sgw_config.lb_s5_ip_addr)
            self._add_iptables(self.new_swg_config.lb_s11_ip_addr)
            self._add_iptables(self.new_swg_config.lb_s1_ip_addr)
            self._add_iptables(self.new_swg_config.lb_s5_ip_addr)
        else:
            self.logger.warn('LB config is not complet: %s, %s, %s',
                              new_swg_config.lb_s11_ip_addr,
                              new_swg_config.lb_s1_ip_addr,
                              new_swg_config.lb_s5_ip_addr)

    def _del_iptables(self, ip):
        if ip is None:
            return

        r =  utils.Runner(self.CMD_IPTABLES, arguments = self.DEL_IPTABLES % ip,
                          log_dir=self._iptables_log_dir_name,
                          append_log = True)
        r.start()

    def _add_iptables(self, ip):
        if ip is None:
            return

        r =  utils.Runner(self.CMD_IPTABLES, arguments = self.ADD_IPTABLES % ip,
                          log_dir=self._iptables_log_dir_name,
                          append_log = True)
        r.start()

    def _setArguments(self):
        nvalid = self._sgw_config.s11_threads_count is None
        nvalid = nvalid or self._sgw_config.s1_threads_count is None
        nvalid = nvalid or self._sgw_config.s5_threads_count is None
        nvalid = nvalid or self._sgw_config.sgw_s11_ip_addr is None
        nvalid = nvalid or self._sgw_config.sgw_s1_ip_addr is None
        nvalid = nvalid or self._sgw_config.sgw_s5_ip_addr is None
        nvalid = nvalid or self._sgw_config.pgw_s5_ip_addr is None
        nvalid = nvalid or self._sgw_config.ds_ip is None

        if nvalid:
            return P.Result.fail('IP for SGW (S1,S11,S5), PGW (S5) and threads count'
                                 'for S1 S11 S5 must be provided')

        args = ('--s11_threads_count %s --s1_threads_count %s '
               '--s5_threads_count %s --sgw_s11_ip_addr %s '
               '--sgw_s1_ip_addr %s --sgw_s5_ip_addr %s '
               '--pgw_s5_ip_addr %s --ds_ip %s')
        args = args % (self._sgw_config.s11_threads_count,
                       self._sgw_config.s1_threads_count,
                       self._sgw_config.s5_threads_count,
                       self._sgw_config.sgw_s11_ip_addr,
                       self._sgw_config.sgw_s1_ip_addr,
                       self._sgw_config.sgw_s5_ip_addr,
                       self._sgw_config.pgw_s5_ip_addr,
                       self._sgw_config.ds_ip)

        if self._sgw_config.ds_port is not None:
            args += ' --ds_port %s' % self._sgw_config.ds_port
        if self._sgw_config.sgw_s11_port is not None:
            args += ' --sgw_s11_port %s' % self._sgw_config.sgw_s11_port
        if self._sgw_config.sgw_s1_port is not None:
            args += ' --sgw_s1_port %s' % self._sgw_config.sgw_s1_port
        if self._sgw_config.sgw_s5_port is not None:
            args += ' --sgw_s5_port %s' % self._sgw_config.sgw_s5_port
        if self._sgw_config.pgw_s5_port is not None:
            args += ' --pgw_s5_port %s' % self._sgw_config.pgw_s5_port

        self._runner.setArguments(args)

        return P.Result.ok('Arguments are set')
