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


class passDataLayerSource(templatetest.TemplateTest):
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
        # Prepare a flow_mod for controller0
        # Flowmod1: outport=0
        #flow_mod1 = _setDataLayerSource(self, dl_src = "00:01:00:00:00:02")
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


class failDataLayerSource(passDataLayerSource):
    """
        Send Flow_mod message to change the dl_src 
        and see if the dl_src to which it is changed is in the expected slice!
    """

    def runTest(self):
        # Prepare a flow_mod for controller0
        # Flowmod1: outport=0
        #flow_mod2 = _setDataLayerSource(self, dl_src = "00:20:00:00:00:02")
	pkt = testutils.simplePacket(dl_src="00:01:00:00:00:02", dl_dst="00:00:00:00:00:02", dl_type=testutils.ETHERTYPE_ARP, nw_proto=testutils.ARP_REPLY)

	action_list = []
        act = action.action_set_dl_src()
        act.dl_addr=[0,22,0,0,0,2]

        action_list.append(act)
        flow_mod2 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod2]
        exp_list = [["switch", 0, flow_mod2]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertFalse(res, "%s: FlowMod2: Received unexpected message" %(self.__class__.__name__))

class passDataLayerDestination(passDataLayerSource):
    def runTest(self):
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

class failDataLayerDestination(passDataLayerSource):
    def runTest(self):
	#rule =  ["changeFlowSpace", "ADD", "33000", "all", "in_port=0,dl_dst=00:00:00:00:00:02", "Slice:controller0=4"]
        #(success, data) = testutils.setRule(self, self.sv, rule)
        #self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))
        
	pkt = testutils.simplePacket(dl_src="00:33:00:00:00:02", dl_dst="00:00:00:00:00:02", dl_type=testutils.ETHERTYPE_ARP, nw_proto=testutils.ARP_REPLY)
	action_list = []
        act = action.action_set_dl_dst()
        act.dl_addr=[0,1,0,0,0,2]

        action_list.append(act)
        flow_mod4 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)
	
	# Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod4]
        exp_list = [["switch", 0, flow_mod4]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertFalse(res, "%s: FlowMod4: Received unexpected message" %(self.__class__.__name__))

class passNetLayerSource(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
    """
    def runTest(self):
	rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=0,nw_src=192.168.0.5", "Slice:controller0=4"]
	#rule =  ["changeFlowSpace", "ADD", "33000", "all", "in_port=0,dl_src=00:11:00:00:00:02,dl_dst=00:22:00:00:22:00,nw_src=192.168.0.2", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))
        
	pkt = testutils.simplePacket(nw_src="192.168.0.5")
	#pkt = testutils.simplePacket(dl_src="00:11:00:00:00:02", dl_dst="00:22:00:00:22:00", dl_type=testutils.ETHERTYPE_ARP, nw_src="192.168.0.2", nw_proto=testutils.ARP_REPLY)
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

class failNetLayerSource(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
    """

    def runTest(self):
        #rule =  ["changeFlowSpace", "ADD", "33000", "all", "in_port=0,dl_src=00:11:00:00:00:02,dl_dst=00:22:00:00:22:00,nw_src=192.168.0.2", "Slice:controller0=4"]

        pkt = testutils.simplePacket(nw_src="192.168.0.5")
        #pkt = testutils.simplePacket(dl_src="00:11:00:00:00:02", dl_dst="00:22:00:00:22:00", dl_type=testutils.ETHERTYPE_ARP, nw_src="192.168.0.2", nw_proto=testutils.ARP_REPLY)
        action_list = []
        act = action.action_set_nw_src()
        act.nw_addr=3232235520

        action_list.append(act)
        flow_mod6 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod6]
        exp_list = [["switch", 0, flow_mod6]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertFalse(res, "%s: FlowMod6: Received unexpected message" %(self.__class__.__name__))


class passNetLayerDestination(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
    """
    def runTest(self):
	rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=0,nw_dst=192.168.0.5", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))
        
	rule =  ["changeFlowSpace", "ADD", "35000", "all", "in_port=0,nw_dst=192.168.0.7", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))
	
	pkt = testutils.simplePacket(nw_dst="192.168.0.5")
	#pkt = testutils.simplePacket(dl_src="00:11:00:00:00:02", dl_dst="00:22:00:00:22:00", dl_type=testutils.ETHERTYPE_ARP, nw_src="192.168.0.2", nw_proto=testutils.ARP_REPLY)
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

class failNetLayerDestination(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
    """

    def runTest(self):

        pkt = testutils.simplePacket(nw_dst="192.168.0.5")
        
	action_list = []
        act = action.action_set_nw_dst()
        act.nw_addr=3232235520

        action_list.append(act)
        flow_mod8 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod8]
        exp_list = [["switch", 0, flow_mod8]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertFalse(res, "%s: FlowMod8: Received unexpected message" %(self.__class__.__name__))

class passNetLayerTOS(passDataLayerSource):
    
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

class failNetLayerTOS(passDataLayerSource):

    def runTest(self):
        pkt = testutils.simplePacket(nw_tos=5)

        action_list = []
        act = action.action_set_nw_tos()
        act.nw_tos=0

        action_list.append(act)
        flow_mod10 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod10]
        exp_list = [["switch", 0, flow_mod10]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertFalse(res, "%s: FlowMod10: Received unexpected message" %(self.__class__.__name__))

class passTransportLayerSource(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
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

class failTransportLayerSource(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
    """
    def runTest(self):

        pkt = testutils.simplePacket(tp_src=1020)
        action_list = []
        act = action.action_set_tp_src()
        act.tp_port=2022

        action_list.append(act)
        flow_mod12 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod12]
        exp_list = [["switch", 0, flow_mod12]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertFalse(res, "%s: FlowMod12: Received unexpected message" %(self.__class__.__name__))

class passTransportLayerDestination(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
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

class failTransportLayerDestination(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
    """
    def runTest(self):

        pkt = testutils.simplePacket(tp_src=80)
        action_list = []
        act = action.action_set_tp_dst()
        act.tp_port=22

        action_list.append(act)
        flow_mod14 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod14]
        exp_list = [["switch", 0, flow_mod14]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertFalse(res, "%s: FlowMod14: Received unexpected message" %(self.__class__.__name__))

class passVlanId(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
    """
    def runTest(self):
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_vlan=1080", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_vlan=2080", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_vlan=1080)
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

class failVlanId(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
    """
    def runTest(self):

        pkt = testutils.simplePacket(dl_vlan=3080)
        action_list = []
        act = action.action_set_vlan_vid()
        act.vlan_vid=80

        action_list.append(act)
        flow_mod16 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod16]
        exp_list = [["switch", 0, flow_mod16]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertFalse(res, "%s: FlowMod16: Received unexpected message" %(self.__class__.__name__))

class passVlanPrio(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
    """
    def runTest(self):
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_vlan=1080", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule) 
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_vlan=2080", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_vlan=1080, dl_vlan_pcp=7 )
        
	action_list = []
	act = action.action_set_vlan_vid()
	act.vlan_vid=2080
	
	action_list.append(act)

        act1 = action.action_set_vlan_pcp()
        act1.vlan_pcp=5

        action_list.append(act1)
        flow_mod17 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod17]
        exp_list = [["switch", 0, flow_mod17]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod17: Received unexpected message" %(self.__class__.__name__))

class passStripVlan(passDataLayerSource):
    """
        Send Flow_mod message to change the nw_src 
    """
    def runTest(self):
        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_vlan=200", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        rule =  ["changeFlowSpace", "ADD", "35000", "all", "dl_vlan=300", "Slice:controller0=4"]
        (success, data) = testutils.setRule(self, self.sv, rule)
        self.assertTrue(success, "%s: Not success" %(self.__class__.__name__))

        pkt = testutils.simplePacket(dl_vlan=200)

        action_list = []
        act = action.action_strip_vlan()
        action_list.append(act)
        
	flow_mod19 = testutils.genFloModFromPkt(self, pkt, ing_port=0, action_list=action_list)

        # Now send those two commands and verify them
        snd_list = ["controller", 0, 0, flow_mod19]
        exp_list = [["switch", 0, flow_mod19]]
        res = testutils.ofmsgSndCmp(self, snd_list, exp_list, xid_ignore=True)
        self.assertTrue(res, "%s: FlowMod19: Received unexpected message" %(self.__class__.__name__))

