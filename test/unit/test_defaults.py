#!/usr/bin/env python3
# Copyright 2021-2022 NetCracker Technology Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest

from kubemarine.core import defaults
from kubemarine import demo


class DefaultsEnrichmentAppendControlPlain(unittest.TestCase):

    def test_controlplain_already_defined(self):
        inventory = demo.generate_inventory(**demo.MINIHA_KEEPALIVED)
        inventory['control_plain'] = {
            'internal': '1.1.1.1',
            'external': '2.2.2.2'
        }
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], '1.1.1.1')
        self.assertEqual(inventory['control_plain']['external'], '2.2.2.2')

    def test_controlplain_already_internal_defined(self):
        inventory = demo.generate_inventory(**demo.MINIHA_KEEPALIVED)
        inventory['control_plain'] = {
            'internal': '1.1.1.1'
        }
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], '1.1.1.1')
        self.assertEqual(inventory['control_plain']['external'], inventory['nodes'][0]['address'])

    def test_controlplain_already_external_defined(self):
        inventory = demo.generate_inventory(**demo.MINIHA_KEEPALIVED)
        inventory['control_plain'] = {
            'external': '2.2.2.2'
        }
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], inventory['vrrp_ips'][0])
        self.assertEqual(inventory['control_plain']['external'], '2.2.2.2')

    def test_controlplain_calculated_half_vrrp_half_master(self):
        inventory = demo.generate_inventory(**demo.MINIHA_KEEPALIVED)
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], inventory['vrrp_ips'][0])
        self.assertEqual(inventory['control_plain']['external'], inventory['nodes'][0]['address'])

    def test_controlplain_calculated_fully_vrrp(self):
        inventory = demo.generate_inventory(**demo.MINIHA_KEEPALIVED)
        inventory['vrrp_ips'][0] = {
            'ip': '192.168.0.1',
            'floating_ip': inventory['vrrp_ips'][0]
        }
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], inventory['vrrp_ips'][0]['ip'])
        self.assertEqual(inventory['control_plain']['external'], inventory['vrrp_ips'][0]['floating_ip'])

    def test_controlplain_calculated_half_fully_master(self):
        inventory = demo.generate_inventory(**demo.MINIHA)
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], inventory['nodes'][0]['internal_address'])
        self.assertEqual(inventory['control_plain']['external'], inventory['nodes'][0]['address'])

    def test_controlplain_control_endpoint_vrrp(self):
        inventory = demo.generate_inventory(**demo.MINIHA)
        inventory['vrrp_ips'] = [
            {
                'ip': '192.168.0.1',
                'floating_ip': '1.1.1.1'
            },
            {
                'ip': '192.168.0.2',
                'floating_ip': '2.2.2.2',
                'control_endpoint': True
            }
        ]
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], '192.168.0.2')
        self.assertEqual(inventory['control_plain']['external'], '2.2.2.2')

    def test_controlplain_control_half_endpoint_vrrp(self):
        inventory = demo.generate_inventory(**demo.MINIHA)
        inventory['vrrp_ips'] = [
            {
                'ip': '192.168.0.1',
                'floating_ip': '1.1.1.1'
            },
            {
                'ip': '192.168.0.2',
                'control_endpoint': True
            }
        ]
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], '192.168.0.2')
        self.assertEqual(inventory['control_plain']['external'], '1.1.1.1')

    def test_controlplain_control_half_endpoint_vrrp_half_master(self):
        inventory = demo.generate_inventory(**demo.MINIHA)
        inventory['vrrp_ips'] = [
            {
                'ip': '192.168.0.1',
            },
            {
                'ip': '192.168.0.2',
                'control_endpoint': True
            }
        ]
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], '192.168.0.2')
        self.assertEqual(inventory['control_plain']['external'], inventory['nodes'][0]['address'])

    def test_controlplain_control_half_endpoint_vrrp_half_endpoint_master(self):
        inventory = demo.generate_inventory(**demo.MINIHA)
        inventory['vrrp_ips'] = [
            {
                'ip': '192.168.0.1',
            },
            {
                'ip': '192.168.0.2',
                'control_endpoint': True
            }
        ]
        inventory['nodes'][1]['control_endpoint'] = True
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], '192.168.0.2')
        self.assertEqual(inventory['control_plain']['external'], inventory['nodes'][1]['address'])

    def test_controlplain_skip_not_bind(self):
        inventory = demo.generate_inventory(**demo.MINIHA_KEEPALIVED)
        inventory['vrrp_ips'] = [
            {
                'ip': '192.168.2.0',
                'floating_ip': '1.1.1.1',
                'params': {
                    'maintenance-type': 'not bind'
                }
            },
            {
                'ip': '192.168.2.1',
                'floating_ip': '2.2.2.2',
            }
        ]
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], '192.168.2.1')
        self.assertEqual(inventory['control_plain']['external'], '2.2.2.2')

    def test_controlplain_skip_not_bind_half_vrrp_half_master(self):
        inventory = demo.generate_inventory(**demo.MINIHA_KEEPALIVED)
        inventory['vrrp_ips'] = [
            {
                'ip': '192.168.2.0',
                'floating_ip': '1.1.1.1',
                'params': {
                    'maintenance-type': 'not bind'
                }
            },
            {
                'ip': '192.168.2.1',
            }
        ]
        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], '192.168.2.1')
        self.assertEqual(inventory['control_plain']['external'], inventory['nodes'][0]['address'])

    def test_controlplain_skip_vrrp_ips_no_balancers(self):
        inventory = demo.generate_inventory(master=3, worker=3, balancer=0, keepalived=1)
        first_control_plane = next(node for node in inventory['nodes'] if 'master' in node['roles'])

        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], first_control_plane['internal_address'])
        self.assertEqual(inventory['control_plain']['external'], first_control_plane['address'])

    def test_controlplain_skip_vrrp_ips_assigned_not_balancer(self):
        inventory = demo.generate_inventory(master=3, worker=3, balancer=1, keepalived=1)
        first_control_plane = next(node for node in inventory['nodes'] if 'master' in node['roles'])
        balancer = next(node for node in inventory['nodes'] if 'balancer' in node['roles'])
        inventory['vrrp_ips'][0] = {
            'ip': inventory['vrrp_ips'][0],
            'hosts': [first_control_plane['name']]
        }

        inventory = defaults.append_controlplain(inventory, None)
        self.assertEqual(inventory['control_plain']['internal'], balancer['internal_address'])
        self.assertEqual(inventory['control_plain']['external'], balancer['address'])

    def test_controlplain_skip_vrrp_ips_and_balancer_removed_only_balancer(self):
        inventory = demo.generate_inventory(master=3, worker=3, balancer=1, keepalived=1)
        first_control_plane = next(node for node in inventory['nodes'] if 'master' in node['roles'])
        balancer = next(node for node in inventory['nodes'] if 'balancer' in node['roles'])

        context = demo.create_silent_context(['fake.yaml'], procedure='remove_node')
        remove_node = demo.generate_procedure_inventory('remove_node')
        remove_node['nodes'] = [balancer]

        cluster = demo.new_cluster(inventory, procedure_inventory=remove_node, context=context)
        inventory = cluster.inventory

        self.assertEqual(inventory['control_plain']['internal'], first_control_plane['internal_address'])
        self.assertEqual(inventory['control_plain']['external'], first_control_plane['address'])

    def test_controlplain_skip_vrrp_ips_assigned_to_removed_balancer(self):
        inventory = demo.generate_inventory(master=3, worker=3, balancer=2, keepalived=2)
        first_balancer = next(node for node in inventory['nodes'] if 'balancer' in node['roles'])
        inventory['vrrp_ips'][0] = {
            'ip': inventory['vrrp_ips'][0],
            'hosts': [first_balancer['name']],
            'floating_ip': '1.1.1.1'
        }
        inventory['vrrp_ips'][1] = {
            'ip': inventory['vrrp_ips'][1],
            'floating_ip': '2.2.2.2'
        }

        context = demo.create_silent_context(['fake.yaml'], procedure='remove_node')
        remove_node = demo.generate_procedure_inventory('remove_node')
        remove_node['nodes'] = [first_balancer]

        cluster = demo.new_cluster(inventory, procedure_inventory=remove_node, context=context)
        inventory = cluster.inventory

        self.assertEqual(inventory['control_plain']['internal'], inventory['vrrp_ips'][1]['ip'])
        self.assertEqual(inventory['control_plain']['external'], inventory['vrrp_ips'][1]['floating_ip'])


class PrimitiveValuesAsString(unittest.TestCase):
    def test_default_enrichment(self):
        inventory = demo.generate_inventory(**demo.ALLINONE)
        inventory['services'].setdefault('cri', {})['containerRuntime'] = 'containerd'
        context = demo.create_silent_context()
        context['nodes'] = demo.generate_nodes_context(inventory, os_name='ubuntu', os_version='22.04')
        inventory = demo.new_cluster(inventory, context=context).inventory

        self.assertEqual(True, inventory['services']['cri']['containerdConfig']
                         ['plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options']['SystemdCgroup'])
        self.assertEqual(['br_netfilter', 'nf_conntrack'],
                         inventory['services']['modprobe']['debian'])
        self.assertEqual({'net.bridge.bridge-nf-call-iptables', 'net.ipv4.ip_forward', 'net.ipv4.ip_nonlocal_bind',
                          'net.ipv4.conf.all.route_localnet', 'net.netfilter.nf_conntrack_max',
                          'kernel.panic', 'vm.overcommit_memory', 'kernel.panic_on_oops'},
                         set(inventory['services']['sysctl'].keys()))
        typha = inventory['plugins']['calico']['typha']
        self.assertEqual(False, typha['enabled'])
        self.assertEqual(2, typha['replicas'])

    def test_custom_jinja_enrichment(self):
        inventory = demo.generate_inventory(**demo.ALLINONE)
        inventory['services'].setdefault('modprobe', {})['debian'] = [
            """
            {% if true %}
            custom_module
            {% endif %}
            """,
            {'<<': 'merge'}
        ]
        inventory['services'].setdefault('sysctl', {})['custom_parameter'] = \
            """
            {% if true %}
            1
            {% endif %}
            """
        inventory.setdefault('plugins', {}).setdefault('kubernetes-dashboard', {})['install'] = "{{ true }}"
        context = demo.create_silent_context()
        context['nodes'] = demo.generate_nodes_context(inventory, os_name='ubuntu', os_version='22.04')
        inventory = demo.new_cluster(inventory, context=context).inventory

        self.assertEqual('custom_module', inventory['services']['modprobe']['debian'][0])
        self.assertEqual(1, inventory['services']['sysctl']['custom_parameter'])
        self.assertEqual(True, inventory['plugins']['kubernetes-dashboard']['install'])


if __name__ == '__main__':
    unittest.main()
