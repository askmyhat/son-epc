import son.vmmanager.processors.pp.lb_processor as lb_p
from son.vmmanager.processors.utils import CommandConfig
from son.vmmanager.jsonserver import IJsonProcessor as P

from unittest.mock import patch
from unittest.mock import Mock
import unittest
import tempfile
import logging
import os

logging.basicConfig(level=logging.DEBUG)

SGW_S11_IP_ADDRS = ['10.0.0.1',
                    '10.0.1.1']
SGW_S1_IP_ADDRS = ['10.0.0.2',
                   '10.0.1.2']
SGW_S5_IP_ADDRS = ['10.0.0.3',
                   '10.0.1.3']
SGW_S11_PORTS = ['1001',
                 '1011']
SGW_S1_PORTS = ['1002',
                '1012']
SGW_S5_PORTS = ['1003',
                '1013']
LB_S11_IP_ADDR = '20.0.0.1'
LB_S1_IP_ADDR = '20.0.0.2'
LB_S5_IP_ADDR = '20.0.0.3'
LB_S11_PORT = '2001'
LB_S1_PORT = '2002'
LB_S5_PORT = '2003'
CLEAR = 'clear'

config_dict = {
    'sgw_s11_ip_addrs': SGW_S11_IP_ADDRS,
    'sgw_s1_ip_addrs': SGW_S1_IP_ADDRS,
    'sgw_s5_ip_addrs': SGW_S5_IP_ADDRS,
    'sgw_s11_ports': SGW_S11_PORTS,
    'sgw_s1_ports': SGW_S1_PORTS,
    'sgw_s5_ports': SGW_S5_PORTS,
    'lb_s11_ip_addr': LB_S11_IP_ADDR,
    'lb_s1_ip_addr': LB_S1_IP_ADDR,
    'lb_s5_ip_addr': LB_S5_IP_ADDR,
    'lb_s11_port': LB_S11_PORT,
    'lb_s1_port': LB_S1_PORT,
    'lb_s5_port': LB_S5_PORT,
    'clear': 'TRUE',
    'garbage': {'key1': 1, 'key2': 2}
}


class LB_Processor(unittest.TestCase):

    @patch('son.vmmanager.processors.utils.Runner')
    def testProcessIssueCommand(self, RunnerMock):
        RunnerMock.return_value = Mock(wraps = RunnerMock)
        processor = lb_p.LB_Processor()
        processor.process(config_dict)

        SERVICE_NUMBER = 3
        REPLICA_NUMBER = 2
        CLEAR_NUMBER = 1
        self.assertEqual(RunnerMock.call_count,
                         SERVICE_NUMBER + SERVICE_NUMBER * REPLICA_NUMBER + CLEAR_NUMBER)
        RunnerMock.setArguments.assert_any_call('-C')
        RunnerMock.setArguments.assert_any_call('-A -u %s:%s -s rr' % (LB_S11_IP_ADDR, LB_S11_PORT))
        RunnerMock.setArguments.assert_any_call('-A -u %s:%s -s rr' % (LB_S1_IP_ADDR, LB_S1_PORT))
        RunnerMock.setArguments.assert_any_call('-A -u %s:%s -s rr' % (LB_S5_IP_ADDR, LB_S5_PORT))

        RunnerMock.setArguments.assert_any_call('-a -u %s:%s -r %s:%s -g -w 1' % (LB_S11_IP_ADDR, LB_S11_PORT,
                                                                                  SGW_S11_IP_ADDRS[0], SGW_S11_PORTS[0]))
        RunnerMock.setArguments.assert_any_call('-a -u %s:%s -r %s:%s -g -w 1' % (LB_S11_IP_ADDR, LB_S11_PORT,
                                                                                  SGW_S11_IP_ADDRS[1], SGW_S11_PORTS[1]))
        RunnerMock.setArguments.assert_any_call('-a -u %s:%s -r %s:%s -g -w 1' % (LB_S1_IP_ADDR, LB_S1_PORT,
                                                                                  SGW_S1_IP_ADDRS[0], SGW_S1_PORTS[0]))
        RunnerMock.setArguments.assert_any_call('-a -u %s:%s -r %s:%s -g -w 1' % (LB_S1_IP_ADDR, LB_S1_PORT,
                                                                                  SGW_S1_IP_ADDRS[1], SGW_S1_PORTS[1]))
        RunnerMock.setArguments.assert_any_call('-a -u %s:%s -r %s:%s -g -w 1' % (LB_S5_IP_ADDR, LB_S5_PORT,
                                                                                  SGW_S5_IP_ADDRS[0], SGW_S5_PORTS[0]))
        RunnerMock.setArguments.assert_any_call('-a -u %s:%s -r %s:%s -g -w 1' % (LB_S5_IP_ADDR, LB_S5_PORT,
                                                                                  SGW_S5_IP_ADDRS[1], SGW_S5_PORTS[1]))


class SGW_MsgParser(unittest.TestCase):
    def testFullConfigWithGarbage(self):
        parser = lb_p.LB_MessageParser(config_dict)
        config = parser.parse()

        self.assertEqual(config.sgw_s11_ip_addrs, SGW_S11_IP_ADDRS)
        self.assertEqual(config.sgw_s1_ip_addrs, SGW_S1_IP_ADDRS)
        self.assertEqual(config.sgw_s5_ip_addrs, SGW_S5_IP_ADDRS)
        self.assertEqual(config.sgw_s11_ports, SGW_S11_PORTS)
        self.assertEqual(config.sgw_s1_ports, SGW_S1_PORTS)
        self.assertEqual(config.sgw_s5_ports, SGW_S5_PORTS)
        self.assertEqual(config.lb_s11_ip_addr, LB_S11_IP_ADDR)
        self.assertEqual(config.lb_s1_ip_addr, LB_S1_IP_ADDR)
        self.assertEqual(config.lb_s5_ip_addr, LB_S5_IP_ADDR)
        self.assertEqual(config.lb_s11_port, LB_S11_PORT)
        self.assertEqual(config.lb_s1_port, LB_S1_PORT)
        self.assertEqual(config.lb_s5_port, LB_S5_PORT)
