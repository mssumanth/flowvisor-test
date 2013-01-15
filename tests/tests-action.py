"""
Slicing action verification tests
"""

import sys
import logging
import templatetest
import testutils
import oftest.cstruct as ofp
import oftest.message as message
import oftest.parse as parse
import oftest.action as action
import oftest.error as error
import socket

# ------ Start: Mandatory portion on each test case file ------

#@var basic_port_map Local copy of the configuration map from OF port
# numbers to OS interfaces
basic_port_map = None
#@var basic_logger Local logger object
basic_logger = None
#@var basic_timeout Local copy of global timeout value
basic_timeout = None
#@var basic_config Local copy of global configuration data
basic_config = None

test_prio = {}

def test_set_init(config):
    """
    Set up function for basic test classes
    @param config The configuration dictionary; see fvt
    """
    global basic_port_map
    global basic_fv_cmd
    global basic_logger
    global basic_timeout
    global basic_config

    basic_fv_cmd = config["fv_cmd"]
    basic_logger = logging.getLogger("flowdb")
    basic_logger.info("Initializing test set")
    basic_timeout = config["timeout"]
    basic_port_map = config["port_map"]
    basic_config = config

# ------ End: Mandatory portion on each test case file ------

    NUM_SW = 2
    NUM_CTL = 2


class DataLayerSourceAction(templatetest.TemplateTest):
    """
        Send Flow_mod message to change the dl_src
        and see if the dl_src to which it is changed is in the expected slice!
    """
    def setUp(self):
        templatetest.TemplateTest.setUp(self)
        self.logger = basic_logger
        # Set up the test environment
        # -- Note: default setting: config_file = test-base.xml, num of SW = 1, num of CTL = 2
        (self.fv, self.sv, sv_ret, ctl_ret, sw_ret) = testutils.setUpTestEnv(self, fv_cmd=basic_fv_cmd)
        self.chkSetUpCondition(self.fv, sv_ret, ctl_ret, sw_ret)

    def runTest(self):
        # Prepare a flow_mod using a simple pkt for controller0
        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10", dl_type=testutils.ETHERTYPE_ARP, nw_proto=testutils.ARP_REPLY)

        action_list = []
        act = action.action_set_dl_src()
        act.dl_addr=[0,1,0,0,0,2]

        action_list.append(act)
        flow_mod1 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod1]
        exp_list = [["switch", 0, flow_mod1]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod1: Received unexpected message" %(self.__class__.__name__))

class DataLayerSourceError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the dl_src
        and see if the dl_src to which it is changed is in the expected slice!
    """
    def runTest(self):
        #Add a rule to the fv config
        rule =  ["changeFlowSpace", "ADD", "33000", "all", "in_port=0,dl_src=00:00:00:00:00:02", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:00:00:00:00:02", dl_dst="00:00:00:00:00:02", dl_type=testutils.ETHERTYPE_ARP, nw_proto=testutils.ARP_REPLY)

        action_list = []
        act = action.action_set_dl_src()
        act.dl_addr=[0,2,0,0,0,2]

        action_list.append(act)
        flow_mod2 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        #Create a err mssg to chk if the appropriate error is thrown
        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_ARGUMENT
        err_msg.data = flow_mod2.pack()

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod2]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True, hdr_only=True)
        self.assertTrue(res, "%s: FlowMod2: Received unexpected message" %(self.__class__.__name__))

class DataLayerDestinationAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the dl_dst
        and see if the dl_dst to which it is changed is in the expected slice!
    """
    def runTest(self):
        #Add a dl_dst rule to the fv config
        rule =  ["changeFlowSpace", "ADD", "33000", "all", "in_port=0,dl_dst=00:00:00:00:00:02", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:11:00:00:00:02", dl_dst="00:00:00:00:00:02", dl_type=testutils.ETHERTYPE_ARP, nw_proto=testutils.ARP_REPLY)
        action_list = []
        act = action.action_set_dl_dst()
        act.dl_addr=[0,0,0,0,0,2]

        action_list.append(act)
        flow_mod3 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod3]
        exp_list = [["switch", 0, flow_mod3]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod3: Received unexpected message" %(self.__class__.__name__))


class DataLayerDestinationError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the dl_dst
        and see if the dl_dst to which it is changed is in the expected slice!
    """
    def runTest(self):
        pkt = testutils.simplePacket(dl_src="00:33:00:00:00:02", dl_dst="00:00:00:00:00:02", dl_type=testutils.ETHERTYPE_ARP, nw_proto=testutils.ARP_REPLY)
        action_list = []
        act = action.action_set_dl_dst()
        act.dl_addr=[0,1,0,0,0,2]

        action_list.append(act)
        flow_mod4 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        #Create a err mssg to chk if the appropriate error is thrown
        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_ARGUMENT
        err_msg.data = flow_mod4.pack()


        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod4]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True, hdr_only=True)
        self.assertTrue(res, "%s: FlowMod4: Received unexpected message" %(self.__class__.__name__))

class NetLayerSourceAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the nw_src
    """
    def runTest(self):
        #Add a nw_src rule to the fv config
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=0,nw_src=192.168.0.5", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(nw_src="192.168.0.5")

        action_list = []
        act = action.action_set_nw_src()
        act.nw_addr=3232235525

        action_list.append(act)
        flow_mod5 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod5]
        exp_list = [["switch", 0, flow_mod5]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod5: Received unexpected message" %(self.__class__.__name__))


class NetLayerSourceError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the nw_src
    """
    def runTest(self):
        pkt = testutils.simplePacket(nw_src="192.168.0.5")

        action_list = []
        act = action.action_set_nw_src()
        act.nw_addr=3232235520

        action_list.append(act)
        flow_mod6 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        #Create a err mssg to chk if the appropriate error is thrown
        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_ARGUMENT
        err_msg.data = flow_mod6.pack()

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod6]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True, hdr_only=True)
        self.assertTrue(res, "%s: FlowMod6: Received unexpected message" %(self.__class__.__name__))


class NetLayerDestinationAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the nw_dst
    """
    def runTest(self):
        #Add a nw_dst rule to the fv config
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=0,nw_dst=192.168.0.5", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=0,nw_dst=192.168.0.7", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(nw_dst="192.168.0.5")

        action_list = []
        act = action.action_set_nw_dst()
        act.nw_addr=3232235527

        action_list.append(act)
        flow_mod7 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod7]
        exp_list = [["switch", 0, flow_mod7]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod7: Received unexpected message" %(self.__class__.__name__))


class NetLayerDestinationError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the nw_dst
    """
    def runTest(self):
        pkt = testutils.simplePacket(nw_dst="192.168.0.5")

        action_list = []
        act = action.action_set_nw_dst()
        act.nw_addr=3232235520

        action_list.append(act)
        flow_mod8 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        #Create a err mssg to chk if the appropriate error is thrown
        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_ARGUMENT
        err_msg.data = flow_mod8.pack()

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod8]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True, hdr_only=True)
        self.assertTrue(res, "%s: FlowMod8: Received unexpected message" %(self.__class__.__name__))

class NetLayerTOSAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the nw_tos
    """
    def runTest(self):

        rule =  ["changeFlowSpace", "ADD", "35000", "all", "nw_tos=5", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        rule =  ["changeFlowSpace", "ADD", "35000", "all", "nw_tos=7", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(nw_tos=5)

        action_list = []
        act = action.action_set_nw_tos()
        act.nw_tos=7

        action_list.append(act)
        flow_mod9 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod9]
        exp_list = [["switch", 0, flow_mod9]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod9: Received unexpected message" %(self.__class__.__name__))

class NetLayerTOSError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the nw_tos
    """
    def runTest(self):
        pkt = testutils.simplePacket(nw_tos=5)

        action_list = []
        act = action.action_set_nw_tos()
        act.nw_tos=0

        action_list.append(act)
        flow_mod10 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_ARGUMENT
        err_msg.data = flow_mod10.pack()
        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod10]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True,hdr_only=True)
        self.assertTrue(res, "%s: FlowMod10: Received unexpected message" %(self.__class__.__name__))

class TransportLayerSourceAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the tp_src
    """
    def runTest(self):
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "tp_src=1020", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        rule =  ["changeFlowSpace", "ADD", "35000", "all", "tp_src=2020", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(tp_src=1020)
        action_list = []
        act = action.action_set_tp_src()
        act.tp_port=2020

        action_list.append(act)
        flow_mod11 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod11]
        exp_list = [["switch", 0, flow_mod11]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod11: Received unexpected message" %(self.__class__.__name__))

class TransportLayerSourceError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the tp_src
    """
    def runTest(self):

        pkt = testutils.simplePacket(tp_src=1020)
        action_list = []
        act = action.action_set_tp_src()
        act.tp_port=2022

        action_list.append(act)
        flow_mod12 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_ARGUMENT
        err_msg.data = flow_mod12.pack()

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod12]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True, hdr_only=True)
        self.assertTrue(res, "%s: FlowMod12: Received unexpected message" %(self.__class__.__name__))

class TransportLayerDestinationAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the tp_dst
    """
    def runTest(self):
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "tp_dst=25", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        rule =  ["changeFlowSpace", "ADD", "35000", "all", "tp_dst=80", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(tp_dst=80)
        action_list = []
        act = action.action_set_tp_dst()
        act.tp_port=25

        action_list.append(act)
        flow_mod13 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod13]
        exp_list = [["switch", 0, flow_mod13]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod13: Received unexpected message" %(self.__class__.__name__))



class TransportLayerDestinationError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the tp_dst
    """
    def runTest(self):
        pkt = testutils.simplePacket(tp_src=80)
        action_list = []
        act = action.action_set_tp_dst()
        act.tp_port=22

        action_list.append(act)
        flow_mod14 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_ARGUMENT
        err_msg.data = flow_mod14.pack()

        # Nor send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod14]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True,hdr_only=True)
        self.assertTrue(res, "%s: FlowMod14: Received unexpected message" %(self.__class__.__name__))

class VlanIdAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the dl_vlan
    """
    def runTest(self):
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_vlan=1080", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_vlan=2080", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:02", dl_vlan=1080)
        action_list = []
        act = action.action_set_vlan_vid()
        act.vlan_vid=2080

        action_list.append(act)
        flow_mod15 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod15]
        exp_list = [["switch", 0, flow_mod15]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod15: Received unexpected message" %(self.__class__.__name__))

class VlanIdError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the dl_vlan
    """
    def runTest(self):

        pkt = testutils.simplePacket(dl_vlan=3080)
        action_list = []
        act = action.action_set_vlan_vid()
        act.vlan_vid=80

        action_list.append(act)
        flow_mod16 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_ARGUMENT
        err_msg.data = flow_mod16.pack()

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod16]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True,hdr_only=True)
        self.assertTrue(res, "%s: FlowMod16: Received unexpected message" %(self.__class__.__name__))

class VlanPrioAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the nw_src
    """
    def runTest(self):
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10,dl_vlan=0x438,dl_vpcp=7", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10", dl_vlan=1080, dl_vlan_pcp=7)

        action_list = []

        act1 = action.action_set_vlan_pcp()
        act1.vlan_pcp=7
        action_list.append(act1)

        flow_mod17 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        snd_list = ["controller", 0, 0, flow_mod17]
        exp_list = [["switch", 0, flow_mod17]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod17: Received unexpected message" %(self.__class__.__name__))

class VlanPrioError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the nw_src
    """
    def runTest(self):
        pkt = testutils.simplePacket(dl_src="10:01:00:00:00:02", dl_dst="00:00:00:00:00:10", dl_vlan=180, dl_vlan_pcp=7)

        action_list = []

        act1 = action.action_set_vlan_pcp()
        act1.vlan_pcp=7
        action_list.append(act1)

        flow_mod18 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_ARGUMENT
        err_msg.data = flow_mod18.pack()

        snd_list = ["controller", 0, 0, flow_mod18]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True, hdr_only=True)
        self.assertTrue(res, "%s: FlowMod18: Received unexpected message" %(self.__class__.__name__))

class StripVlanAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the nw_src
    """
    def runTest(self):
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10,dl_vlan=200", "Slice:controller0=4"]
        #rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10", "Slice:controller0=4"]
        #rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_src=00:06:07:08:09:0a,dl_dst=00:01:02:03:04:05,dl_vlan=200", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10", dl_vlan=200,dl_vlan_pcp=7)
        #pkt = testutils.simplePacket(dl_src="00:06:07:08:09:0a", dl_dst="00:01:02:03:04:05", dl_vlan=200)
        action_list = []

        act = action.action_strip_vlan()
        action_list.append(act)

        flow_mod19 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod19]
        exp_list = [["switch", 0, flow_mod19]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod19: Received unexpected message" %(self.__class__.__name__))


class StripVlanError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the nw_src
    """
    def runTest(self):
        pkt = testutils.simplePacket(dl_src="10:01:00:00:00:02", dl_dst="00:00:00:00:00:10", dl_vlan=200,dl_vlan_pcp=7)

        action_list = []

        act = action.action_strip_vlan()
        action_list.append(act)

        flow_mod20 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_ARGUMENT
        err_msg.data = flow_mod20.pack()


        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod20]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True, hdr_only=True)
        self.assertTrue(res, "%s: FlowMod20: Received unexpected message" %(self.__class__.__name__))


class FVInPortAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the action output
    """
    def runTest(self):
        """
        Creating a rule with port number equal to the OFPP_IN_PORT port
        """
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=0,dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10", "Slice:controller0=4"]

        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10")

        action_list = []

        act = action.action_output()
        act.port = ofp.OFPP_IN_PORT
        action_list.append(act)

        flow_mod21 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod21]
        exp_list = [["switch", 0, flow_mod21]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod21: Received unexpected message" %(self.__class__.__name__))


class FVAllPortAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the action output
    """
    def runTest(self):
        """
        Creating a rule such that it matches the action_output with the OFPP_ALL port.
        """
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10", "Slice:controller0=4"]

        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10")

        action_list = []

        act = action.action_output()
        act.port = ofp.OFPP_ALL
        action_list.append(act)

        flow_mod22 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod22]
        exp_list = [["switch", 0, flow_mod22]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod22: Received unexpected message" %(self.__class__.__name__))



class FVTablePortAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the action output
    """
    def runTest(self):
        """
        Creating a rule such that it matches the action_output with the OFPP_TABLE port.
        """
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10", "Slice:controller0=4"]

        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10")

        action_list = []

        act = action.action_output()
        act.port = ofp.OFPP_TABLE
        action_list.append(act)

        flow_mod23 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod23]
        exp_list = [["switch", 0, flow_mod23]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod23: Received unexpected message" %(self.__class__.__name__))


class FVControllerPortAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the action output
    """
    def runTest(self):
        """
        Creating a rule such that it matches the action_output with the OFPP_CONTROLLER port.
        """
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10", "Slice:controller0=4"]

        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10")

        action_list = []

        act = action.action_output()
        act.port = ofp.OFPP_CONTROLLER
        action_list.append(act)

        flow_mod24 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod24]
        exp_list = [["switch", 0, flow_mod24]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod24: Received unexpected message" %(self.__class__.__name__))


class FVLocalPortAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the action output
    """
    def runTest(self):
        """
        Creating a rule with port number equal to 65534 which is the decimal equivalent of the OFPP_LOCAL port.
        """
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=65534,dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10", "Slice:controller0=4"]

        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10")

        action_list = []

        act = action.action_output()
        act.port = ofp.OFPP_LOCAL
        action_list.append(act)

        flow_mod25 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod25]
        exp_list = [["switch", 0, flow_mod25]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod25: Received unexpected message" %(self.__class__.__name__))
   
 
class FVNormalPortAction(DataLayerSourceAction):
    """
        Send Flow_mod message to change the action output
    """
    def runTest(self):
        """
        Creating a rule with port number equal to 65530 which is the decimal equivalent of the OFPP_NORMAL port.
        """
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=65530,dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10", "Slice:controller0=4"]

        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10")

        action_list = []

        act = action.action_output()
        act.port = ofp.OFPP_NORMAL
        action_list.append(act)

        flow_mod26 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod26]
        exp_list = [["switch", 0, flow_mod26]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod26: Received unexpected message" %(self.__class__.__name__))
    

class FVNormalPortError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the action output
    """
    def runTest(self):
        """
        Creating a rule with port number equal to 65531 which is not the decimal equivalent of the OFPP_NORMAL port.
        """
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=65531,dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10", "Slice:controller0=4"]

        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10")

        action_list = []

        act = action.action_output()
        act.port = ofp.OFPP_NORMAL
        action_list.append(act)

        flow_mod27 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)


        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_BAD_OUT_PORT
        err_msg.data = flow_mod27.pack()

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod27]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True, hdr_only=True)
        self.assertTrue(res, "%s: FlowMod27: Received unexpected message" %(self.__class__.__name__))
    

class FVInPortError(DataLayerSourceAction):
    """
        Send Flow_mod message to change the action output
    """
    def runTest(self):
        """
        Creating a rule with port number not equal to the in port.
        """
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=6,dl_src=00:01:00:00:00:02,dl_dst=00:00:00:00:00:10", "Slice:controller0=4"]

        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:10")

        action_list = []

        act = action.action_output()
        act.port = ofp.OFPP_IN_PORT
        action_list.append(act)

        flow_mod28 = testutils.genFloModFromPkt(self, pkt, ing_port=9, action_list=action_list)


        err_msg = error.bad_action_error_msg()
        err_msg.code = ofp.OFPBAC_EPERM
        err_msg.data = flow_mod28.pack()

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod28]
        exp_list = [["controller", 0, err_msg]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True, hdr_only=True)
        self.assertTrue(res, "%s: FlowMod28: Received unexpected message" %(self.__class__.__name__))
    



