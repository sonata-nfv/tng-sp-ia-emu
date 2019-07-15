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

# With infrastructure adaptor

import os

wrapper_part_of_ia = False

prefix = ''
if os.environ.get("topic_prefix"):
	prefix = os.environ.get("topic_prefix") + '.'

path_to_nbi = ''
reply_prefix = ''
if os.environ.get("path_to_nbi"):
	reply_prefix = 'nbi.'
	wrapper_part_of_ia = True
	path_to_nbi = os.environ.get("path_to_nbi")
	post_vims = path_to_nbi.strip('/') + '/vims/emu'
	post_wims = path_to_nbi.strip('/') + '/wims/emu'

EMU_BASE = 'http://127.0.0.1:5001/restapi/'
if os.environ.get("emulator_path"):
	EMU_BASE = os.environ.get("emulator_path")

VNF_DEPLOY = 'infrastructure.' + prefix + 'function.deploy'
VNF_REMOVE = 'infrastructure.' + prefix + 'function.remove'
NETWORK_CREATE = 'infrastructure.' + prefix + 'service.network.create'
NETWORK_REMOVE = 'infrastructure.' + prefix + 'service.network.delete'
SERVICE_REMOVE = 'infrastructure.' + prefix + 'service.remove'
WAN_ADD = 'infrastructure.' + prefix + 'wan.configure'
WAN_REMOVE = 'infrastructure.' + prefix + 'wan.deconfigure'
COMP_RESOURCES = 'infrastructure.' + prefix + 'management.compute.list' 
NET_RESOURCES = 'infrastructure.' + prefix + 'management.wan.list'
VNF_CONFIGURE = 'infrastructure.' + prefix + 'function.configure'

