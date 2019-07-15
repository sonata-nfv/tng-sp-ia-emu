# Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, 5GTANGO
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).
#
# This work has been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the 5GTANGO
# partner consortium (www.5gtango.eu).

import logging
import threading
import concurrent.futures as pool
import uuid
import time
import yaml
import json
import requests
import uuid

from emulator_wrapper import messaging
from emulator_wrapper import plugin
from emulator_wrapper import emu_topics as t
from emulator_wrapper.logger import TangoLogger

LOG = TangoLogger.getLogger(__name__, log_level=logging.INFO, log_json=False)

class EmulatorWrapper(plugin.ManoBasePlugin):
    """
    This class implements the emulator wrapper.
    """

    def __init__(self,
                 auto_register=False,
                 wait_for_registration=False,
                 start_running=True):

        # Create the ledger that saves state
        self.ledger = {}
        self.infra = {}
        self.wim = str(uuid.uuid4())
        self.emu_busy = False
        self.emu_active = True

        self.thrd_pool = pool.ThreadPoolExecutor(max_workers=1)

        # call super class (will automatically connect to
        # broker and register the SLM to the plugin manger)
        ver = "0.1-dev"
        des = "This is the Emulator wrapper"

        self.network_counter = 10

        # try:
        self.populate_infrastructure_database()
        if t.wrapper_part_of_ia:
            self.register_wrapper_in_ia_registry()
        # except:
        #     LOG.info("Failed to connect to emulator...")
        #     self.emu_active = False

        wait_reg = wait_for_registration
        super(self.__class__, self).__init__(version=ver,
                                             description=des,
                                             auto_register=auto_register,
                                             wait_for_registration=wait_reg,
                                             start_running=start_running)

    def __del__(self):
        """
        Destroy the wrapper. De-register. Disconnect.
        :return:
        """
        super(self.__class__, self).__del__()

    def declare_subscriptions(self):
        """
        Declare topics that the wrapper subscribes on.
        """
        # We have to call our super class here
        super(self.__class__, self).declare_subscriptions()

        self.manoconn.subscribe(self.deploy_vnf, t.VNF_DEPLOY)

        self.manoconn.subscribe(self.remove_vnf, t.VNF_REMOVE)

        self.manoconn.subscribe(self.add_wan, t.WAN_ADD)

        self.manoconn.subscribe(self.remove_wan, t.WAN_REMOVE)

        self.manoconn.subscribe(self.create_network, t.NETWORK_CREATE)

        self.manoconn.subscribe(self.remove_network, t.NETWORK_REMOVE)

        self.manoconn.subscribe(self.remove_service, t.SERVICE_REMOVE)

        self.manoconn.subscribe(self.comp_resources, t.COMP_RESOURCES)

        self.manoconn.subscribe(self.net_resources, t.NET_RESOURCES)

        self.manoconn.subscribe(self.vnf_configure, t.VNF_CONFIGURE)

    def populate_infrastructure_database(self):
        """
        Get a view of the available infrastructure and store it
        """

        # datacenters
        url = t.EMU_BASE + 'datacenter'
        req = requests.get(url, timeout=5.0)

        LOG.info(req.text)
        LOG.info(req.status_code)

        data = json.loads(req.text)

        for dc in data:
            vim_uuid = str(uuid.uuid4())
            vim_name = dc['internalname']
            self.infra[vim_uuid] = vim_name

        return

    def register_wrapper_in_ia_registry(self):
        """
        Register the wrapper in the IA registry, so it can be used
        """

        # Register the dcs
        for dc_uuid in self.infra.keys():
            payload = {}
            payload['uuid'] = dc_uuid
            payload['name'] = self.infra[dc_uuid]
            payload['country'] = 'foo'
            payload['city'] = 'bar'
            payload['endpoint'] = t.EMU_BASE

            req = requests.post(t.post_vims, json=payload, timeout=10.0)

            LOG.info(req.text)
            LOG.info(req.status_code)

        # Register the wim
        payload = {}
        payload['uuid'] = self.wim
        payload['name'] = 'vim_emu'
        payload['endpoint'] = t.EMU_BASE
        payload["vim_list"] = list(self.infra.keys())

        req = requests.post(t.post_wims, json=payload, timeout=10.0)

        LOG.info(req.text)
        LOG.info(req.status_code)

        return

    def vnf_configure(self, ch, mthd, prop, msg):
        """
        Handle a request to load env variables into running containers
        """

        # TODO: handle this, currently ignored
        LOG.info(msg)

        # Don't trigger on self created messages
        if self.name == prop.app_id:
            return

        response = {}
        response['request_status'] = 'COMPLETED'
        response['message'] = ""

        self.manoconn.notify(prop.reply_to,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        return

    def comp_resources(self, ch, mthd, prop, msg):
        """
        This method provides the available computing resources
        """

        # Don't trigger on self created messages
        if self.name == prop.app_id:
            return

        vim_list = []

        for vim_uuid in self.infra.keys():
            vim_data = {}
            vim_data['type'] = 'container'
            vim_data['core_used'] = 0
            vim_data['core_total'] = 100
            vim_data['memory_used'] = 0
            vim_data['memory_total'] = 100000
            vim_data['vim_city'] = 'Ghent'
            vim_data['vim_domain'] = 'null'
            vim_data['vim_endpoint'] = 'null'
            vim_data['vim_name'] = self.infra[vim_uuid]
            vim_data['vim_uuid'] = vim_uuid

            vim_list.append(vim_data)

        if t.wrapper_part_of_ia:
            response = {'resources': vim_list}
        else:
            response = {'vim_list': vim_list}


        LOG.info(yaml.dump(response))

        self.manoconn.notify(prop.reply_to,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        return

    def net_resources(self, ch, mthd, prop, msg):
        """
        This method provides the available networking resources
        """

        # Don't trigger on self created messages
        if self.name == prop.app_id:
            return

        wim = {}
        wim['uuid'] = self.wim
        wim['name'] = 'emu_wim'

        qos = []

        dc_uuids = list(self.infra.keys())
        for dc1 in dc_uuids:
            for dc2 in dc_uuids:
                if dc_uuids.index(dc1) < dc_uuids.index(dc2):
                    path_data = {}
                    path_data['node_1'] = dc1
                    path_data['node_2'] = dc2
                    path_data['latency'] = 10
                    path_data['latency_unit'] = "ms"
                    path_data['bandwidth'] = 10000
                    path_data['bandwidth_unit'] = "Mbps"

                    qos.append(path_data)

        wim['qos'] = qos

        response = [wim]

        LOG.info(yaml.dump(response))

        self.manoconn.notify(prop.reply_to,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        return

    def create_network(self, ch, mthd, prop, msg):
        """
        This method parses and stores network information for later use
        """

        # Don't trigger on self created messages
        if self.name == prop.app_id:
            return

        payload = yaml.load(msg)

        serv_id = payload['instance_id']

        # Add the serv_id to the ledger if not present yet
        if serv_id not in self.ledger.keys():
            self.ledger[serv_id] = {}

            self.ledger[serv_id]['networks'] = {}

        networks = self.ledger[serv_id]['networks']

        for vim in payload['vim_list']:
            # Add the vim if new for this service
            if vim['uuid'] not in networks.keys():
                networks[vim['uuid']] = {}

            # Add the vl if new for this vim
            for vl in vim['virtual_links']:
                if vl['id'] not in networks[vim['uuid']].keys():
                    fir_seg = str(self.network_counter % 255)
                    sec_seg = str(int(self.network_counter / 255))
                    tot_seg =  fir_seg + '.' + sec_seg + '.0.'
                    networks[vim['uuid']][vl['id']] = {'segment': tot_seg,
                                                       'count': 1,
                                                       'interfaces': []}
                    self.network_counter += 1

        LOG.info(yaml.dump(self.ledger))

        response = {}
        response['request_status'] = 'COMPLETED'
        response['message'] = ""

        if t.wrapper_part_of_ia:
            payload = json.dumps(response)
        else:
            payload = yaml.dump(response)


        self.manoconn.notify(prop.reply_to,
                             payload,
                             correlation_id=prop.correlation_id)

        return

    def remove_network(self, ch, mthd, prop, msg):
        """
        This method parses and stores network information for later use
        """

        # Don't trigger on self created messages
        if self.name == prop.app_id:
            return

        response = {}
        response['request_status'] = 'COMPLETED'
        response['message'] = ""

        if t.wrapper_part_of_ia:
            payload = json.dumps(response)
        else:
            payload = yaml.dump(response)


        self.manoconn.notify(prop.reply_to,
                             payload,
                             correlation_id=prop.correlation_id)

    def deploy_vnf(self, ch, mthd, prop, msg):
        """
        This method interacts with the emulator to deploy a vnf
        """

        # Don't trigger on self created messages
        if self.name == prop.app_id:
            return

        payload = yaml.load(msg)
        vnfd = payload['vnfd']
        serv_id = payload['service_instance_id']
        func_id = vnfd['instance_uuid']
        vim_id = payload['vim_uuid']
        vim = self.infra[vim_id]
        networks = self.ledger[serv_id]['networks'][vim_id]

        error = None
        cdu_dic = []

        for cdu in vnfd['cloudnative_deployment_units']:

            cdu_name = serv_id[:8] + '_' + func_id[:8] + '_' +  cdu['id'][:-37]

            data = {}
            data['image'] = cdu['image']

            cdu_vnfr = {}
            cdu_vnfr['cdu_reference'] = vnfd['name'] + ':' + cdu['id']
            cdu_vnfr['id'] = cdu['id'][:-37]
            cdu_vnfr['image'] = cdu['image']
            cdu_vnfr['vim_id'] = vim_id
            cdu_vnfr['load_balancer_ip'] = {'floating_ip': '', 'internal_ip': ''}
            cdu_vnfr['connection_points'] = []

            # build message to create required interfaces
            if cdu['connection_points']:
                network_str = ''
                for cp in cdu['connection_points']:
                    # separate interfaces by comma
                    if network_str:
                        network_str = network_str + ','
                    cp_network = 'id=' + str(cp['id']) + ',' + 'ip='
                    net_info = networks[cp['network_id']]
                    cidr = net_info['segment'] + str(net_info['count']) + '/24'
                    cp_network = cp_network + cidr
                    net_info['count'] = net_info['count'] + 1
                    network_str = network_str + '(' + cp_network + ')'

                    cp_vnfr = {}
                    cp_vnfr['id'] = cp['id']
                    cp_vnfr['ip'] = cidr.split('/')[0]
                    cdu_vnfr['connection_points'].append(cp_vnfr)

                data['network'] = network_str

            url_specific = str(vim) + '/' + cdu_name
            url = t.EMU_BASE + 'compute/' + url_specific
            LOG.info(yaml.dump(data))

            while self.emu_busy:
                time.sleep(1)

            self.emu_busy = True

            counter = 0
            while counter < 1:
                req = requests.put(url, json=data)
                LOG.info(req.text)
                LOG.info(req.status_code)

                if str(req.status_code) == "200":
                    break

                counter += 1
                LOG.info('counter at ' + str(counter))

            self.emu_busy = False
            if str(req.status_code) != "200":
                error = 'cdu deployment failed: ' + req.text
                break

            cdu_dic.append(cdu_vnfr)

            # Setup links between interfaces in same networks
            if cdu['connection_points']:
                for cp in cdu['connection_points']:
                    for interface in networks[cp['network_id']]['interfaces']:
                        data = {}
                        data['vnf_src_name'] = cdu_name
                        data['vnf_dst_name'] = interface['cdu_name']
                        data['vnf_src_interface'] = cp['id']
                        data['vnf_dst_interface'] = interface['id']
                        data['bidirectional'] = True

                        url = t.EMU_BASE + 'network'
                        LOG.info(url)

                        while self.emu_busy:
                            time.sleep(1)

                        self.emu_busy = True
                        req = requests.put(url, json=data)
                        self.emu_busy = False

                        req = requests.put(url, json=data)

                        LOG.info(req.text)
                        LOG.info(req.status_code)

                        if str(req.status_code) != '200':
                            error = 'link setup failure: ' + req.text
                            break

                    interface = {'cdu_name': cdu_name, 'id': cp['id']}
                    networks[cp['network_id']]['interfaces'].append(interface)

            LOG.info(yaml.dump(self.ledger))

        # build response message for MANO
        response = {}

        if error:
            response['request_status'] = 'ERROR'
            response['message'] = error

        else:
            response['request_status'] = 'COMPLETED'
            response['vimUuid'] = vim_id
            response['service_instance_id'] = serv_id
            response['ip_mapping'] = []
            response['message'] = ''
            response['instanceName'] = vnfd['name']
            response['vnfr'] = {}
            response['vnfr']['status'] = 'normal operation'
            response['vnfr']['descriptor_reference'] = vnfd['uuid']
            response['vnfr']['id'] = func_id
            response['vnfr']['descriptor_version'] = 'vnfr-schema-01'
            response['vnfr']['name'] = vnfd['name']
            response['vnfr']['cloudnative_deployment_units'] = cdu_dic

        LOG.info(yaml.dump(response))
        self.manoconn.notify(prop.reply_to,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        return

    def remove_vnf(self, ch, mthd, prop, msg):
        """
        This method interacts with the emulator to deploy a vnf
        """

        # Don't trigger on self created messages
        if self.name == prop.app_id:
            return

        payload = yaml.load(msg)
        serv_id = payload['service_instance_id']
        func_id = payload['vnf_uuid']

        networks = self.ledger[serv_id]['networks']

        # Get all compute nodes
        url = t.EMU_BASE + 'compute'
        req = requests.get(url, timeout=30)

        nodes = json.loads(req.text)

        LOG.info(req.text)

        for node in nodes:
            name = node[0]
            dc = node[1]['datacenter']

            # if the vnf belongs to the vnf uuid, delete it
            if func_id[:8] in name:
                del_url = url + '/' + dc + '/' + name
                req = requests.delete(del_url, timeout=15.0)

                LOG.info(req.text)

                # remove interfaces associated to this vnf
                for vim_id in networks.keys():
                    networks_per_vim = networks[vim_id]
                    for network_id in networks_per_vim.keys():
                        interfaces = networks_per_vim[network_id]['interfaces']
                        fin_interface = None
                        for interface in interfaces:
                            if interface['cdu_name'] == name:
                                fin_interface = interface
                                break
                        if fin_interface:
                            interfaces.remove(fin_interface)

        LOG.info(yaml.dump(self.ledger))

        response = {}
        response['request_status'] = 'COMPLETED'
        response['message'] = ""

        self.manoconn.notify(prop.reply_to,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        return

    def add_wan(self, ch, mthd, prop, msg):
        """
        Add a link for each wan request
        """

        # Don't trigger on self created messages
        if self.name == prop.app_id:
            return

        payload = yaml.load(msg)

        src_ip = payload['ingress']['nap']
        dst_ip = payload['egress']['nap']

        # Get all nodes
        url = t.EMU_BASE + 'compute'
        req = requests.get(url, timeout=5.0)

        nodes = json.loads(req.text)

        LOG.info(req.text)

        data = {}
        data['bidirectional'] = True

        for node in nodes:
            name = node[0]
            netw = node[1]['network']

            for interface in netw:
                if interface['ip'] == src_ip:
                    data['vnf_src_name'] = name
                    data['vnf_src_interface'] = interface['intf_name']
                    break
                if interface['ip'] == dst_ip:
                    data['vnf_dst_name'] = name
                    data['vnf_dst_interface'] = interface['intf_name']
                    break

        LOG.info(yaml.dump(data))
        url = t.EMU_BASE + 'network'
        LOG.info(url)
        req = requests.put(url, json=data)

        LOG.info(req.text)

        response = {}
        response['request_status'] = 'COMPLETED'
        response['message'] = ""

        self.manoconn.notify(prop.reply_to,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        return

    def remove_wan(self, ch, mthd, prop, msg):
        """
        Remove a link for each wan removal request
        """

        # Don't trigger on self created messages
        if self.name == prop.app_id:
            return

        # Nothing is done here. Removing a wan preceeds a vnf remove
        # request, which will take care of the attached links.
        response = {}
        response['request_status'] = 'COMPLETED'
        response['message'] = ""

        self.manoconn.notify(prop.reply_to,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        return


    def remove_service(self, ch, mthd, prop, msg):
        """
        Removes all artefacts related to a service
        """

        # Don't trigger on self created messages
        if self.name == prop.app_id:
            return

        payload = yaml.load(msg)
        serv_id = payload['instance_uuid']

        # Get all compute nodes
        url = t.EMU_BASE + 'compute'
        req = requests.get(url, timeout=5.0)

        nodes = json.loads(req.text)

        LOG.info(req.text)

        for node in nodes:
            name = node[0]
            dc = node[1]['datacenter']

            # if the vnf belongs to the service, delete it
            if serv_id.startswith(name[:8]):
                del_url = url + '/' + dc + '/' + name
                req = requests.delete(del_url, timeout=15.0)

                LOG.info(req.text)


        # Try to delete the entry from the ledger. Might already be deleted
        # if mulitple remove_service requests are received
        try:
            del self.ledger[serv_id]
        except:
            pass

        response = {}
        response['request_status'] = 'COMPLETED'
        response['message'] = ""

        self.manoconn.notify(prop.reply_to,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        return

def main():
    """
    Entry point to start the wrapper.
    """

    # reduce messaging log level to have a nicer output for this plugin
#    TangoLogger.getLogger("son-mano-base:messaging", logging.INFO, log_json=True)
#    TangoLogger.getLogger("son-mano-base:plugin", logging.INFO, log_json=True)

    emu_wrapper = EmulatorWrapper()

if __name__ == '__main__':
    main()