import business_rules
from business_rules import run_all, export_rule_data
from business_rules.variables import *
from business_rules.actions import *
from business_rules.fields import *
from tngsdk.validation.util import read_descriptor_file
from tngsdk.validation import event
from tngsdk.validation.storage import DescriptorStorage

import datetime
import json
import os
import sys
import yaml
import logging

log = logging.getLogger(__name__)
evtlog = event.get_logger('validator.events')

class DescriptorVDU(object):

    def __init__(self, vnfd_id):
        self._vnfd_id = vnfd_id
        self._vdu_id = ""
        self._errors = []
        self._storage = {}
        self._cpu = {}
        self._memory = {}
        self._network = {}
        self._vm_images_format = ""
    def display_error(self, error_text):
        log.error("Custom error in descriptor '{}' in vdu_id = '{}'\n{}"
                 .format(self._vnfd_id, self._vdu_id, error_text))

    def display_warning(self, warning_text):
        log.warning("Warning detected in custom rules validation: {}"
                 .format(warning_text))


class DescriptorVariablesVDU(BaseVariables):

    def __init__(self, descriptor):
        self._vnfd_id = descriptor._vnfd_id
        self._vdu_id = descriptor._vdu_id
        self._storage = descriptor._storage
        self._cpu = descriptor._cpu
        self._memory = descriptor._memory
        self._network = descriptor._network
        self._vm_images_format = descriptor._vdu_images_format
    # virtual_deployment_units/resource_requirements/memory
    @numeric_rule_variable(label='Size of RAM')
    def vdu_resource_requirements_ram_size(self):
        size = self._memory.get("size")
        if size:
            return size
        else:
            return -1
    @string_rule_variable(label='Unit of RAM')
    def vdu_resource_requirements_ram_size_unit(self):
        size_unit = self._memory.get("size_unit")
        if size_unit:
            return size_unit
        else:
            log.error("Custom error in descriptor '{}' in vdu_id = '{}'\n{}"
                     .format(self._vnfd_id, self._vdu_id, "'size_unit' is not present in 'memory'"))
            return ""

    # virtual_deployment_units/resource_requirements/cpu
    @numeric_rule_variable(label='Number of vCPUs')
    def vdu_resource_requirements_cpu_vcpus(self):
        vcpus = self._cpu.get("vcpus")
        if vcpus:
            return vcpus
        else:
            return -1

    # virtual_deployment_units/resource_requirements/storage
    @numeric_rule_variable(label='Size of storage')
    def vdu_resource_requirements_storage_size(self):
        size = self._storage.get("size")
        if size:
            return size
        else:
            return -1

    @string_rule_variable(label='Unit of storage')
    def vdu_resource_requirements_storage_size_unit(self):
        size_unit = self._storage.get("size_unit")
        if size_unit:
            return size_unit
        else:
            log.error("Custom error in descriptor '{}' in vdu_id = '{}'\n{}"
                     .format(self._vnfd_id, self._vdu_id, "'size_unit' is not present in 'storage'"))
            return ""

    # virtual_deployment_units/network
    @numeric_rule_variable(label='size of BW')
    def vdu_resource_requirements_network_network_interface_bandwidth(self):
        if self._network:
            size = self._network.get("network_interface_bandwidth")
            if size:
                return size
            else:
                return -1
        else:
            return -1
    @string_rule_variable(label='Unit of BW')
    def vdu_resource_requirements_network_network_interface_bandwidth_unit(self):
        if self._network:
            size_unit = self._network.get("network_interface_bandwidth_unit")
            if size_unit:
                return size_unit
            else:
                log.error("Custom error in descriptor '{}' in vdu_id = '{}'\n{}"
                         .format(self._vnfd_id, self._vdu_id, "'network_interface_bandwidth_unit' is not present in 'network'"))
                return ""
        else:
            log.error("Custom error in descriptor '{}' in vdu_id = '{}'\n{}"
                     .format(self._vnfd_id, self._vdu_id, "'network' is not present in 'resource_requirements'"))
            return ""
    @boolean_rule_variable(label='SR-IOV')
    def vdu_resource_requirements_network_network_interface_card_capabilities_SRIOV(self):
        return False
    @boolean_rule_variable(label='Mirroring')
    def vdu_resource_requirements_network_network_interface_card_capabilities_mirroring(self):
        return False
    @string_rule_variable(label='Format of VM')
    def vdu_vm_resource_format(self):
        return self._vm_images_format

class DescriptorActions(BaseActions):

    def __init__(self, descriptor):
        self.descriptor = descriptor

    @rule_action(params={"error_text": FIELD_TEXT})
    def raise_error(self, error_text):
        self.descriptor._errors.append(error_text)
        self.descriptor.display_error(error_text)

    @rule_action(params={"error_text": FIELD_TEXT})
    def raise_warning(self, error_text):
        self.descriptor.display_warning(error_text)


def process_rules(custom_rule_file, descriptor_file_name):
    rules = load_rules_yaml(custom_rule_file)
    storage = DescriptorStorage()

    func = storage.create_function(descriptor_file_name)
    if not func:
        evtlog.log("Invalid function descriptor, Couldn't store "
                   "VNF of file '{0}'".format(descriptor_file_name),
                   descriptor_file_name,
                   'evt_function_invalid_descriptor')
        exit(1)

    for vdu in func.content.get("virtual_deployment_units"):
        descriptor = DescriptorVDU(func.id)
        descriptor._vdu_id = vdu.get("id")
        descriptor._storage = vdu.get("resource_requirements").get("storage")
        descriptor._cpu = vdu.get("resource_requirements").get("cpu")
        descriptor._memory = vdu.get("resource_requirements").get("memory")
        descriptor._network = vdu.get("resource_requirements").get("network")
        descriptor._vdu_images_format = vdu.get("vm_image_format")
        triggered = run_all(rule_list=rules,
                            defined_variables=DescriptorVariablesVDU(descriptor),
                            defined_actions=DescriptorActions(descriptor),
                            stop_on_first_trigger=False)
    return descriptor._errors

def load_rules_yaml(custom_rule_file):
        if not os.path.isfile(custom_rule_file):
            log.error("Invalid custom rule file")
            exit(1)

        try:
            with open(custom_rule_file, "r") as fn_custom_rule:
                rules = yaml.load(fn_custom_rule, Loader=yaml.SafeLoader)
        except IOError:
            log.error("Error opening custom rule file: "
                      "File does not appear to exist.")
            exit(1)
        except (yaml.YAMLError, yaml.MarkedYAMLError) as e:
            log.error("The rule file seems to have contain invalid YAML syntax."
                      " Please fix and try again. Error: {}".format(str(e)))
            exit(1)
        return rules

if __name__ == "__main__":
    if len(sys.argv) != 3:
        # if len(sys.argv)!= 2:
        log.error("This script takes exactly two arguments: "
                  "example_descriptor <custom rule file> <descriptor file>")
        exit(1)

    custom_rule_file = sys.argv[1]
    descriptor_file_name = sys.argv[2]

    if not os.path.isfile(custom_rule_file):
        log.error("Invalid custom rule file")
        exit(1)

    if not os.path.isfile(descriptor_file_name):
        print("Invalid descriptor file")
        exit(1)

    process_rules(custom_rule_file, descriptor_file_name)
