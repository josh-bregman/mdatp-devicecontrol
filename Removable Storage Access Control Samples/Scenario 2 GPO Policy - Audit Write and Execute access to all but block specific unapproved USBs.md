# Device control policy sample: Scenario 2

Description: A sample policy

A device control policy is a combination of [policy rules](#policy-rules) and [groups](#groups).  
This sample is based on the [sample files](#files).  
To configure the sample, follow the [deployment instructions](#deployment-instructions).  

## Policy Rules
<table>
    <tr>
        <th rowspan="2" valign="top">Name</th>
        <th rowspan="2" valign="top">Devices</th>
        <th rowspan="2" valign="top">Excluding</th>
        <th rowspan="2" valign="top">Rule Type</th>
        <th colspan="7" valign="top"><center>Access</center></th>
        <th rowspan="2" valign="top">Notification</th>
        <th rowspan="2" valign="top">User SID</th>
        <th rowspan="2" valign="top">Conditions</th>
    </tr>
    <tr>
		<th>Disk Read</th>
		<th>Disk Write</th>
		<th>Disk Execute</th>
		<th>File Read</th>
		<th>File Write</th>
		<th>File Execute</th>
		<th>Print</th>
	</tr><tr>
            <td rowspan="2"><b>Block Write and Execute access to all but block specific unapproved USBs</b></td>
            <td rowspan="2 valign="top">
                <ul><li>Approved USBs Group_0<a href="#approved-usbs-group_0" title="MatchAny [{'InstancePathId': 'USBSTOR\\DISK&VEN__USB&PROD__SANDISK_3.2GEN1&REV_1.00\\03003324080520232521&*'}]"> (details)</a></ul>
            </td>
            <td rowspan="2" valign="top">
                <ul></ul>
            </td>
            <td>Deny</td>
            <td>-</td>
            <td>:x:</td>
            <td>:x:</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>None (0)</td> 
            <td>All Users</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr><tr>
            <td>Audit Denied</td>
            <td>-</td>
            <td>:page_facing_up:</td>
            <td>:page_facing_up:</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>Show notification and Send event (3)</td>
            <td>All Users</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr><tr>
            <td rowspan="1"><b>Audit Write and Execute access to others</b></td>
            <td rowspan="1 valign="top">
                <ul><li>Any Removable Storage and CD-DVD and WPD Group_1<a href="#any-removable-storage-and-cd-dvd-and-wpd-group_1" title="MatchAny [{'PrimaryId': 'RemovableMediaDevices'}, {'PrimaryId': 'CdRomDevices'}, {'PrimaryId': 'WpdDevices'}]"> (details)</a></ul>
            </td>
            <td rowspan="1" valign="top">
                <ul><li>Approved USBs Group_0<a href="#approved-usbs-group_0" title="MatchAny [{'InstancePathId': 'USBSTOR\\DISK&VEN__USB&PROD__SANDISK_3.2GEN1&REV_1.00\\03003324080520232521&*'}]"> (details)</a></ul>
            </td>
            <td>Audit Allowed</td>
            <td>-</td>
            <td>:page_facing_up:</td>
            <td>:page_facing_up:</td>
            <td>-</td>
            <td>:page_facing_up:</td>
            <td>:page_facing_up:</td>
            <td>-</td>
            <td>Send event (2)</td> 
            <td>All Users</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr></table>

## Groups


### Approved USBs Group_0

This is a group of type *Device*. 
The match type for the group is *MatchAny*.

|  Property | Value |
|-----------|-------|
| InstancePathId | USBSTOR\DISK&VEN__USB&PROD__SANDISK_3.2GEN1&REV_1.00\03003324080520232521&* |

<details>
<summary>View XML</summary>

```xml
<Group Id="{65fa649a-a111-4912-9294-fb6337a25038}" Type="Device">
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B65fa649a-a111-4912-9294-fb6337a25038%7D/GroupData -->
	<Name>Approved USBs Group_0</Name>
	<MatchType>MatchAny</MatchType>
	<DescriptorIdList>
		<InstancePathId>USBSTOR\DISK&amp;VEN__USB&amp;PROD__SANDISK_3.2GEN1&amp;REV_1.00\03003324080520232521&amp;*</InstancePathId>
	</DescriptorIdList>
</Group>
```
</details>

### Any Removable Storage and CD-DVD and WPD Group_1

This is a group of type *Device*. 
The match type for the group is *MatchAny*.

|  Property | Value |
|-----------|-------|
| PrimaryId | RemovableMediaDevices |
| PrimaryId | CdRomDevices |
| PrimaryId | WpdDevices |

<details>
<summary>View XML</summary>

```xml
<Group Id="{9b28fae8-72f7-4267-a1a5-685f747a7146}" Type="Device">
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B9b28fae8-72f7-4267-a1a5-685f747a7146%7D/GroupData -->
	<Name>Any Removable Storage and CD-DVD and WPD Group_1</Name>
	<MatchType>MatchAny</MatchType>
	<DescriptorIdList>
		<PrimaryId>RemovableMediaDevices</PrimaryId>
		<PrimaryId>CdRomDevices</PrimaryId>
		<PrimaryId>WpdDevices</PrimaryId>
	</DescriptorIdList>
</Group>
```
</details>


## Files
This policy is based on information in the following files:

- [Group Policy/Any Removable Storage and CD-DVD and WPD Group.xml](Group%20Policy/Any%20Removable%20Storage%20and%20CD-DVD%20and%20WPD%20Group.xml)
- [Group Policy/Scenario 2 GPO Policy - Audit Write and Execute access to all but block specific unapproved USBs.xml](Group%20Policy/Scenario%202%20GPO%20Policy%20-%20Audit%20Write%20and%20Execute%20access%20to%20all%20but%20block%20specific%20unapproved%20USBs.xml)
- [Intune OMA-URI/Approved USBs Group.xml](Intune%20OMA-URI/Approved%20USBs%20Group.xml)


# Deployment Instructions

Device control [policy rules](#policy-rules) and [groups](#groups) can be deployed through the following management tools:

## Windows
- [Intune UX](#intune-ux)
- [Intune Custom Settings](#intune-custom-settings)
- [Group Policy (GPO)](#group-policy-gpo)

## Mac
- [Mac Policy](#mac-policy)

## Intune UX

Intune UX is not supported for this policy because:
- File Execute (32) is an unsupported access mask
- File Write (16) is an unsupported access mask

Use [Intune custom settings](#intune-custom-settings) to deploy the policy instead.


## Group Policy (GPO)
<details>
<summary>Define device control policy groups</summary>

   1. Go to Computer Configuration > Administrative Templates > Windows Components > Microsoft Defender Antivirus > Device Control > Define device control policy groups.
   2. Save the XML below to a network share.
```xml
<Groups>
	<Group Id="{65fa649a-a111-4912-9294-fb6337a25038}" Type="Device">
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B65fa649a-a111-4912-9294-fb6337a25038%7D/GroupData -->
		<Name>Approved USBs Group_0</Name>
		<MatchType>MatchAny</MatchType>
		<DescriptorIdList>
			<InstancePathId>USBSTOR\DISK&amp;VEN__USB&amp;PROD__SANDISK_3.2GEN1&amp;REV_1.00\03003324080520232521&amp;*</InstancePathId>
		</DescriptorIdList>
	</Group>
	<Group Id="{9b28fae8-72f7-4267-a1a5-685f747a7146}" Type="Device">
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B9b28fae8-72f7-4267-a1a5-685f747a7146%7D/GroupData -->
		<Name>Any Removable Storage and CD-DVD and WPD Group_1</Name>
		<MatchType>MatchAny</MatchType>
		<DescriptorIdList>
			<PrimaryId>RemovableMediaDevices</PrimaryId>
			<PrimaryId>CdRomDevices</PrimaryId>
			<PrimaryId>WpdDevices</PrimaryId>
		</DescriptorIdList>
	</Group>
</Groups>
```
   3. In the Define device control policy groups window, select *Enabled* and specify the network share file path containing the XML groups data.
</details>

<details>
<summary>Define device control policy rules</summary>
 
  1. Go to Computer Configuration > Administrative Templates > Windows Components > Microsoft Defender Antivirus > Device Control > Define device control policy rules.
  2. Save the XML below to a network share.
```xml
<PolicyRules>
	<PolicyRule Id="{23b8e437-66ac-4b32-b3d7-24044637fc98}" >
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B23b8e437-66ac-4b32-b3d7-24044637fc98%7D/RuleData -->
		<Name>Block Write and Execute access to all but block specific unapproved USBs</Name>
		<IncludedIdList>
			<GroupId>{65fa649a-a111-4912-9294-fb6337a25038}</GroupId>
		</IncludedIdList>
		<ExcludedIdList>
		</ExcludedIdList>
		<Entry Id="{5fbf7a77-0e50-456a-bb25-1b60e1b9b288}">
			<Type>Deny</Type>
			<AccessMask>6</AccessMask>
			<Options>0</Options>
		</Entry>
		<Entry Id="{e1caaa4e-7bd1-4812-bec0-5a5973cb88f4}">
			<Type>AuditDenied</Type>
			<AccessMask>6</AccessMask>
			<Options>3</Options>
		</Entry>
	</PolicyRule>
	<PolicyRule Id="{b58ab853-9a6f-405c-a194-740e69422b48}" >
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7Bb58ab853-9a6f-405c-a194-740e69422b48%7D/RuleData -->
		<Name>Audit Write and Execute access to others</Name>
		<IncludedIdList>
			<GroupId>{9b28fae8-72f7-4267-a1a5-685f747a7146}</GroupId>
		</IncludedIdList>
		<ExcludedIdList>
			<GroupId>{65fa649a-a111-4912-9294-fb6337a25038}</GroupId>
		</ExcludedIdList>
		<Entry Id="{979701d8-584a-4f27-8b68-2ecca59ccabd}">
			<Type>AuditAllowed</Type>
			<AccessMask>54</AccessMask>
			<Options>2</Options>
		</Entry>
	</PolicyRule>
</PolicyRules>
```
  3. In the Define device control policy rules window, select *Enabled*, and enter the network share file path containing the XML rules data.
</details>

## Intune Custom Settings

<details>
<summary>Create custom intune configuration</summary>

   1. Navigate to Devices > Configuration profiles
   2. Click Create (New Policy)
   3. Select Platform "Windows 10 and Later"
   4. Select Profile "Templates"
   5. Select Template Name "Custom"
   6. Click "Create"
   7. Under Name, enter **
   8. Optionally, enter a description
   9. Click "Next" 
</details>
<details>
<summary>Add a row for Block Write and Execute access to all but block specific unapproved USBs</summary>  
   
   1. Click "Add"
   2. For Name, enter *Block Write and Execute access to all but block specific unapproved USBs*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B23b8e437-66ac-4b32-b3d7-24044637fc98%7D/RuleData*
   5. For Data type, select *String (XML File)*
   
        
   6. Save this XML to a file. 
   ```xml
   <PolicyRule Id="{23b8e437-66ac-4b32-b3d7-24044637fc98}" >
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B23b8e437-66ac-4b32-b3d7-24044637fc98%7D/RuleData -->
	<Name>Block Write and Execute access to all but block specific unapproved USBs</Name>
	<IncludedIdList>
		<GroupId>{65fa649a-a111-4912-9294-fb6337a25038}</GroupId>
	</IncludedIdList>
	<ExcludedIdList>
	</ExcludedIdList>
	<Entry Id="{5fbf7a77-0e50-456a-bb25-1b60e1b9b288}">
		<Type>Deny</Type>
		<AccessMask>6</AccessMask>
		<Options>0</Options>
	</Entry>
	<Entry Id="{e1caaa4e-7bd1-4812-bec0-5a5973cb88f4}">
		<Type>AuditDenied</Type>
		<AccessMask>6</AccessMask>
		<Options>3</Options>
	</Entry>
</PolicyRule>
   ```
   
   7. For Custom XML, select the file.
         
   
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for Audit Write and Execute access to others</summary>  
   
   1. Click "Add"
   2. For Name, enter *Audit Write and Execute access to others*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7Bb58ab853-9a6f-405c-a194-740e69422b48%7D/RuleData*
   5. For Data type, select *String (XML File)*
   
        
   6. Save this XML to a file. 
   ```xml
   <PolicyRule Id="{b58ab853-9a6f-405c-a194-740e69422b48}" >
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7Bb58ab853-9a6f-405c-a194-740e69422b48%7D/RuleData -->
	<Name>Audit Write and Execute access to others</Name>
	<IncludedIdList>
		<GroupId>{9b28fae8-72f7-4267-a1a5-685f747a7146}</GroupId>
	</IncludedIdList>
	<ExcludedIdList>
		<GroupId>{65fa649a-a111-4912-9294-fb6337a25038}</GroupId>
	</ExcludedIdList>
	<Entry Id="{979701d8-584a-4f27-8b68-2ecca59ccabd}">
		<Type>AuditAllowed</Type>
		<AccessMask>54</AccessMask>
		<Options>2</Options>
	</Entry>
</PolicyRule>
   ```
   
   7. For Custom XML, select the file.
         
   
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for Approved USBs Group_0</summary>  
   
   1. Click "Add"
   2. For Name, enter *Approved USBs Group_0*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B65fa649a-a111-4912-9294-fb6337a25038%7D/GroupData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *.\Intune OMA-URI\Approved USBs Group.xml*
         
   
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for Any Removable Storage and CD-DVD and WPD Group_0</summary>  
   
   1. Click "Add"
   2. For Name, enter *Any Removable Storage and CD-DVD and WPD Group_0*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B9b28fae8-72f7-4267-a1a5-685f747a7146%7D/GroupData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *.\Intune OMA-URI\Any Removable Storage and CD-DVD and WPD Group.xml*
         
   
   
   7. Click "Save"
</details>


## Mac Policy

This policy is not supported on Mac because Unsupported Descriptor ID InstancePathId

Learn more
- [Mac device control examples](../Removable%20Storage%20Access%20Control%20Samples/macOS/policy/examples/README.md)
