import asyncio
import os
import base64
import jinja2
from datetime import datetime
import time

from msgraph_beta.generated.models.o_data_errors.o_data_error import ODataError

from msgraph_beta.generated.models.windows10_custom_configuration import Windows10CustomConfiguration
from msgraph_beta.generated.models.oma_setting_string_xml import OmaSettingStringXml
from msgraph_beta.generated.models.oma_setting_integer import OmaSettingInteger
from msgraph_beta.generated.models.oma_setting_string import OmaSettingString

from msgraph_beta.generated.models.device_management_configuration_group_setting_collection_instance import DeviceManagementConfigurationGroupSettingCollectionInstance
from msgraph_beta.generated.models.device_management_configuration_group_setting_value import DeviceManagementConfigurationGroupSettingValue
from msgraph_beta.generated.models.device_management_configuration_simple_setting_instance import DeviceManagementConfigurationSimpleSettingInstance
from msgraph_beta.generated.models.device_management_configuration_string_setting_value import DeviceManagementConfigurationStringSettingValue
from msgraph_beta.generated.models.device_management_configuration_choice_setting_instance import DeviceManagementConfigurationChoiceSettingInstance
from msgraph_beta.generated.models.device_management_configuration_choice_setting_value import DeviceManagementConfigurationChoiceSettingValue
from msgraph_beta.generated.models.device_management_configuration_reference_setting_value import DeviceManagementConfigurationReferenceSettingValue
from msgraph_beta.generated.models.device_management_configuration_choice_setting_collection_instance import DeviceManagementConfigurationChoiceSettingCollectionInstance
from msgraph_beta.generated.models.device_management_configuration_setting_instance_template_reference import DeviceManagementConfigurationSettingInstanceTemplateReference
from msgraph_beta.generated.models.device_management_configuration_simple_setting_instance import DeviceManagementConfigurationSimpleSettingInstance
from msgraph_beta.generated.models.device_management_configuration_setting_instance import DeviceManagementConfigurationSettingInstance

from mdedevicecontrol.dcgraph import Graph
from mdedevicecontrol import Setting

import plistlib
import argparse
import json
import pathlib
import urllib.parse
import hashlib

from lxml import etree as ET

import mdedevicecontrol as dc
from mdedevicecontrol.dcdoc import Inventory, Description

import logging
logger = logging.getLogger(__name__)

def full_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

class DeviceControlPolicyTemplate:

    class Util:

        def get_values_from_group_setting_collection_instance_as_list(group_setting_collection_instance):
            return_list = []
            for group_setting in group_setting_collection_instance.group_setting_collection_value:
                if group_setting.odata_type == "#microsoft.graph.deviceManagementConfigurationGroupSettingValue":
                    for child in group_setting.children:
                        return_list.append(child.simple_setting_value.value)


            return return_list


    class DeviceControlGroup:

        GROUP_DATA_ID_SETTING_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_id'
        GROUP_DATA_PRINTER_DEVICES_ID_LIST_SETTINGD_ID  = 'device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_printerdevicesidlist'
        GROUP_DATA_MATCH_TYPE_SETTING_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_matchtype'
        GROUP_DATA_DESCRIPTOR_LIST_SETTING_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist'
        GROUP_DATA_DESCRIPTOR_LIST_NAME_SETTING_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist_name'

        GROUP_DATA_MATCH_ANY_SETTING_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_matchtype_matchany'
        GROUP_DATA_MATCH_ALL_SETTING_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_matchtype_matchall'

        group_settings = {}

        def __init__(self):
            self.id = ""

            self.metadata_id = ""

            self.name = ""
            self.description = ""
            self.type = "Device"
            self.match_type = ""
            self.descriptors = []


        def toJSON(self):

            group_json = {
                "id": self.id,
                "name": self.name,
                "descriptors":{}
            }
            match self.match_type:
                case DeviceControlPolicyTemplate.DeviceControlGroup.GROUP_DATA_MATCH_ANY_SETTING_ID:
                    group_json["match_type"] = "MatchAny"
                case DeviceControlPolicyTemplate.DeviceControlGroup.GROUP_DATA_MATCH_ALL_SETTING_ID:
                    group_json["match_type"] = "MatchAll"
                case _:
                    logger.warn("Unknown MatchType "+self.match_type)
        
            for descriptor in self.descriptors:
                comment = None
                tag_name = None
                tag_text = None
                

                logger.debug("descriptor="+str(descriptor))

                for key in descriptor:
                    logger.debug("key="+key)
                    match key:
                        case DeviceControlPolicyTemplate.DeviceControlGroup.GROUP_DATA_DESCRIPTOR_LIST_NAME_SETTING_ID:
                            comment = descriptor[key]
                        case _:
                            setting_details = DeviceControlPolicyTemplate.DeviceControlGroup.group_settings[key]
                            descriptor_id = setting_details.display_name
                            descriptor_value = descriptor[key]

                
                group_json["descriptors"][comment] = {
                    descriptor_id: descriptor_value
                }

                    

            return group_json



        def __str__(self):

            '''
            	<Group Id="{33e06f08-8787-4219-9dca-5872854f9d79}" Type="Device">
		            <!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B33e06f08-8787-4219-9dca-5872854f9d79%7D/GroupData -->
		            <Name>bitlocker encrypted USBs</Name>
		            <MatchType>MatchAll</MatchType>
		            <DescriptorIdList>
			            <PrimaryId>RemovableMediaDevices</PrimaryId>
			            <DeviceEncryptionStateId>BitlockerEncrypted</DeviceEncryptionStateId>
		            </DescriptorIdList>
	            </Group>
            '''

            group = ET.Element("Group", Id=self.id)
            
            oma_uri_comment = ET.Comment("./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/"+urllib.parse.quote(self.id)+"/GroupData")
            group.append(oma_uri_comment)

            name = ET.SubElement(group,"Name",{})
            name.text = self.name

            match_type = ET.SubElement(group,"MatchType")
            match self.match_type:
                case DeviceControlPolicyTemplate.DeviceControlGroup.GROUP_DATA_MATCH_ANY_SETTING_ID:
                    match_type.text = "MatchAny"
                case DeviceControlPolicyTemplate.DeviceControlGroup.GROUP_DATA_MATCH_ALL_SETTING_ID:
                    match_type.text = "MatchAll"
                case _:
                    logger.warn("Unknown MatchType "+self.match_type)
        
            descriptorId_list = ET.SubElement(group,"DescriptorIdList")
            for descriptor in self.descriptors:
                comment = None
                tag_name = None
                tag_text = None
                for key in descriptor:
                    match key:
                        case DeviceControlPolicyTemplate.DeviceControlGroup.GROUP_DATA_DESCRIPTOR_LIST_NAME_SETTING_ID:
                            comment = descriptor[key]
                        case _:
                            setting_details = DeviceControlPolicyTemplate.DeviceControlGroup.group_settings[key]
                            tag_name = setting_details.display_name
                            tag_text = descriptor[key]

                if comment is not None:
                    descriptorId_list.append(ET.Comment(comment))

                if tag_name is not None:
                    tag = ET.SubElement(descriptorId_list,tag_name)
                    tag.text = tag_text


            
            ET.indent(group, space="\t", level=0)
            return ET.tostring(group,method="xml").decode("utf-8")


        def createSettingFromJSON(group_json):

            logger.debug(str(group_json))
            groupdata = DeviceManagementConfigurationGroupSettingCollectionInstance()
            groupdata.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata"
            groupdata.group_setting_collection_value = []

            groupdata_group_setting_value = DeviceManagementConfigurationGroupSettingValue()
            groupdata.group_setting_collection_value.append(groupdata_group_setting_value)

            groupdata_group_setting_value.children = []

            #group id"settingDefinitionId": "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata"
            #groupdata_id_setting = DeviceManagementConfigurationSimpleSettingInstance()
            #groupdata_id_setting.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_id"

            #groupdata_id_value = DeviceManagementConfigurationStringSettingValue()
            #groupdata_id_value.value = group_json["id"]

            #groupdata_id_setting.simple_setting_value = groupdata_id_value
            #groupdata_group_setting_value.children.append(groupdata_id_setting)

            '''
            For each element in the list 
                    {
                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationGroupSettingCollectionInstance",
                        "groupSettingCollectionValue": [
                            {
                                "children": [
                                    {
                                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                                        "settingDefinitionId": "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist_name",
                                        "simpleSettingValue": {
                                            "@odata.type": "#microsoft.graph.deviceManagementConfigurationStringSettingValue",
                                            "value": "Serial Number 1"
                                        }
                                    },
                                    {
                                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                                        "settingDefinitionId": "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist_serialnumberid",
                                        "simpleSettingValue": {
                                            "@odata.type": "#microsoft.graph.deviceManagementConfigurationStringSettingValue",
                                            "value": "11111111"
                                        }
                                    }
                                ]
                            }
                        ],
                        "settingDefinitionId": "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist"
                    }
            '''
            

            
            for descriptor in group_json["descriptors"].keys():

                descriptorIdList = DeviceManagementConfigurationGroupSettingCollectionInstance()
                descriptorIdList.setting_definition_id = 'device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist'
                descriptor_id_value = DeviceManagementConfigurationGroupSettingValue()
                descriptorIdList.group_setting_collection_value = [descriptor_id_value]
                descriptor_id_value.children = []
           
                logger.debug("descriptor="+descriptor)

                #One item for the name
                name = DeviceManagementConfigurationSimpleSettingInstance()
                name.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist_name"
                name.simple_setting_value = DeviceManagementConfigurationStringSettingValue()
                name.simple_setting_value.value = descriptor
                descriptor_id_value.children.append(name)

                descriptor_ids = group_json["descriptors"][descriptor]

                logger.debug("descriptor_ids="+str(descriptor_ids))

                for descriptor_id_name in descriptor_ids:

                    #One item for the value
                    value = DeviceManagementConfigurationSimpleSettingInstance()
                    value.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist_"+str(descriptor_id_name).lower()
                    value.simple_setting_value = DeviceManagementConfigurationStringSettingValue()
                    value.simple_setting_value.value = descriptor_ids[descriptor_id_name]
                    descriptor_id_value.children.append(value)

                groupdata_group_setting_value.children.append(descriptorIdList)

            
            #match type
            match_type_setting = DeviceManagementConfigurationChoiceSettingInstance()
            match_type_setting.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_matchtype"
            match_type_setting.choice_setting_value = DeviceManagementConfigurationChoiceSettingValue()
            match_type_setting.choice_setting_value.value = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_matchtype_matchany"

            groupdata_group_setting_value.children.append(match_type_setting)

            return groupdata


        def createSettingFromGroup(group):

            groupdata = DeviceManagementConfigurationGroupSettingCollectionInstance()
            groupdata.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata"
            groupdata.group_setting_collection_value = []

            groupdata_group_setting_value = DeviceManagementConfigurationGroupSettingValue()
            groupdata.group_setting_collection_value.append(groupdata_group_setting_value)

            groupdata_group_setting_value.children = []

            #group id"settingDefinitionId": "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata"
            groupdata_id_setting = DeviceManagementConfigurationSimpleSettingInstance()
            groupdata_id_setting.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_id"

            groupdata_id_value = DeviceManagementConfigurationStringSettingValue()
            groupdata_id_value.value = group.id

            groupdata_id_setting.simple_setting_value = groupdata_id_value
            groupdata_group_setting_value.children.append(groupdata_id_setting)

            for property in group._properties:

                descriptorId = DeviceManagementConfigurationGroupSettingCollectionInstance()
                descriptorId.setting_definition_id = 'device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist'
                descriptor_id_value = DeviceManagementConfigurationGroupSettingValue()
                descriptorId.group_setting_collection_value = [descriptor_id_value]
                descriptor_id_value.children = []

                #One item for the name
                name = DeviceManagementConfigurationSimpleSettingInstance()
                name.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist_name"
                name.simple_setting_value = DeviceManagementConfigurationStringSettingValue()
                
                if property.dcv2_name is not None:
                    name.simple_setting_value.value = property.dcv2_name
                else:
                    name.simple_setting_value.value = property.name+"("+property.value+")"
                descriptor_id_value.children.append(name)

                #One item for the value
                value = DeviceManagementConfigurationSimpleSettingInstance()
                value.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist_"+str(property.name).lower()
                value.simple_setting_value = DeviceManagementConfigurationStringSettingValue()
                value.simple_setting_value.value = property.value
                descriptor_id_value.children.append(value)

                groupdata_group_setting_value.children.append(descriptorId)

            '''
            For each element in the list 
                    {
                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationGroupSettingCollectionInstance",
                        "groupSettingCollectionValue": [
                            {
                                "children": [
                                    {
                                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                                        "settingDefinitionId": "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist_name",
                                        "simpleSettingValue": {
                                            "@odata.type": "#microsoft.graph.deviceManagementConfigurationStringSettingValue",
                                            "value": "Serial Number 1"
                                        }
                                    },
                                    {
                                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                                        "settingDefinitionId": "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist_serialnumberid",
                                        "simpleSettingValue": {
                                            "@odata.type": "#microsoft.graph.deviceManagementConfigurationStringSettingValue",
                                            "value": "11111111"
                                        }
                                    }
                                ]
                            }
                        ],
                        "settingDefinitionId": "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_descriptoridlist"
                    }
            '''
            #match type
            match_type_setting = DeviceManagementConfigurationChoiceSettingInstance()
            match_type_setting.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_matchtype"
            match_type_setting.choice_setting_value = DeviceManagementConfigurationChoiceSettingValue()
            match_type_setting.choice_setting_value.value = "device_vendor_msft_defender_configuration_devicecontrol_policygroups_{groupid}_groupdata_matchtype_matchany"

            groupdata_group_setting_value.children.append(match_type_setting)

            return groupdata

        def createGroupfromSetting(setting):
            group = DeviceControlPolicyTemplate.DeviceControlGroup()

            group.metadata_id = setting.id
            group.name = setting.display_name
            group.description = setting.description
            setting_instance = setting.setting_instance
            group_setting_collection_value = setting_instance.group_setting_collection_value[0]

            for child in group_setting_collection_value.children:

                match child.setting_definition_id:
                    case DeviceControlPolicyTemplate.DeviceControlGroup.GROUP_DATA_ID_SETTING_ID:
                        group.id = child.simple_setting_value.value
                    case DeviceControlPolicyTemplate.DeviceControlGroup.GROUP_DATA_PRINTER_DEVICES_ID_LIST_SETTINGD_ID:
                        group.type = "Printer"
                        descriptor_ids = {}
                        for group_setting in child.group_setting_collection_value:
                            for group_setting_child in group_setting.children:
                                group_setting_definition_id = group_setting_child.setting_definition_id
                                
                                if group_setting_child.odata_type == "#microsoft.graph.deviceManagementConfigurationChoiceSettingInstance":
                                    group_setting_value = group_setting_child.choice_setting_value.value
                                    group_setting_value_index = int(str(group_setting_value).split("_")[-1])
                                    value = DeviceControlPolicyTemplate.DeviceControlGroup.group_settings[group_setting_child.setting_definition_id]
                                    group_setting_value = value.options[group_setting_value_index].display_name
                                else:    
                                    group_setting_value = group_setting_child.simple_setting_value.value

                                descriptor_ids[group_setting_definition_id] = group_setting_value

                        group.descriptors.append(descriptor_ids)

                    case DeviceControlPolicyTemplate.DeviceControlGroup.GROUP_DATA_MATCH_TYPE_SETTING_ID:
                        group.match_type = child.choice_setting_value.value
                    case DeviceControlPolicyTemplate.DeviceControlGroup.GROUP_DATA_DESCRIPTOR_LIST_SETTING_ID:
                        
                        descriptor_ids = {}
                        for group_setting in child.group_setting_collection_value:
                            for group_setting_child in group_setting.children:
                                group_setting_definition_id = group_setting_child.setting_definition_id
                                group_setting_value = group_setting_child.simple_setting_value.value

                                descriptor_ids[group_setting_definition_id] = group_setting_value

                        group.descriptors.append(descriptor_ids)
                                
                    case _:
                        logger.warn("Unknown child.setting_definition_id"+child.setting_definition_id)



            return group

        

    class DeviceControlRule:


        def createSettingsFromRule(rule,groups_map):


            #rule_setting = DeviceManagementConfigurationGroupSettingCollectionInstance()
            #rule_setting.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata"
            #rule_setting.setting_instance_template_reference = DeviceManagementConfigurationSettingInstanceTemplateReference()
            #rule_setting.setting_instance_template_reference.setting_instance_template_id = "a5c5409c-886a-4909-81c7-28156aee9419"

            #rule_group_setting_collection_value = []
            #rule_setting.group_setting_collection_value = rule_group_setting_collection_value

            #rule_value = DeviceManagementConfigurationGroupSettingValue() 
            #rule_value_children = []
            #rule_value.children = rule_value_children

            #rule_group_setting_collection_value.append(rule_value)

            rule_data = DeviceManagementConfigurationGroupSettingCollectionInstance()
            rule_data.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata"

            #rule_value_children.append(rule_data)

            rule_data_group_setting_value = DeviceManagementConfigurationGroupSettingValue()
            rule_data.group_setting_collection_value = [rule_data_group_setting_value]

            rule_data_group_setting_value_children = []
            rule_data_group_setting_value.children = rule_data_group_setting_value_children

            #Create the rule id
            rule_id_simple_setting_instance = DeviceManagementConfigurationSimpleSettingInstance()
            rule_id_simple_setting_instance.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_id"

            rule_id_simple_setting_instance_value = DeviceManagementConfigurationStringSettingValue()
            rule_id_simple_setting_instance.simple_setting_value = rule_id_simple_setting_instance_value
            #This is the rule id value
            rule_id_simple_setting_instance_value.value = rule.id

            #Add it to the list
            rule_data_group_setting_value_children.append(rule_id_simple_setting_instance)

            #Create the name
            rule_name_simple_setting_instance = DeviceManagementConfigurationSimpleSettingInstance()
            rule_name_simple_setting_instance.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_name"

            rule_name_simple_setting_instance_value = DeviceManagementConfigurationStringSettingValue()
            rule_name_simple_setting_instance.simple_setting_value = rule_name_simple_setting_instance_value

            #This is the rule name
            rule_name_simple_setting_instance_value.value = rule.name

            #Add it to the list
            rule_data_group_setting_value_children.append(rule_name_simple_setting_instance)

            #Create the included groups
            if len(rule.included_groups) > 0:
                included_groups_configuration_group_setting_collection_instance = DeviceManagementConfigurationGroupSettingCollectionInstance()
                included_groups_configuration_group_setting_collection_instance.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_includedidlist"

                included_groups_configuration_group_setting_collection_instance_value = DeviceManagementConfigurationGroupSettingValue()
                included_groups_configuration_group_setting_collection_instance_group_setting_collection_value = [included_groups_configuration_group_setting_collection_instance_value]

                included_groups_configuration_group_setting_collection_instance.group_setting_collection_value = included_groups_configuration_group_setting_collection_instance_group_setting_collection_value

                included_groups_configuration_group_setting_collection_instance_value.children = []

                logger.debug("Included Groups="+str(rule.included_groups)) 
                included_group_ids = rule.included_groups

                for included_group_id in included_group_ids:

                        included_group_id_configuration_simple_setting_instance = DeviceManagementConfigurationSimpleSettingInstance()
                        included_group_id_configuration_simple_setting_instance.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_includedidlist_groupid"

                        included_group_id_configuration_simple_setting_instance_value = DeviceManagementConfigurationReferenceSettingValue()
                        included_group_id_configuration_simple_setting_instance.simple_setting_value = included_group_id_configuration_simple_setting_instance_value


                        included_reusable_setting_id = groups_map[included_group_id]
                        logger.debug(included_group_id+"=>"+included_reusable_setting_id)

                        included_group_id_configuration_simple_setting_instance_value.value = included_reusable_setting_id
                        included_group_id_configuration_simple_setting_instance_value.note = None

                        included_groups_configuration_group_setting_collection_instance_value.children.append(
                               included_group_id_configuration_simple_setting_instance
                        )


                 #Add it to the list
                rule_data_group_setting_value_children.append(included_groups_configuration_group_setting_collection_instance)

            #Create the excluded groups
            if len(rule.excluded_groups) > 0:
                excluded_groups_configuration_group_setting_collection_instance = DeviceManagementConfigurationGroupSettingCollectionInstance()
                excluded_groups_configuration_group_setting_collection_instance.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_excludedidlist"

                excluded_groups_configuration_group_setting_collection_instance_value = DeviceManagementConfigurationGroupSettingValue()
                excluded_groups_configuration_group_setting_collection_instance_group_setting_collection_value = [excluded_groups_configuration_group_setting_collection_instance_value]

                excluded_groups_configuration_group_setting_collection_instance.group_setting_collection_value = excluded_groups_configuration_group_setting_collection_instance_group_setting_collection_value

                excluded_groups_configuration_group_setting_collection_instance_value.children = []

                logger.debug("Excluded Groups="+str(rule.excluded_groups)) 
                excluded_group_ids = rule.excluded_groups

                for excluded_group_id in excluded_group_ids:

                       excluded_group_id_configuration_simple_setting_instance = DeviceManagementConfigurationSimpleSettingInstance()
                       excluded_group_id_configuration_simple_setting_instance.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_excludedidlist_groupid"

                       excluded_group_id_configuration_simple_setting_instance_value = DeviceManagementConfigurationReferenceSettingValue()
                       excluded_group_id_configuration_simple_setting_instance.simple_setting_value = excluded_group_id_configuration_simple_setting_instance_value

                       excluded_reusable_setting_id = groups_map[excluded_group_id]
                       logger.debug(excluded_group_id+"=>"+excluded_reusable_setting_id)


                       excluded_group_id_configuration_simple_setting_instance_value.value = excluded_reusable_setting_id
                       excluded_group_id_configuration_simple_setting_instance_value.note = None

                       excluded_groups_configuration_group_setting_collection_instance_value.children.append(
                              excluded_group_id_configuration_simple_setting_instance
                       )


                #Add it to the list
                rule_data_group_setting_value_children.append(excluded_groups_configuration_group_setting_collection_instance)


            #This is an entry
            rule_data_entry = DeviceManagementConfigurationGroupSettingCollectionInstance()
            rule_data_entry.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry"
            rule_data_entry.group_setting_collection_value = []
            #rule_data_group_setting_collection_value.children = []

            for entry in rule.entries:
                 
                 #Add it to the list
                 #rule_data_group_setting_value_children.append(rule_data_entry)
                 rule_data_group_setting_collection_value = DeviceManagementConfigurationGroupSettingValue()
                 rule_data_entry.group_setting_collection_value.append(rule_data_group_setting_collection_value)

                 rule_data_group_setting_collection_value.children = []

                 

                 rule_data_entry_type = DeviceManagementConfigurationChoiceSettingInstance()
                 rule_data_entry_type.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_type"

                 rule_data_group_setting_collection_value.children.append(rule_data_entry_type) 

                 rule_data_entry_type_value = DeviceManagementConfigurationChoiceSettingValue()
                 rule_data_entry_type.choice_setting_value = rule_data_entry_type_value

                 match entry.enforcement: 
                     case dc.PolicyRule.Allow:
                         entry_value = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_type_allow"
                     case dc.PolicyRule.Deny:
                         entry_value = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_type_deny"
                     case dc.PolicyRule.AuditAllowed:
                         entry_value = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_type_auditallowed"
                     case dc.PolicyRule.AuditDenied:
                         entry_value = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_type_auditdenied"

                 rule_data_entry_type_value.value = entry_value
                 rule_data_entry_type_value.children = []

                 rule_data_entry_options = DeviceManagementConfigurationChoiceSettingInstance()
                 rule_data_entry_options.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_options"

                 rule_data_entry_options_value = DeviceManagementConfigurationChoiceSettingValue()
                 rule_data_entry_options.choice_setting_value = rule_data_entry_options_value

                 #Append with the options mask
                 rule_data_entry_options_value.value = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_options_"+str(int(entry.notifications))
                 rule_data_entry_options_value.children = []

                 # The options are a child to the allow/deny
                 rule_data_entry_type_value.children.append(rule_data_entry_options)


                 rule_data_entry_access_mask = DeviceManagementConfigurationChoiceSettingCollectionInstance()
                 rule_data_entry_access_mask.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_accesmask"

                 #Add it to the list
                 rule_data_group_setting_collection_value.children.append(rule_data_entry_access_mask)


                 rule_data_entry_access_mask.choice_setting_collection_value = []

                 for permission in entry.permissions:

                        if entry.permissions[permission]:
                        
                             mask_value = DeviceManagementConfigurationChoiceSettingValue()
                             mask_value.value =  "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_accesmask_"+str(permission)
                             mask_value.children = []

                             rule_data_entry_access_mask.choice_setting_collection_value.append(mask_value)


                 entry_id_setting = DeviceManagementConfigurationSimpleSettingInstance()
                 entry_id_setting.setting_definition_id = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_id"

                 entry_id_setting_value = DeviceManagementConfigurationStringSettingValue()
                 entry_id_setting_value.value = "{6f9df57a-aadb-4b41-9e35-3634dc3857e6}"

                 entry_id_setting.simple_setting_value = entry_id_setting_value

                 #Add it to the list
                 rule_data_group_setting_collection_value.children.append(entry_id_setting)

            rule_data_group_setting_value_children.append(rule_data_entry)
            logger.debug(str(rule_data))
            return rule_data






        def createRulesFromSetting(setting):

            rules = []
            for group_setting_collection_value in setting.group_setting_collection_value:
                for child in group_setting_collection_value.children:
                    if child.setting_definition_id == DeviceControlPolicyTemplate.DeviceControlRule.RULE_DATA_SETTING_ID:
                        for group_setting_collection_value_2 in child.group_setting_collection_value:

                            #I think this is all of the data for the rule
                            rule = DeviceControlPolicyTemplate.DeviceControlRule()
                            for rules_data_setting in group_setting_collection_value_2.children:
                                match rules_data_setting.setting_definition_id:
                                    case DeviceControlPolicyTemplate.DeviceControlRule.RULE_DATA_ID_SETTING_ID:
                                        #this is the rule id
                                        rule.id = rules_data_setting.simple_setting_value.value

                                    case DeviceControlPolicyTemplate.DeviceControlRule.RULE_DATA_INCLUDED_GROUPS_SETTING_ID:
                                        rule.included_groups = DeviceControlPolicyTemplate.Util.get_values_from_group_setting_collection_instance_as_list(rules_data_setting)

                                    case DeviceControlPolicyTemplate.DeviceControlRule.RULE_DATA_EXCLUDED_GROUPS_SETTING_ID:
                                        rule.excluded_groups = DeviceControlPolicyTemplate.Util.get_values_from_group_setting_collection_instance_as_list(rules_data_setting)

                                    case DeviceControlPolicyTemplate.DeviceControlRule.RULE_DATA_ENTRY_SETTING_ID:
                                        
                                        
                                        for entry_setting in rules_data_setting.group_setting_collection_value:
                                            entry = DeviceControlPolicyTemplate.DeviceControlRule.Entry(entry_setting)
                                            rule.entries.append(entry)

                                    case DeviceControlPolicyTemplate.DeviceControlRule.RULE_DATA_NAME_SETTING_ID:

                                        rule.name = rules_data_setting.simple_setting_value.value

                                    case _:
                                        logger.warn("Unknown rules_data_setting.setting_definition_id "+rules_data_setting.setting_definition_id)

                        rules.append(rule)

            return rules

        class Entry:

            ENTRY_ID_SETTING_ID =   'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_id'
            ENTRY_TYPE_SETTING_ID  =   'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_type'
            ENTRY_ACCESS_MASK_SETTING_ID   =   'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_accesmask'
            ENTRY_NAME_SETTING_ID =  "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_name"

            ENTRY_ACCESS_MASK_READ_SETTING_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_accesmask_1'
            ENTRY_ACCESS_MASK_WRITE_SETTING_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_accesmask_2'
            ENTRY_ACCESS_MASK_EXECUTE_SETTING_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_accesmask_4'
            ENTRY_ACCESS_MASK_PRINT_SETTING_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_accesmask_64'

            def __init__(self,entry_setting):

                    for entry_data in entry_setting.children:
                        
                        match entry_data.setting_definition_id:
                            case self.ENTRY_ID_SETTING_ID:
                                self.entry_id = entry_data.simple_setting_value.value
                            case self.ENTRY_TYPE_SETTING_ID:
                                self.entry_type = entry_data.choice_setting_value.value
                                self.options = entry_data.choice_setting_value.children[0].choice_setting_value.value
                            case self.ENTRY_ACCESS_MASK_SETTING_ID:
                                
                                self.access_mask = 0
                                for access_mask_selection in entry_data.choice_setting_collection_value:
                                    match access_mask_selection.value:
                                        case self.ENTRY_ACCESS_MASK_READ_SETTING_ID:
                                            self.access_mask = self.access_mask + 1
                                        case self.ENTRY_ACCESS_MASK_WRITE_SETTING_ID:
                                            self.access_mask = self.access_mask + 2
                                        case self.ENTRY_ACCESS_MASK_EXECUTE_SETTING_ID:
                                            self.access_mask = self.access_mask + 4
                                        case self.ENTRY_ACCESS_MASK_PRINT_SETTING_ID:
                                            self.access_mask = self.access_mask + 64
                            case self.ENTRY_NAME_SETTING_ID:
                                self.entry_name = entry_data.simple_setting_value.value  
                            case _:
                                logger.warn("Unknown entry_data.setting_definition_id "+entry_data.setting_definition_id)                                      




        RULE_SETTING_ID = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}"
        RULE_DATA_SETTING_ID = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata"
        RULE_DATA_ID_SETTING_ID  = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_id"
        RULE_DATA_INCLUDED_GROUPS_SETTING_ID = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_includedidlist"
        RULE_DATA_EXCLUDED_GROUPS_SETTING_ID = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_excludedidlist"
        RULE_DATA_ENTRY_SETTING_ID = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry"
        
        RULE_DATA_ENTRY_TYPE_DENY_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_type_deny'
        RULE_DATA_ENTRY_TYPE_ALLOW_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_type_allow'
        RULE_DATA_ENTRY_TYPE_AUDIT_DENIED_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_type_auditdenied'
        RULE_DATA_ENTRY_TYPE_AUDIT_ALLOWED_ID = 'device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_entry_type_auditallowed'
        
        
        RULE_DATA_NAME_SETTING_ID = "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}_ruledata_name"

        def __init__(self):
            
            self.description = ""
            self.entries = []
            self.id = None
            self.included_groups = []
            self.excluded_groups = []
            self.name = ""
            self.setting_id = None

            
        def __str__(self):
            '''
            <PolicyRule Id="{f7e75634-7eec-4e67-bec5-5e7750cb9e02}"> 
                <!-- Allow Any Read activity -->
                <!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7bf7e75634-7eec-4e67-bec5-5e7750cb9e02%7d/RuleData -->
                <Name>Allow Read Activity</Name>
                <IncludedIdList>
		            <GroupId>{9b28fae8-72f7-4267-a1a5-685f747a7146}</GroupId>
                </IncludedIdList>
                <ExcludedIdList>
                </ExcludedIdList>
                <Entry Id="{27c79875-25d2-4765-aec2-cb2d1000613f}">
                    <Type>Allow</Type>
                    <Options>0</Options>
                    <AccessMask>9</AccessMask>
                </Entry>
                <Entry Id="{b280c2bf-ca5d-46a1-afc9-7e34d8098ca7}">
                    <Type>AuditAllowed</Type>
                    <Options>2</Options>
                    <AccessMask>9</AccessMask>
                </Entry>
            </PolicyRule>
            '''
            

            rule = ET.Element("PolicyRule", Id=self.id)
            name_comment = ET.Comment(self.name)
            rule.append(name_comment)
            
            oma_uri_comment = ET.Comment("./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/"+urllib.parse.quote(self.id))
            rule.append(oma_uri_comment)

            name = ET.SubElement(rule,"Name",{})
            name.text = self.name

            
            includedid_list = ET.SubElement(rule,"IncludedIdList")
            for included_group in self.included_groups:
                group_id = ET.SubElement(includedid_list,"GroupId")
                if isinstance(included_group,str):
                    group_id.text = included_group
                else:
                    group_id.text = included_group.id


            excludedid_list = ET.SubElement(rule,"ExcludedIdList")
            for excluded_group in self.excluded_groups:
                group_id = ET.SubElement(excludedid_list,"GroupId")
                if isinstance(excluded_group,str):
                    group_id.text = excluded_group
                else:    
                    group_id.text = excluded_group.id

                
            for entry in self.entries:
                entry_element = ET.SubElement(rule,"Entry",Id=entry.entry_id)
                access_mask = ET.SubElement(entry_element,"AccessMask")
                access_mask.text = str(entry.access_mask)
                
                options = ET.SubElement(entry_element,"Options")
                options.text = str(entry.options).split("_")[-1]
                
                type = ET.SubElement(entry_element,"Type",{})
                match entry.entry_type:
                    case DeviceControlPolicyTemplate.DeviceControlRule.RULE_DATA_ENTRY_TYPE_ALLOW_ID:
                        type.text = "Allow"
                    case DeviceControlPolicyTemplate.DeviceControlRule.RULE_DATA_ENTRY_TYPE_AUDIT_ALLOWED_ID:
                        type.text = "AuditAllowed"
                    case DeviceControlPolicyTemplate.DeviceControlRule.RULE_DATA_ENTRY_TYPE_DENY_ID:
                        type.text = "Deny"
                    case DeviceControlPolicyTemplate.DeviceControlRule.RULE_DATA_ENTRY_TYPE_AUDIT_DENIED_ID:
                        type.text = "AuditDenied"
                    case _:
                        logger.warn("Unknown entry.entry_type "+entry.entry_type)
            
            ET.indent(rule, space="\t", level=0)
            return ET.tostring(rule,method="xml").decode("utf-8")

            






    class DeviceControlPolicy:

        def __init__(self,version, id,name,policy_settings,assignments):
            
            logger.debug(">>>DeviceControlPolicy.__init__ id="+id+" name="+name+" version="+version)
            logger.debug(">>>DeviceControlPolicy.__init__ policy_settings="+str(policy_settings))

            self.id = id
            self.version = version
            self.name = name
            self.os = Package.WINDOWS_OS

            self.settings = []
            self.rules = []
            self.rules_metadata_id = None
            self.groups = []

            self.assignments = assignments
            self.intune_assignments = []
            self.policy_settings = policy_settings

        async def proces_data(self,graph):
            for assignment in self.assignments.value:
                intune_assignment = Package.IntuneAssignment(assignment)
                await intune_assignment.update_groups(graph)
                self.intune_assignments.append(intune_assignment)
            
            self.assignments = self.intune_assignments
            self.description = ""

            #just store the objects for now
            for setting_id in self.policy_settings.keys():
                if setting_id == DeviceControlPolicyTemplate.DeviceControlRule.RULE_SETTING_ID:
                    rules = self.policy_settings[setting_id]["value"]
                    self.rules_metadata_id = self.policy_settings[setting_id]["id"]
                    for rule in rules:
                        self.rules.append(rule)

                    #retrieve the groups from the rule
                    for group in rule.included_groups:
                        logger.debug("Adding included_group "+str(group))
                        self.groups.append(group)

                    for group in rule.excluded_groups:
                        logger.debug("Adding excluded_group "+str(group))
                        self.groups.append(group)
    
                else:
                    #setting id is the oma-uri
                    policy_setting = self.policy_settings[setting_id]
                    name = dc.Setting.getSettingNameFor(setting_id)

                    value_dict = policy_setting["value"]
                    config = policy_setting["config"]
                    id = policy_setting["id"]

                    for key in value_dict.keys():
                        value = value_dict[key]

                        if hasattr(value,"name"):
                            dc_setting = dc.Setting(key,value.name) 
                        else:
                            dc_setting = dc.Setting(key,value)

                        intune_setting = Package.IntuneSetting(dc_setting,config.display_name)
                        intune_setting.metadata_id = id
                        self.settings.append(intune_setting)
                    

                    
                     
                        
                    
            


    async def getTemplate(graph):
        template = DeviceControlPolicyTemplate(graph)
        await template.load_data()
        return template

    def __init__(self,graph):
        self.dc_setting_instance_templates = {}
        self.graph = graph


    async def getPolicies(self,policyFilter):

        policies = []

        #get the device control configuration policies
        dc_policies = await self.graph.get_device_control_policies()
        logger.info("v2 policies retrieved="+str(len(dc_policies.value))+" policies.")
        for dc_policy in dc_policies.value:

            id = dc_policy.id
            name = dc_policy.name

            if policyFilter is not None and policyFilter.included_policies is not None:
                if name not in policyFilter.included_policies:
                    logger.debug("Not including policy name="+name)
                    continue


            description = dc_policy.description

            settings = await self.graph.get_device_control_policy_settings(id)

            settings_value_for_policy = {}
            for setting in settings.value:

                setting_config = \
                    await self.get_configuration_settings_for_definition(
                        setting.setting_instance.setting_definition_id
                )

                setting_value = await self.get_value(setting)
                if setting.setting_instance.setting_definition_id == DeviceControlPolicyTemplate.DeviceControlRule.RULE_SETTING_ID:
                    settings_value_for_policy[setting.setting_instance.setting_definition_id] = { "value": setting_value, "id": setting.id }
                else:
                    oma_uri = setting_config.base_uri + setting_config.offset_uri
                    settings_value_for_policy[oma_uri] = { "value": setting_value, "config": setting_config , "id": setting.id}


            assignments = await self.graph.get_assignments_for_policy(id)



            policy = DeviceControlPolicyTemplate.DeviceControlPolicy("v2",id,name,settings_value_for_policy,assignments)
            await policy.proces_data(self.graph)
            policy.description = description

            logger.info("Retrieved policy name="+policy.name+" id=("+policy.id+")")
            policies.append(policy)

        return policies    





    async def load_data(self):

        
        dc_policy_template = await self.graph.get_device_control_policy_template()
        dc_policy_template_id = dc_policy_template.value[0].id

        dc_policy_template_settings_instance_templates = await self.graph.get_configuration_policy_settings_templates_by_id(dc_policy_template_id)
        
        #Add the settings from the dc template to the devicecontrol api settings
        for dc_policy_template_setting_instance_template in dc_policy_template_settings_instance_templates.value:
            setting_instance_template = dc_policy_template_setting_instance_template.setting_instance_template
            
            details = await self.get_configuration_settings_for_definition(setting_instance_template.setting_definition_id)
            
            if details.id == "device_vendor_msft_defender_configuration_devicecontrol_policyrules_{ruleid}":
                #This is the setting in the template for the rules 
                continue

            name = details.display_name
            description = details.description

            setting_data = dc.Setting.Data(name,description)

            oma_uri = details.base_uri + details.offset_uri

            setting_data.set_oma_uri(oma_uri)
            setting_data.set_supported(dc.Format.OMA_URI,True)

            if len(details.info_urls) > 0:
                documentation = details.info_urls[0]
                setting_data.set_documentation(dc.Format.OMA_URI,documentation)

            value_type = None
            if details.odata_type == "#microsoft.graph.deviceManagementConfigurationChoiceSettingDefinition":
                value_map = {}
                for option in details.options:
                    value_map[option.name] = option.option_value.value 
                    value_type = option.option_value.odata_type

                    for depended_on_by in option.depended_on_by:
                        
                        depended_on_by_id = depended_on_by.depended_on_by
                        depended_on_by_details = await self.get_configuration_settings_for_definition(depended_on_by_id)
                        
                        dependent_name = depended_on_by_details.display_name
                        dependent_description = depended_on_by_details.description

                        dependent_setting_data = dc.Setting.Data(dependent_name,dependent_description)

                        dependent_oma_uri = depended_on_by_details.base_uri + depended_on_by_details.offset_uri

                        dependent_setting_data.set_oma_uri(dependent_oma_uri)
                        dependent_setting_data.set_supported(dc.Format.OMA_URI,True)

                        if hasattr(depended_on_by_details,"value_definition"):
                            dependent_value_type = depended_on_by_details.value_definition.odata_type
                        
                            if "Integer" in dependent_value_type:
                                dependent_setting_data.set_oma_uri_type(dc.Setting.OMA_URI_Integer_DataType)
                            elif "String" in dependent_value_type:
                                dependent_setting_data.set_oma_uri_type(dc.Setting.OMA_URI_String_DataType)
                            else:
                                logger.warn("Unknown dependent_value_type "+dependent_value_type)

                        if len(depended_on_by_details.info_urls) > 0:
                            dependent_documentation = depended_on_by_details.info_urls[0]
                            dependent_setting_data.set_documentation(dc.Format.OMA_URI,dependent_documentation)

                    
                        dc.Setting.addSettingData(depended_on_by_details.name,dependent_setting_data.get_data())
                        

                setting_data.set_value_map(dc.Format.OMA_URI,value_map)

            elif details.odata_type == "#microsoft.graph.deviceManagementConfigurationSimpleSettingCollectionDefinition":
                
                value_definition = details.value_definition
                value_type = value_definition.odata_type 
                
            else:
                #This is a type that we don't parse
                logger.warn("Unknown details.odata_type "+details.odata_type)
                continue


            if "Integer" in value_type:
                setting_data.set_oma_uri_type(dc.Setting.OMA_URI_Integer_DataType)
            elif "String"in value_type:
                setting_data.set_oma_uri_type(dc.Setting.OMA_URI_String_DataType)
            else:
                logger.warn("Unknown value_type "+value_type)

            dc.Setting.addSettingData(details.name,setting_data.get_data())

        group_settings = await self.graph.get_reusable_settings_for_groups()
        for group_setting in group_settings.value:
            DeviceControlPolicyTemplate.DeviceControlGroup.group_settings[group_setting.id] = group_setting

    async def get_configuration_settings_for_definition(self,definitionId):
        details = await self.graph.get_configuration_settings_for_definition(definitionId)
        return details

    async def get_value(self,setting):
        setting_instance = setting.setting_instance
        
        if setting_instance.odata_type == "#microsoft.graph.deviceManagementConfigurationChoiceSettingInstance":
            return await self.get_choice_value(setting_instance)
        elif setting_instance.odata_type == "#microsoft.graph.deviceManagementConfigurationGroupSettingCollectionInstance":
            if setting_instance.setting_definition_id == DeviceControlPolicyTemplate.DeviceControlRule.RULE_SETTING_ID:
                rules = DeviceControlPolicyTemplate.DeviceControlRule.createRulesFromSetting(setting_instance)
                for rule in rules:
                    updated_included_groups = []
                    for group_id in rule.included_groups:
                        group_setting = await self.graph.get_group_details(group_id)
                        group = DeviceControlPolicyTemplate.DeviceControlGroup.createGroupfromSetting(group_setting)
                        updated_included_groups.append(group)

                    rule.included_groups = updated_included_groups

                    updated_excluded_groups = []
                    for group_id in rule.excluded_groups:
                        group_setting = await self.graph.get_group_details(group_id)
                        group = DeviceControlPolicyTemplate.DeviceControlGroup.createGroupfromSetting(group_setting)
                        updated_excluded_groups.append(group)

                    rule.excluded_groups = updated_excluded_groups

                return rules
            
            else:
                logger.warn("Unknown setting_instance.setting_definition_id "+setting_instance.setting_definition_id)

    async def get_choice_value(self,setting_instance):
         
         
        logger.debug("choice_value > setting_instance > setting_definition_id="+setting_instance.setting_definition_id)
        choice_setting_value = setting_instance.choice_setting_value

        logger.debug("choice_value > setting_instance > choice_setting_value="+choice_setting_value.odata_type)

        if choice_setting_value.odata_type == "#microsoft.graph.deviceManagementConfigurationChoiceSettingValue":
            logger.debug("choice_value > setting_instance > choice_setting_value > value ="+choice_setting_value.value)
            
            config = await self.graph.get_configuration_settings_for_definition(setting_instance.setting_definition_id)
            option = await self.get_option_for_value(setting_instance.setting_definition_id,choice_setting_value.value)
            
            #oma_uri = config.base_uri + config.offset_uri

            result = {config.name: option}
            if len(choice_setting_value.children) == 0:
                return result
            else:
                
                for child in choice_setting_value.children:
                    value = None

                    child_config = await self.graph.get_configuration_settings_for_definition(child.setting_definition_id)

                    if child.odata_type == "#microsoft.graph.deviceManagementConfigurationSimpleSettingCollectionInstance":
                        value = self.get_simple_setting_collection_value(child)
                    elif child.odata_type == "#microsoft.graph.deviceManagementConfigurationChoiceSettingInstance":
                        option = await self.get_choice_setting_option(child)
                        value = option
                    else:
                        logger.warn("Unknown choice_value > setting_instance > choice_setting_value > child > odata_type="+child.odata_type)

                    #oma_uri = child_config.base_uri + child_config.offset_uri
                    result[child_config.name] = value

                return result
        else:
            logger.warn("Unknown choice_setting_value.odata_type "+choice_setting_value.odata_type)        

    def get_simple_setting_collection_value(self,simple_setting_collection_instance):
        logger.debug("get_simple_setting_collection_value "+str(simple_setting_collection_instance))
        collection = []
        for value in simple_setting_collection_instance.simple_setting_collection_value:
            if "String" in value.odata_type:
                collection.append(str(value.value))
            else:
                logger.warn("Unknown value.odata_type "+value.odata_type)

        return collection


    async def get_choice_setting_option(self,choice_setting_instance):
        value = choice_setting_instance.choice_setting_value.value
        return await self.get_option_for_value(choice_setting_instance.setting_definition_id,value)

    async def get_option_for_value(self,setting_definition_id,value):
        setting_value = None
        settings = await self.get_configuration_settings_for_definition(setting_definition_id)
        for option in settings.options:
            if option.item_id == value:
                setting_value = option

        return setting_value
                    



        

class Package:


    WINDOWS_OS = "windows"
    MAC_OS = "macOS"

    MAC_PATH = MAC_OS+".devicecontrol.policies"
    WINDOWS_GROUPS_PATH = WINDOWS_OS+".devicecontrol.groups"
    WINDOWS_RULES_PATH = WINDOWS_OS+".devicecontrol.rules"
    WINDOWS_DEVICE_CONTROL = WINDOWS_OS+".devicecontrol"

    MAC_DEVICE_CONTROL = "macOS.devicecontrol"
    MAC_DEVICE_CONTROL_POLICIES = "macOS.devicecontrol.policies"

    SOURCE_PATH = "src"

    layout = [
        MAC_OS,
        MAC_DEVICE_CONTROL,
        MAC_DEVICE_CONTROL_POLICIES,
        WINDOWS_OS,
        WINDOWS_DEVICE_CONTROL,
        WINDOWS_GROUPS_PATH,
        WINDOWS_RULES_PATH,
        SOURCE_PATH
    ]

    def getSHA256Hash(filename, mode = "r"):

        file = open(filename,mode)
        contents = file.read()

        if mode == "rb":
            hashed_object = hashlib.sha256(contents)
        else:
            hashed_object = hashlib.sha256(contents.encode())
        hash_result = hashed_object.hexdigest()
        file.close()
        return hash_result
        

    class IntuneResults:


        class UpdateApplied:
            def __init__(self,id):
                self.id = id
                pass

        class NoChangesNeeded:
            def __init__(self,id):
                self.id = id
                pass

        class ObjectDeleted:

            def __init__(self,id):
                if id is not None:
                    logger.debug("id="+id)
                else:
                    logger.debug("id=None")
                self.id = id


        def was_successful_result(result):
            
            if result is None:
                return False
            elif isinstance(result,RuntimeError):
                return False
            elif isinstance(result,ODataError):
                return False
            else:
                logger.debug("result="+str(result))
                return True

        def __init__(self,operation, meta_data_for_policy):

            self.operation = operation

            self.results =  {
                "groups":{},
                "policy": None
            }

            self.meta_data_for_policy = meta_data_for_policy


        def setResultForPolicy(self,result):
            self.results["policy"] = result

        def addResultForGroup(self,result,group):
            if isinstance(group,str):
                self.results["groups"][group] =result
            elif hasattr(group,"name"):
                self.results["groups"][group.name] =result
            else:
                raise Exception("Unsupported object "+str(group)+" passed to addResultToGroup")

        def getResultForGroup(self,group):
            logger.debug("group_name=("+group.name+")")
            logger.debug("group dict="+str(group.__dict__))
            group_name = str(group.name).strip()
            logger.debug("results="+str(self.results))
            keys = list(self.results["groups"].keys())
            logger.debug("keys="+str(keys))
            if group_name not in keys:
                if "metadata_id" in group.__dict__:
                    return Package.IntuneResults.NoChangesNeeded(group.__dict__["metadata_id"])
                else:
                    return Package.IntuneResults.NoChangesNeeded(None)
            else:
                return self.results["groups"][group.name]

        def getPolicyResult(self):
            return self.results["policy"]

        def was_successful(self):

            was_successful = True

            was_successful = was_successful & Package.IntuneResults.was_successful_result(self.results["policy"])

            for group_name in self.results["groups"]:
                group_result = self.results["groups"][group_name]
                was_successful = was_successful & Package.IntuneResults.was_successful_result(was_successful & Package.IntuneResults.was_successful_result(group_result))

            return was_successful
    

        
            

    class IntuneSetting:

        def __init__(self,dc_setting,name = None,description = None):
            self.setting = dc_setting
            self.name = name
            self.description = description

            self.metadata_id = None
            pass

        def get_oma_uri(self):

            return dc.Setting.getOMAURIFor(self.setting.name)
        
    class IntuneAssignment:

        class TargetGroup:

            def __init__(self,group):

                self.name = group.display_name
                self.id = group.id
                self.odata_type = group.odata_type
                self.security_enabled = group.security_enabled
                self.security_identifier = group.security_identifier


            def toJSON(self):

                return {
                    "name": self.name,
                    "id": self.id
                }
                


        def __init__(self,assignments):

            self.metadata_id = None
            self.metadata_source_id = None
            self.metadata_additional_data = None


            if hasattr(assignments,"id"):
                self.metadata_id = assignments.id
            if hasattr(assignments,"source_id"):
                self.metadata_source_id = assignments.source_id
            if hasattr(assignments,"additional_data"):
                self.metadata_additional_data = assignments.additional_data

            self.data = None

            if hasattr(assignments,"value"):
                for assignment in assignments.value:
                    target = assignment.target
                    self.update_data_for_target(target)
            elif hasattr(assignments,"target"):
                target = assignments.target
                self.update_data_for_target(target)
            else:
                logger.warn("Unknown assignments "+assignments)

        async def update_groups(self,graph):
                
            group = self.data["group"]
            if "id" in group.keys():
                group_id = group["id"]
                group = await graph.get_group_by_id(group_id)
                self.data["group"] = Package.IntuneAssignment.TargetGroup(group).toJSON()
                
        def update_data_for_target(self,target):

                target_type = target.odata_type

                if target_type == "#microsoft.graph.allDevicesAssignmentTarget":
                    self.data = {"type":"include","group":{"name":"all machines"}}
                elif target_type == "#microsoft.graph.allLicensedUsersAssignmentTarget":
                    self.data ={"type":"include","group":{"name":"all users"}}
                elif target_type == "#microsoft.graph.exclusionGroupAssignmentTarget":
                    excluded_group_id = target.group_id
                    self.data = {"type":"exclude","group":{"id":excluded_group_id}}
                elif target_type == "#microsoft.graph.groupAssignmentTarget":
                    included_group_id = target.group_id
                    self.data ={"type":"include","group":{"id":included_group_id}}
                else:
                    logger.warn("Unknown target_type "+target_type)

        def toJSON(self):

            return json.dumps(self.data,indent=5)
            
    class Policy:


        def __init__(self, graph):
            self.name = "A Windows Policy"
            self.description = "A default description for the policy"
            self.rules = []
            self.groups = []
            self.settings = []
            self.os = Package.WINDOWS_OS
            self.id = None
            self.assignments = []
            self.version = "v1"

            self.graph = graph

        async def setAssignments(self,assignments):

            for assignment in assignments.value:
                intune_assignment = Package.IntuneAssignment(assignment)
                await intune_assignment.update_groups(self.graph)
                self.assignments.append(intune_assignment)


        def addGroup(self,group):
            self.groups.append(group)

        def addRule(self,rule):
            self.rules.append(rule)

        def addSetting(self,setting):
            self.settings.append(setting)

        def setPayload(self,payload):
            if self.os == Package.MAC_OS:
                mac_policy = json.loads(payload)

                if "groups" in mac_policy.keys():
                    for group in mac_policy["groups"]:
                        self.groups.append(dc.Group(group,"mac"))

                if "rules" in mac_policy.keys():
                    for rule in mac_policy["rules"]:
                        self.rules.append(dc.PolicyRule(rule,"mac"))

                
                dc_settings = dc.Settings.generate_settings_from_mac_policy(mac_policy)
                for dc_setting in dc_settings:
                    self.settings.append(Package.IntuneSetting(dc_setting))

        def getMacOSSettings(self):

            settings_dict = {}
            if self.os == Package.MAC_OS:
                for setting in self.settings:
                    dc_setting = setting.setting

                    mac_settings_data = dc_setting.data[dc_setting.name]["mac"]["mac_setting"]
                    
                    category = mac_settings_data["category"]

                    settings_for_category = {}

                    if category in settings_dict.keys():
                        settings_for_category = settings_dict[category]

                    if "name" in mac_settings_data:
                        setting_name = mac_settings_data["name"]
                        settings_for_category[setting_name] = dc_setting.value
                    else:    
                        settings_for_category = dc_setting.value

                    settings_dict[category] = settings_for_category

            return settings_dict
        
        def getPolicyJSON(self):

            json = {}

            if self.os == Package.MAC_OS:
                json["groups"] = self.groups
                json["rules"] = self.rules
                json["settings"] = self.getMacOSSettings()

            return json


    class Metadata:

        def __init__(self):
            self.metadata = {
                "policies":{

                }
            }
            pass

        
        def getMetadataForGroup(self,policy_name,group_name):
            logger.debug("policy_name="+policy_name+" group_name="+group_name)

            if policy_name in self.metadata["policies"]:
                if "groups" in self.metadata["policies"][policy_name]:
                    if group_name in self.metadata["policies"][policy_name]["groups"]:
                        return self.metadata["policies"][policy_name]["groups"][group_name]
                
            logger.debug("No metadata for policy_name="+policy_name+" group_name="+group_name)
            return None
        
        def getMetadataForRule(self,policy_name,rule_name):
            logger.debug("policy_name="+policy_name+" rule_name="+rule_name)

            if policy_name in self.metadata["policies"]:
                if rule_name in self.metadata["policies"][policy_name]["rules"]:
                    return self.metadata["policies"][policy_name]["rules"][rule_name]
                
            logger.debug("No metadata for policy_name="+policy_name+" rule_name="+rule_name)
            return None


        def getMetadataForPolicy(self,policy):
            
            policy_name = policy.name
            logger.debug("policy_name: "+policy_name)

            policies = self.metadata["policies"]
            
            if policy_name in policies:
                policy_meta_data = policies[policy_name]
                logger.debug("policy_name="+policy_name+" metadata="+str(policy_meta_data))
                return policy_meta_data
            else:
                logger.debug("metadata does not contain "+policy_name)
                return None

            



        def updateMetadataForPolicy(self,policy):

            from datetime import datetime

            now = str(datetime.now())
            logger.debug(">>>>>Package.Metadata.Policy "+str(policy)+" now="+now)

            if hasattr(policy,"id"):

                if policy.name in self.metadata["policies"]:
                    logger.debug("Updating last_update on current metadata.")
                    self.metadata["policies"][policy.name]["last_update"] = now
                    self.metadata["policies"][policy.name]["id"] = policy.id
                else: 
                    self.metadata["policies"][policy.name] = {
                        "id": policy.id,
                        "last_update": now
                    }

            if policy.version == "v2":
                self.metadata["policies"][policy.name]["@odata.context"] = "https://graph.microsoft.com/beta/$metadata#deviceManagement/configurationPolicies/$entity"

                if policy.id is not None:
                    settings = {
                        "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceManagement/configurationPolicies('"+policy.id+"')/settings",
                    }

                settings = {}
                for setting in policy.settings:
                    logger.debug("setting="+str(setting))
                    settings[setting.setting.name] = {
                        "id":setting.metadata_id
                }

                if hasattr(policy,"rules_metadata_id"):
                    settings["ruleid"] = {
                        "id":policy.rules_metadata_id
                    }
                    
                self.metadata["policies"][policy.name]["settings"] = settings

                groups_metadata = {}
                for group in policy.groups:

                    if isinstance(group,str):
                        logger.debug("group="+group+" for policy="+policy.name+".  No metadata")
                        continue


                    if self.getMetadataForGroup(policy.name,group.name) is None:
                        groups_metadata[group.name] = {
                            "groupdata_id":group.id,
                            "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceManagement/reusablePolicySettings(settingInstance,id,displayName,description)/$entity"
                        }
                    else:
                        logger.debug("Using existing metadata for group "+group.name)
                        groups_metadata[group.name] = self.getMetadataForGroup(policy.name,group.name)
                        groups_metadata[group.name]["last_update"] = now

                    if hasattr(group,"metadata_id"):
                        logger.debug("Setting id="+str(group.metadata_id)+" from metadata for group="+(group.name))
                        groups_metadata[group.name]["id"] = group.metadata_id
                        if hasattr(group,"last_update"):
                            logger.debug("Setting last update from group")
                            groups_metadata[group.name]["last_update"] = group.last_update
                        else:
                            logger.debug("Setting last update to now")
                            groups_metadata[group.name]["last_update"] = now

                if len(groups_metadata) > 0:
                    self.metadata["policies"][policy.name]["groups"] = groups_metadata

                rules_metadata = {}
                for rule in policy.rules:
                    rules_metadata[rule.name] = {
                        "ruledata_id":rule.id,
                        "last_update":now
                    }
                
                if len(rules_metadata) > 0:
                    self.metadata["policies"][policy.name]["rules"] = rules_metadata

                pass
            elif policy.version == "v1":

                self.metadata["policies"][policy.name]["@odata.context"] = "https://graph.microsoft.com/beta/$metadata#deviceManagement/deviceConfigurations/$entity"
    
                if policy.os == Package.WINDOWS_OS:
                    self.metadata["policies"][policy.name]["@odata.type"] = "#microsoft.graph.windows10CustomConfiguration"
                    
                    groups_metadata = {}
                    for group in policy.groups:
                        groups_metadata[group.name] = {
                            "id":group.id
                        }
                
                    if len(groups_metadata) > 0:
                        self.metadata["policies"][policy.name]["groups"] = groups_metadata

                    rules_metadata = {}
                    for rule in policy.rules:
                        rules_metadata[rule.name] = {
                            "id":rule.id
                        }
                
                    if len(rules_metadata) > 0:
                        self.metadata["policies"][policy.name]["rules"] = rules_metadata
                    
                    pass
                elif policy.os == Package.MAC_OS:
                    self.metadata["policies"][policy.name]["@odata.type"] = "#microsoft.graph.macOSCustomConfiguration"
                   
                    pass
                else:
                    logger.warn("Unknown policy.os "+policy.os)
            else:
                logger.warn("Unknown policy.version "+policy.version)

            assignments_meta_data = {}
            index = 0
            for assignment in policy.assignments:
                new_assignment = None
                logger.debug(">>>>> assignment "+str(assignment))
                
                if "id" in assignment.data["group"].keys():
                    new_assignment = {"type":assignment.data["type"],"group":{"name":assignment.data["group"]["name"]}}
                    assignments_meta_data[assignment.data["group"]["name"]] = {
                        "@odata.context": "https://graph.microsoft.com/beta/$metadata#groups/$entity",
                        "id": assignment.data["group"]["id"]
                    }
                else:
                    assignments_meta_data[assignment.data["group"]["name"]] = {}
                    new_assignment = assignment.data

                if hasattr(assignment,"metadata_id"):
                    if assignment.metadata_id is not None:
                        assignments_meta_data[assignment.data["group"]["name"]]["assignment_id"] = assignment.metadata_id

                if hasattr(assignment,"metadata_source_id"):
                    if assignment.metadata_source_id is not None:
                        assignments_meta_data[assignment.data["group"]["name"]]["assignment_source_id"] = assignment.metadata_source_id
                

                policy.assignments[index] = new_assignment

                index = index+1

            if len(assignments_meta_data) > 0:
                self.metadata["policies"][policy.name]["assignments"] = assignments_meta_data


        def __str__(self):
            return json.dumps(self.metadata,indent=5)

    def load(root_path,package_name,environment,api):

    
        p = Package(package_name,templateEnv=environment)
        p.package_root = root_path

        package_path = os.path.join(root_path,package_name)

        package_file_name = os.path.join(package_path,"package.json")
        metadata_file_name = os.path.join(package_path,"metadata.json")

        package_file = open(package_file_name,"r") 
        p.package_json = json.load(package_file)

        metadata_file = open(metadata_file_name,"r")
        p.metadata.metadata = json.load(metadata_file)


        logger.debug("package_json="+str(p.package_json))
        logger.debug("metadata_json="+str(p.metadata.metadata))

        policies_json = p.package_json["policies"]
        

        for policy_name in policies_json:
            logger.info("loading policy "+policy_name)
            policy_json = policies_json[policy_name]


            
            policy_os = policy_json["os"]
            policy_version = policy_json["version"]
            policy_description = policy_json["description"]


            settings = []
            for setting_name in policy_json["settings"]:
                logger.info("Loading setting "+setting_name)
                setting_value = policy_json["settings"][setting_name]["value"]
                setting = Setting(setting_name,setting_value)
                settings.append(setting)

            groups = []
            for group_name in policy_json["groups"]:
                group_json = policy_json["groups"][group_name]
                logger.info("Loading group "+group_name)

                file = group_json["file"]

                path = file["path"]
                sha256 = file["sha256"]

                group_file = open(path,"r")
                group_xml = group_file.read()

                logger.debug("group_xml="+group_xml)
                
                parser = ET.XMLParser(remove_comments=False)
                
                group = dc.Group(
                    ET.fromstring(group_xml,parser),dc.Format.OMA_URI,
                    str(pathlib.Path(path).resolve()))

                groups.append(group)
                group_file.close()

                group_meta_data = p.metadata.getMetadataForGroup(policy_name,group_name)
                if "id" in group_meta_data:
                    logger.debug("Setting metadata_id to "+str(group_meta_data["id"]))
                    group.__dict__["metadata_id"] = group_meta_data["id"]
                
                if "last_update" in group_meta_data:
                    group.__dict__["last_update"] = group_meta_data["last_update"]


            rules = []
            for rule_name in policy_json["rules"]:
                rule_json = policy_json["rules"][rule_name]
                logger.info("Loading rule "+rule_name)

                file = rule_json["file"]
                description = rule_json["description"]

                path = file["path"]
                sha256 = file["sha256"]

                rule_file = open(path,"r")
                rule_xml = rule_file.read()

                logger.debug("rule_xml="+rule_xml)
                rule = dc.PolicyRule(
                    ET.fromstring(rule_xml),dc.Format.OMA_URI,
                    str(pathlib.Path(path).resolve()))
                
                rule.description = description
                rules.append(rule)
                rule_file.close()

            policy = api.createPolicy(
                name=policy_name,
                os=policy_os,
                version=policy_version,
                description=policy_description,
                rules=rules,
                groups=groups,
                settings=settings)
            
            policies_metadata_json = p.metadata.getMetadataForPolicy(policy)
            policy_id = policies_metadata_json["id"]

            if policy_id is not None:
                policy.id = policy_id

            p.addPolicy(policy=policy)

            


        package_file.close()
        metadata_file.close()
        
        return p
        
    def __init__(self,name,templateEnv=None):

        self.name = name
        self.policies = []
        self.templateEnv = templateEnv
        if templateEnv is None:
            templateLoader = jinja2.FileSystemLoader("templates")
            self.templateEnv = jinja2.Environment(loader=templateLoader)

        self.metadata = Package.Metadata()
        self.source_path = None
        self.package_json = None
        
        self.package_root = None


    def addPolicy(self,policy):
        self.policies.append(policy)
        self.metadata.updateMetadataForPolicy(policy)


    def save_metadata(self):
        
        package_path = pathlib.PurePath(os.path.join(self.package_root,self.name))
        metadata_file_path = pathlib.PurePath(os.path.join(package_path,"metadata.json"))
        metadata_file = open(metadata_file_path,"w")
        logger.info("Writing package metadata file to "+str(metadata_file_path))
        metadata_file.write(str(self.metadata))
        metadata_file.close()


    def save(self,destination,rule_template_name,readme_template_name,description_template_name):

        self.package_root = pathlib.Path(destination).resolve()

        package_path = pathlib.PurePath(os.path.join(destination,self.name))
        if not os.path.isdir(package_path):
            os.mkdir(package_path)

        logger.info("Saving package name="+self.name+" to "+str(self.package_root))

        path_map = {}

        for layout_path in Package.layout:

            orig_path = str(layout_path)

            layout_path = layout_path.replace(".",os.sep)
            layout_path = pathlib.PurePath(os.path.join(package_path,layout_path)) 
            if not os.path.isdir(layout_path):
                os.mkdir(layout_path)

            path_map[orig_path] = layout_path

        policy_data = {}

        #This is where the documentation gets generated
        windows_dest_paths = str(path_map[Package.WINDOWS_DEVICE_CONTROL])
       
        
        if self.source_path is not None:

            import shutil

            source_file_name = pathlib.Path(self.source_path).name

            source_path_in_package=os.path.join(path_map[Package.SOURCE_PATH],source_file_name)

            try:
                shutil.copyfile(self.source_path,source_path_in_package)
            except shutil.SameFileError as e:
                logger.debug("Same file")
                
            sha256Hash = Package.getSHA256Hash(source_path_in_package,"rb")

            self.metadata.metadata["source"] = {
                "file": {
                    "path": "source"+os.sep+source_file_name,
                    "sha256": sha256Hash
                }
            }

        policies_by_name = {}

        #load_templates
        rule_template = self.templateEnv.get_template(rule_template_name)
        readme_template = self.templateEnv.get_template(readme_template_name)
        description_template = self.templateEnv.get_template(description_template_name)


        logger.info("Saving "+str(len(self.policies))+" policies.")

        for policy in self.policies:
            name = policy.name

            if name in policies_by_name:
                count = policies_by_name[name]
                count = count + 1
                
                oldname = str(name)
                name = name+"_"+str(count)
                policy.name = name

                logger.info("Renamed policy "+oldname+" to "+name)
                policies_by_name[oldname] = count
            else:
                count = 0
                policies_by_name[name] = count


            #These are the paths for the documentations     
            mac_policy_file_paths = []
            windows_policy_file_paths = {}
            doc_src = []

            #generate documentation for windows
            

            version = policy.version
            if policy.os == Package.MAC_OS:
                policy_json = policy.getPolicyJSON()

                policy_file_path = pathlib.PurePath(os.path.join(path_map[Package.MAC_PATH],name+".json"))
                policy_file = open(policy_file_path,"w")
                json.dump(policy_json,policy_file,cls=dc.DCJSONEncoder,indent=5)
                policy_file.close()

                logger.info("Exporting macOS policy "+name+" to "+str(policy_file_path))

                if policy.description is None:
                    policy.description = ""
                    
                policy_data[name] = {
                    "os":Package.MAC_OS,
                    "version": version,
                    "description": policy.description,
                    "assignments": policy.assignments,
                    "file": {
                        "path": str(policy_file_path.relative_to(package_path)),
                        "sha256": Package.getSHA256Hash(policy_file_path)
                    }
                }

                mac_policy_file_paths.append(policy_file_path)


            elif policy.os == Package.WINDOWS_OS:

                groups_data = {}
                rules_data = {}
                settings_data = {}

                logger.info("Exporting windows policy "+name)
                
                for group in policy.groups:
                    if not isinstance(group,str):
                        if count > 0:
                            old_group_name = group.name
                            group_name = old_group_name+"_"+str(count)
                            group.name = group_name
                            logger.info("Renamed group "+old_group_name+" to "+group_name)

                        group_file_path = pathlib.PurePath(os.path.join(path_map[Package.WINDOWS_GROUPS_PATH],group.name+".xml"))
                        group_file = open(group_file_path,"w")
                        group_file.write(str(group))
                        group_file.close()

                        #Add the group to the inventory
                        doc_src.append(str(group_file_path))

                        if group.description is None:
                            group.description = ""

                        groups_data [group.name] = {
                            "description": group.description,
                            "file": {
                                "path": str(group_file_path.relative_to(package_path)),
                                "sha256": Package.getSHA256Hash(group_file_path)
                            }
                        }


                        logger.info("Exporting group "+group.name+" to "+str(group_file_path))
                    else:
                        logger.warn("Group "+group+" is missing metadata.")

                    
                for rule in policy.rules:
                    if count > 0:
                        old_rule_name = rule.name
                        rule_name = old_rule_name+"_"+str(count)
                        rule.name = rule_name
                        logger.info("Renamed rule "+old_rule_name+" to "+rule_name)
                        
                    rule_file_path = pathlib.PurePath(os.path.join(path_map[Package.WINDOWS_RULES_PATH],rule.name+".xml"))
                    rule_file = open(rule_file_path,"w")
                    rule_file.write(str(rule))
                    rule_file.close()

                    logger.info("Exporting rule "+rule.name+" to "+str(rule_file_path))


                    if rule.description is None:
                        rule.description = ""

                    rules_data [rule.name] = {
                        "description": rule.description,
                        "file": {
                            "path": str(rule_file_path.relative_to(package_path)),
                            "sha256": Package.getSHA256Hash(rule_file_path)
                        }
                    }
                    

                    

                for setting in policy.settings:

                    dc_setting = setting.setting

                    settings_data[dc_setting.name] = {
                        "value" : dc_setting.value
                    }

                    if policy.version == "v1":
                        #v1 policies - OMA-URI - can have name and description
                        if setting.name is None:
                            setting.name = ""
                        settings_data[dc_setting.name]["name"] = setting.name
                        if setting.description is None:
                            setting.description = ""
                        settings_data[dc_setting.name]["description"] = setting.description
                    elif policy.version == "v2":
                        #v2 policies - no name or description
                        pass
                    else:
                        logger.warn("Unknown policy version "+policy.version)

 
                                        

                if policy.description is None:
                    policy.description = ""

                policy_data[name] = {
                    "os":Package.WINDOWS_OS,
                    "version":version,
                    "description": policy.description,
                    "assignments": policy.assignments,
                    "groups": groups_data,
                    "rules": rules_data,
                    "settings": settings_data
                }

                if count > 0:
                    self.metadata.updateMetadataForPolicy(policy)

                for rule_name in policy_data[name]["rules"]:
                    rule_file_path = pathlib.PurePath(os.path.join(path_map[Package.WINDOWS_RULES_PATH],rule_name+".xml"))
                    windows_policy_file_paths[rule_file_path] = dc.Settings(settings_data)

            #generate documentation
            logger.debug("generating_doc src="+str(windows_policy_file_paths.keys()))

            
            for src_path in windows_policy_file_paths.keys():
                doc_src.append(str(src_path))

            windows_inventory = Inventory(doc_src,None,windows_dest_paths)
            windows_inventory.load_inventory()

            query = None
            title = policy.name
            outfile = title+".md"

            result = windows_inventory.process_query(query)

            result["description"] = policy.description

            #settings_data_for_path =[windows_policy_file_path]

            try:
                
                settings = dc.Settings(settings_data)
                windows_inventory.generate_text(result,rule_template,str(path_map[Package.WINDOWS_DEVICE_CONTROL]),outfile,title,settings)
            except Exception as e:
                logger.warn(full_stack())
                logger.warn("Could not generate documentation error="+str(e))
                
            

            for windows_policy_file_path in windows_policy_file_paths.keys():
                windows_policy_file_name = str(windows_policy_file_path).split(os.sep)[-1]

            


        package_file_path = pathlib.PurePath(os.path.join(package_path,"package.json"))
        
        package_file = open(package_file_path,"w")    
        

        package_data = {
            "policies":policy_data
        }

        

        #generate documentation for mac
        mac_src_paths = [str(path_map[Package.MAC_DEVICE_CONTROL_POLICIES])]
        mac_dest_paths = str(path_map[Package.MAC_DEVICE_CONTROL])
        
        mac_inventory = Inventory(mac_src_paths,None,mac_dest_paths)
        mac_inventory.load_inventory()

        for mac_policy_file_path in mac_policy_file_paths:

            mac_policy_file_name = str(mac_policy_file_path).split(os.sep)[-1]

            query = "path.str.contains('"+str(mac_policy_file_name)+"',regex=False)"
            title = mac_policy_file_name.split(".")[0]
            outfile = title+".md"

            result = mac_inventory.process_query(query)

            result["description"] = Description(result,self.templateEnv,description_template_name)

            with open(mac_policy_file_path,"r") as json_file:
                mac_policy = json.loads(json_file.read())
                mac_settings = dc.Settings.generate_settings_from_mac_policy(mac_policy)
            
            json_file.close()
            

            try:
                mac_inventory.generate_text(result,rule_template,str(path_map[Package.MAC_DEVICE_CONTROL]),outfile,title,mac_settings)
            except Exception as e:
                logger.warn("Could not generate documentation for "+mac_policy_file_name+" error="+str(e))

        
        
        json.dump(package_data,package_file,indent=5)
        package_file.close()
        logger.info("Writing package file to "+str(package_file_path))

        self.save_metadata()

    async def delete(self,graph):

        results = {}
        for policy in self.policies:

            
            metadata_for_policy = self.metadata.getMetadataForPolicy(policy)
            result = Package.IntuneResults("delete",meta_data_for_policy=metadata_for_policy)

            
            logger.debug("policy @odata.context="+metadata_for_policy["@odata.context"])
            
            
            

            if metadata_for_policy["id"] is None:
                logger.debug("No policy in metadata")
                result.setResultForPolicy(Package.IntuneResults.NoChangesNeeded)
            else:
                
                if metadata_for_policy["@odata.context"] == "https://graph.microsoft.com/beta/$metadata#deviceManagement/configurationPolicies/$entity":
                    graph_result = await graph.delete_device_control_policy(metadata_for_policy["id"])
                else:
                    graph_result = await graph.delete_device_configuration(metadata_for_policy["id"])
            
                if not isinstance(graph_result,RuntimeError) and not isinstance(graph_result,ODataError):
                    result.setResultForPolicy(Package.IntuneResults.ObjectDeleted(metadata_for_policy["id"]))
                else:
                    result.setResultForPolicy(graph_result)

            if "groups" in metadata_for_policy:
                for group_name in metadata_for_policy["groups"]:
                    group = metadata_for_policy["groups"][group_name]
                    if "id" in group and "@odata.context" in group:
                        logger.debug("group @odata.context="+group["@odata.context"])

                        #see if the group exists
                        group_details = await graph.get_group_details(group["id"])

                        group_result = await graph.delete_group_v2(group["id"])
                        if isinstance(group_result,ODataError):
                            result.addResultForGroup(group_result,group_name)
                        else:
                            result.addResultForGroup(Package.IntuneResults.ObjectDeleted(group["id"]),group_name)
                    else:
                        logger.debug("No id in group "+group_name)
                
            results[policy.name] = result
            
        self.process_results(results)

    def getIntuneObjectMetadata(self, policy_param = None):

        if policy_param is not None:
            logger.debug("policy_param="+policy_param)

        ids = {
            "https://graph.microsoft.com/beta/$metadata#deviceManagement/deviceConfigurations/$entity":{
                "ids":[],
                "label":"v1 policies"
            },
            "https://graph.microsoft.com/beta/$metadata#deviceManagement/configurationPolicies/$entity":{
                "ids":[],
                "label":"v2 policies"
            },
            "https://graph.microsoft.com/beta/$metadata#deviceManagement/reusablePolicySettings(settingInstance,id,displayName,description)/$entity":{
                "ids":[],
                "label":"reusable settings"
            }

        }

        for policy in self.policies:

            if policy_param is not None and policy != policy_param:
                continue

            policy_metadata = self.metadata.getMetadataForPolicy(policy)

            odata_context = policy_metadata["@odata.context"]
            ids_for_odata_context = ids[odata_context]["ids"]

            if not "id" in policy_metadata:
                logger.error(policy.name+" has no id in metadata.")
                continue

            ids_for_odata_context.append(policy_metadata)

            if "groups" not in policy_metadata:
                continue

            for group_name in policy_metadata["groups"]:

                group_metadata = policy_metadata["groups"][group_name]
                if "@odata.context" in group_metadata:
                    group_odata_context = group_metadata["@odata.context"]
                    ids_for_group_odata_context = ids[group_odata_context]["ids"]
                    ids_for_group_odata_context.append(group_metadata)

            

        return ids 







    
    async def deploy(self,graph):
        logger.info("Deploying package "+self.name+" to tenantId"+graph.tenant_id)

        results = {}
        for policy in self.policies:

            operation = "new"
            version = policy.version
            os = policy.os

            logger.info("name="+policy.name+" version="+policy.version+" os="+policy.os)

            metadata_for_policy = self.metadata.getMetadataForPolicy(policy)

            if version not in ["v1","v2"]:
                logger.error("Unsupported policy version "+version)
                results[policy.name] = Package.IntuneAssignment(
                    operation="?",
                    error=RuntimeError("Unsupported policy version "+version),
                    metadata_for_policy=metadata_for_policy
                )
                continue

            if os not in [Package.MAC_OS, Package.WINDOWS_OS]:
                logger.error("Unsupported os "+os)
                results[policy.name] = Package.IntuneAssignment(
                    operation="?",
                    error=RuntimeError("Unsupported os "+os),
                    metadata_for_policy=metadata_for_policy
                )
                continue

            if os == Package.MAC_OS and version == "v2":
                logger.error("macOS only supports v1")
                results[policy.name] = Package.IntuneAssignment(
                    operation="?",
                    error=RuntimeError("macOS only supports v1"),
                    metadata_for_policy=metadata_for_policy
                )              
                continue
            
            if metadata_for_policy is None:
                logger.debug("No metadata for policy "+policy.name)
            else:
                logger.debug(str(metadata_for_policy))
                if "id" in metadata_for_policy and metadata_for_policy["id"] is not None:
                    operation = "update"
                else:
                    if "groups" in metadata_for_policy:
                        for group in metadata_for_policy["groups"]:
                            if "id" in metadata_for_policy["groups"][group] and metadata_for_policy["groups"][group]["id"] is not None:
                                operation = "update_groups_only"
                                logger.debug("Updating existing groups")
                                break


            logger.debug("operation is "+operation)



            if os == Package.MAC_OS:
                result = await self.deployMacPolicy(graph,policy,operation,metadata_for_policy)
                results[policy.name] = result
            elif version == "v1":
                result = await self.deployOMAUriPolicy(graph,policy,operation,metadata_for_policy)
                results[policy.name] = result
            else:
                result = await self.deployDCV2Policy(graph,policy,operation,metadata_for_policy)
                results[policy.name] = result
        
        self.process_results(results)

        return results

    
    def process_results(self,results):
        logger.debug("results="+str(results))

        i = 0
        
    
        for policy_name in results:

            save_metadata = False
            policy = self.policies[i]
            if policy.id is None:
                logger.debug("policy_id is None")
            else:
                logger.debug("policy_id="+policy.id)

            graph_result = results[policy_name]

            if graph_result.was_successful():
                policy_result = graph_result.getPolicyResult()

                if isinstance(policy_result,Package.IntuneResults.NoChangesNeeded):
                    logger.info("No changes to apply for "+policy.name)
                elif isinstance(policy_result,Package.IntuneResults.ObjectDeleted):
                    logger.info(policy.name+" deleted.")
                    policy.id = None
                    save_metadata = True
                else:
                    logger.debug("policy_result_keys="+str(policy_result.__dict__.keys()))
                    save_metadata = True

                for group in policy.groups:
                    group_name = group.name
                    group_result = graph_result.getResultForGroup(group)
                    logger.debug("group_result="+str(group_result))

                    if isinstance(group_result,Package.IntuneResults.NoChangesNeeded):
                        logger.info("No changes to apply for "+group.name)
                    elif isinstance(group_result,Package.IntuneResults.ObjectDeleted):
                        now = str(datetime.now())
                        logger.info(group.name+" deleted.")
                        group.__dict__["last_update"] = now
                        group.__dict__["metadata_id"] = None
                        save_metadata = True
                    elif isinstance(group_result,Package.IntuneResults.UpdateApplied):
                        now = str(datetime.now())
                        logger.info("Updating last_update time for "+group.name+" to "+now)
                        group.__dict__["last_update"] = now
                        save_metadata = True
                    else:
                        save_metadata = True

                    if hasattr(group_result,"id") and not isinstance(group_result,Package.IntuneResults.ObjectDeleted):
                        logger.debug("Setting metadata_id to "+str(group_result.id))
                        group.__dict__["metadata_id"] = group_result.id



                if "id" in policy_result.__dict__.keys() and policy_result.id is not None and not isinstance(policy_result,Package.IntuneResults.ObjectDeleted):
                    if policy.id != policy_result.id:
                        policy.id = policy_result.id
                        logger.debug("Updating policy metadata to id="+policy.id)
                        save_metadata = True

           
                    

            i=i+1
            logger.info("Policy="+policy_name+" operation="+graph_result.operation+" result="+str(graph_result.was_successful())+" update_metadata="+str(save_metadata))
            if save_metadata:
                self.metadata.updateMetadataForPolicy(policy)
                self.save_metadata()

    def deployMacPolicy(self,graph,policy,operation="new",metadata_policy_policy=None):
        logger.debug("operation="+operation)
        pass

    async def deployOMAUriPolicy(self,graph,policy,operation="new",metadata_policy_policy=None):
        logger.debug("operation="+operation)

        win10config = Windows10CustomConfiguration()
        win10config.display_name = policy.name
        win10config.description = ""

        if policy.description is not None:
            win10config.description = ""


        oma_settings = []
        
        for setting in policy.settings:
            
            setting_value = setting.get_value()
            setting_oma_uri = setting.get_oma_uri()
            setting_type = setting.get_data_type()
            
            if setting_type == Setting.OMA_URI_Integer_DataType:
                oma_uri_setting = OmaSettingInteger()
                
            elif setting_type == Setting.OMA_URI_String_DataType:
                oma_uri_setting = OmaSettingString()
                
            oma_uri_setting.oma_uri = setting_oma_uri
            oma_uri_setting.value = setting_value
            oma_uri_setting.display_name = setting.name
            
            
            oma_settings.append(oma_uri_setting)
            logger.debug("Deploying setting "+str(setting.name))
            
            
            
        for group in policy.groups:

            setting = OmaSettingStringXml()

            description = ""
            if group.description is not None:
                description = group.description

            setting.value = str(group).encode("utf-8")
            setting.file_name = group.name+".xml"
            setting.display_name = group.name
            setting.description = description
            setting.oma_uri = group.get_oma_uri()

            oma_settings.append(setting)

        for rule in policy.rules:

            setting = OmaSettingStringXml()

            description = ""
            if rule.description is not None:
                description = rule.description

            setting.value = str(rule).encode("utf-8")
            setting.file_name = rule.name+".xml"
            setting.display_name = rule.name
            setting.description = description
            setting.oma_uri = rule.get_oma_uri()

            oma_settings.append(setting)


            
        win10config.oma_settings = oma_settings

        results = Package.IntuneResults(operation,metadata_policy_policy)
        

        if operation == "new":
            result = await graph.create_device_configuration(win10config)
        else:
            result = await graph.update_device_configuration(win10config,metadata_policy_policy["id"])

        results.setResultForPolicy(result)
        return results
        
    
    async def deployDCV2Policy(self,graph,policy,operation="new",metadata_policy_policy=None):
        logger.debug("operation="+operation)

        metadata = self.metadata
        results = Package.IntuneResults(operation,metadata_policy_policy)

        
        groups_map = {

        }

        groups = policy.groups
        for group in groups:

            metadata_for_group = self.metadata.getMetadataForGroup(policy.name,group.name)
            if "id" in metadata_for_group:
                logger.debug("Setting metadata_id to "+str(metadata_for_group["id"]))
                group.__dict__["metadata_id"] = metadata_for_group["id"]

            result = None
            group_operation = None
            if metadata_for_group is None:
                logger.debug("No metadata found for group "+group.name+".  Creating group")
                group_operation = "new"
            else:
                logger.debug("Found metadata for group "+group.name+" metadata="+str(metadata_for_group))
                
                if "id" in metadata_for_group and metadata_for_group["id"] is not None:
                    last_update_str = metadata_for_group["last_update"]
                    #2024-05-14 10:55:06.943441
                    last_update = datetime.fromisoformat(last_update_str)
                    last_update = last_update.replace(microsecond=0)
        

                    group_file_name = self.getFileForGroup(policy,group)
                    #Tue May 14 10:54:58 2024
                    file_last_update=datetime.strptime(time.ctime(os.path.getmtime(group_file_name)),"%c")
                    logger.debug("package last update="+str(last_update)+" file_last_update="+str(file_last_update))

                    if file_last_update >= last_update:
                        logger.info(group_file_name+" has been updated")
                        group_operation = "update"
                    

                    groups_map[metadata_for_group["groupdata_id"]] = metadata_for_group["id"]
                else:
                    logger.debug("No id found for "+group.name+".  Creatining group")
                    group_operation = "new"

            if group_operation is not None:

                logger.debug("Creating a reusable setting for "+str(group))
                group_setting = DeviceControlPolicyTemplate.DeviceControlGroup.createSettingFromGroup(group)
                logger.debug("Setting="+str(group_setting))

                if group_operation == "new":
                    result = await graph.create_group_v2(group_setting,group.name)
                elif group_operation == "update":
                    result = await graph.update_group_v2(group_setting,group.name,metadata_for_group["id"])

                logger.debug("Result="+str(result))
                if result is not None and result.__class__.__name__ == "DeviceManagementReusablePolicySetting":
                    groups_map[group.id] = result.id
                    logger.debug("Adding result for "+group.name)
                    results.addResultForGroup(result,group)
                elif result is None:
                    if group_operation == "update":
                        results.addResultForGroup(Package.IntuneResults.UpdateApplied(metadata_for_group["id"]),group)
                    else:
                        logger.debug("No results for "+group.name)
                else:
                    logger.warning("Unexpected result class "+result.__class__.__name__+" for group "+group.name)

        
        rule_settings = []
        any_rule_changes = False
        for rule in policy.rules:

            metadata_for_rule = self.metadata.getMetadataForRule(policy.name,rule.name)

            if metadata_for_rule is None:
                any_rule_changes = True
            else:
                logger.debug("Found metadata for rule rule_name="+rule.name)

            rule_setting = DeviceControlPolicyTemplate.DeviceControlRule.createSettingsFromRule(rule,groups_map)
            logger.debug("Setting="+str(rule_setting))
            rule_settings.append(rule_setting)

        result = Package.IntuneResults.NoChangesNeeded(policy.id)

        #Handle the case where the package has no rules
        if (any_rule_changes or operation == "new") and len(rule_settings) > 0:
            result = await graph.create_policy_v2(policy.name, policy.description,rule_settings)
            logger.debug("Result="+str(result))

        results.setResultForPolicy(result)
            

        return results
    
    def setSource(self,sourcePath):
        self.source_path = sourcePath


    def getFileForGroup(self,policy,group):

        policies_json = self.package_json["policies"]
        policy_json = policies_json[policy.name]
        group_json = policy_json["groups"][group.name]

        group_path = group_json["file"]["path"]

        logger.debug("policy="+policy.name+" group="+group.name+" file="+group_path)

        return group_path


class PolicyFilter:

    def __init__(self, included_policies = None, versions = None, os=None):
        self.included_policies = included_policies
        self.os = os
        self.versions = versions      

def client_id_type(value):
    return value

def tenant_id_type(value):
    return value

def dir_type(path):
    if os.path.isdir(path):
        return path
    else:
        raise NotADirectoryError(path)
    
def path_array(path):
    paths = []
    path_strs = str.split(path,os.pathsep)
    for path_str in path_strs:
        
        path = pathlib.Path(path_str)
        if path.is_absolute():
            paths.append(path)
        else:
            parent_path = pathlib.Path(__file__ ).parent.resolve() 
            path = pathlib.Path(str(parent_path)+ os.sep + path_str).resolve()
            paths.append(path)

    return paths

def file(path):
    if os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentError(None,"Not a file "+path)

async def display_access_token(graph: Graph):
    logger.debug("Display access token")
    token = await graph.get_app_only_token()
    logger.debug("App-only token: "+str(token))

async def main():
    
    arg_parser = argparse.ArgumentParser(
    description='Utility for importing and exporting device control settings to/from Intune.')

    arg_parser.add_argument('-t', '--tenantId', type=tenant_id_type, dest="tenantId", help='tenantId for the tenant',required=True)
    arg_parser.add_argument('-c', '--clientId', type=client_id_type, dest="clientId", help='clientId of the application',required=True)
    arg_parser.add_argument('-s', '--clientSecret', dest="clientSecret", help='clientSecret of the application',required=True)
    arg_parser.add_argument('-l','--loggingConf', type=file,dest="loggingConf",help="path to the logging.conf",default="logging.conf")

    subparsers = arg_parser.add_subparsers(help='sub-command help')
    parser_export = subparsers.add_parser('export', help='export help')
    parser_export.add_argument("command",action="store_const",const="export")
    parser_export.add_argument('-d','--dest',dest="dest",type=dir_type,help="The output directory.  Defaults to current working directory.",default=".")
    parser_export.add_argument('-n','--name',dest="package_name",help="The name of the package")
    parser_export.add_argument('-t','--template',dest="template",help="Jinja2 template to use to generate output.  Defaults to dcutil.j2.",default="dcutil.j2")
    parser_export.add_argument('-rt','--readme_template',dest="readme_template",help="Jinja2 template to use for the readme.  Defaults to readme.j2.",default="readme.j2")
    parser_export.add_argument('-dt','--description_template',dest="description_template",help="Jinja2 template to use for the description.  Defaults to description.j2.",default="description.j2")
    parser_export.add_argument('-r','--readme',dest="readme_file",help="The readme file to generate.  Defaults to readme.md.",default="readme.md")
    parser_export.add_argument('-tp','--templates_path',dest="templates_path",help="path to Jinja2 templates.  Defaults to templates.",default="templates",type=path_array)
    
   

    parser_import = subparsers.add_parser('import', help='export help')
    parser_import.add_argument("command",action="store_const",const="import")
    


    args = arg_parser.parse_args()
    process_args(args)


async def process_args(args):

    import logging.config
    logging.config.fileConfig(args.loggingConf)


    graph: Graph = Graph(args.tenantId,args.clientId,args.clientSecret)

    await display_access_token(graph)
    
    try:
        if args.command == "export":

            templateLoader = jinja2.FileSystemLoader(searchpath=args.templates_path)
            templateEnv = jinja2.Environment(loader=templateLoader)

            logger.info("Exporting package "+args.package_name+" from tenantId "+args.tenantId+" to "+args.dest)

            logger.debug("description_template="+args.description_template)


            await export(graph,args.dest,args.package_name,
                         templateEnv,
                         args.template,
                         args.readme_template,
                         args.description_template)
        
        elif not hasattr("command",args):
            logging.warning("No command")
        else:
            logging.warning("Unknown command "+args.command)
            
    except ODataError as odata_error:
        logger.error('Error:')
        if odata_error.error:
            logger.error("Code: " + odata_error.error.code + "Message: " + odata_error.error.message)
            full_stack()
        else:
            logger.error("ODataError "+str(odata_error))
            full_stack()



async def export(graph: Graph, destination,name, 
                 templateEnv, 
                 rule_template="dcutil.j2",
                 readme_template="readme.j2",
                 description_template="description.j2",
                 policy_filter = None):

    package = Package(name,templateEnv)

    dc_policy_template = await DeviceControlPolicyTemplate.getTemplate(graph)
    dc_policies = await dc_policy_template.getPolicies(policy_filter)
    for dc_policy in dc_policies:
        package.addPolicy(dc_policy)
    
    configs = await graph.export_device_configurations(policy_filter)

    logger.info("v1 policies retrieved="+str(len(configs.value))+" policies.")
       
    for device_config in configs.value:
        if device_config.odata_type == "#microsoft.graph.macOSCustomConfiguration":
            payload_bytes = device_config.payload
            payload = base64.b64decode(payload_bytes)
            plist = plistlib.loads(payload,fmt=plistlib.FMT_XML)
            if 'deviceControl' in plist['PayloadContent'][0]:

                policy = Package.Policy(graph)

                id = device_config.id

                
                policy.os = Package.MAC_OS
                policy.id = id
                policy.name = device_config.display_name
                policy.description = device_config.description

                deviceControl = plist['PayloadContent'][0]['deviceControl']
                
                policy.setPayload(deviceControl['policy'])

                assignments = await graph.get_assignments_for_configuration(id)

                await policy.setAssignments(assignments)

                logger.info("Retrieved policy name="+policy.name+" id="+policy.id)
                package.addPolicy(policy)

        if device_config.odata_type == "#microsoft.graph.windows10CustomConfiguration":
            
            policy = Package.Policy(graph)

            id = device_config.id

            policy.id = id
            policy.name = device_config.display_name
            policy.description = device_config.description

            
            assignments = await graph.get_assignments_for_configuration(id)

            await policy.setAssignments(assignments)


            for oma_setting in device_config.oma_settings:
                
                name = oma_setting.display_name
                description = oma_setting.description
                oma_uri = oma_setting.oma_uri

                
                if oma_setting.odata_type == "#microsoft.graph.omaSettingStringXml":
                    secret_reference_value_id = oma_setting.secret_reference_value_id
                    xml = await graph.get_xml(id,secret_reference_value_id)
                    root = ET.fromstring(xml.value)

                    #logger.debug("xml="+str(xml.value))
                    

                    #file name without .xml
                    name = str(oma_setting.file_name).split(".")[0]
                    if root.tag == "PolicyRule":
                        try:
                            rule = dc.PolicyRule(root,dc.Format.OMA_URI)
                            policy.addRule(rule)
                            policy.name = name
                            policy.description = description
                        except RuntimeError as e:
                            logger.error("Error loading policy rule from xml: "+str(e))

                    elif root.tag == "Group":
                        try:
                            group = dc.Group(root,dc.Format.OMA_URI)
                            policy.addGroup(group)
                            group.name = name
                            group.description = description
                        except RuntimeError as e:
                            logger.error("Error loading group from xml: "+str(e))
                else:
                    dc_setting_name = dc.Setting.getSettingNameFor(oma_uri)
                    if dc_setting_name is not None:
                        setting_value = oma_setting.value
                        dc_setting = dc.Setting(dc_setting_name,setting_value)
                        intune_settings = Package.IntuneSetting(dc_setting,oma_setting.display_name,description)
                        policy.addSetting(intune_settings)

            logger.info("Retrieved policy name="+policy.name+" id="+policy.id)

            package.addPolicy(policy)
    

    package.save(destination,rule_template,readme_template,description_template)


    package.metadata.metadata["source"] = {
        "intune":{
            
        }
    }

    if policy_filter is not None and policy_filter.included_policies is not None:
        package.metadata.metadata["source"]["intune"]["policies"] = policy_filter.included_policies

    package.save_metadata()

if __name__ == '__main__':
    # Run main
    asyncio.run(main())
