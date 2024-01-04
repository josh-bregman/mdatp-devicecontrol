# Device control policy sample: Block Read and Write access to specific file _Policy

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
            <td rowspan="2"><b>Block Read and Write access to specific file</b></td>
            <td rowspan="2 valign="top">
                <ul><li>Any Removable Storage and CD-DVD and WPD Group_1<a href="#any-removable-storage-and-cd-dvd-and-wpd-group_1" title="MatchAny [{'PrimaryId': 'RemovableMediaDevices'}, {'PrimaryId': 'CdRomDevices'}, {'PrimaryId': 'WpdDevices'}]"> (details)</a></ul>
            </td>
            <td rowspan="2" valign="top">
                <ul></ul>
            </td>
            <td>Deny</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>:x:</td>
            <td>-</td>
            <td>:x:</td>
            <td>-</td>
            <td>None (0)</td> 
            <td>All Users</td>
            <td>MatchAll
                <ul><li> MatchAny 
                        <ul><li>Block Read and Write access to specific file _Groups_2<a href="#block-read-and-write-access-to-specific-file-_groups_2" title="MatchAny [{'PathId': '*.exe'}, {'PathId': '*.dll'}]"> (details)</a></ul>
                </ul>
            </td>
        </tr><tr>
            <td>Audit Denied</td>
            <td>:page_facing_up:</td>
            <td>:page_facing_up:</td>
            <td>:page_facing_up:</td>
            <td>:page_facing_up:</td>
            <td>:page_facing_up:</td>
            <td>:page_facing_up:</td>
            <td>-</td>
            <td>Show notification and Send event (3)</td>
            <td>All Users</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr></table>

## Groups


### Block Read and Write access to specific file _Groups_2

This is a group of type *File*. 
The match type for the group is *MatchAny*.

|  Property | Value |
|-----------|-------|
| PathId | *.exe |
| PathId | *.dll |

<details>
<summary>View XML</summary>

```xml
<Group Id="{e5f619a7-5c58-4927-90cd-75da2348a30f}" Type="File">
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7Be5f619a7-5c58-4927-90cd-75da2348a30f%7D/GroupData -->
	<Name>Block Read and Write access to specific file _Groups_2</Name>
	<MatchType>MatchAny</MatchType>
	<DescriptorIdList>
		<PathId>*.exe</PathId>
		<PathId>*.dll</PathId>
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

- [Group Policy/Block Read and Write access to specific file _Groups.xml](Group%20Policy/Block%20Read%20and%20Write%20access%20to%20specific%20file%20_Groups.xml)
- [Group Policy/Any Removable Storage and CD-DVD and WPD Group.xml](Group%20Policy/Any%20Removable%20Storage%20and%20CD-DVD%20and%20WPD%20Group.xml)
- [Group Policy/Block Read and Write access to specific file _Policy.xml](Group%20Policy/Block%20Read%20and%20Write%20access%20to%20specific%20file%20_Policy.xml)


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
- Parameters are not supported
- File Execute (32) is an unsupported access mask
- File groups not supported.
- File Write (16) is an unsupported access mask
- File Read (8) is an unsupported access mask

Use [Intune custom settings](#intune-custom-settings) to deploy the policy instead.


## Group Policy (GPO)
<details>
<summary>Define device control policy groups</summary>

   1. Go to Computer Configuration > Administrative Templates > Windows Components > Microsoft Defender Antivirus > Device Control > Define device control policy groups.
   2. Save the XML below to a network share.
```xml
<Groups>
	<Group Id="{e5f619a7-5c58-4927-90cd-75da2348a30f}" Type="File">
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7Be5f619a7-5c58-4927-90cd-75da2348a30f%7D/GroupData -->
		<Name>Block Read and Write access to specific file _Groups_2</Name>
		<MatchType>MatchAny</MatchType>
		<DescriptorIdList>
			<PathId>*.exe</PathId>
			<PathId>*.dll</PathId>
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
	<PolicyRule Id="{5038638c-9352-47bb-88df-8a659f0c02a7}" >
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B5038638c-9352-47bb-88df-8a659f0c02a7%7D/RuleData -->
		<Name>Block Read and Write access to specific file</Name>
		<IncludedIdList>
			<GroupId>{9b28fae8-72f7-4267-a1a5-685f747a7146}</GroupId>
		</IncludedIdList>
		<ExcludedIdList>
		</ExcludedIdList>
		<Entry Id="{1ecfdafb-9b7f-4b66-b3c5-f1d872b0961d}">
			<Type>Deny</Type>
			<AccessMask>40</AccessMask>
			<Options>0</Options>
			<Parameters MatchType="MatchAll">
				<File MatchType="MatchAny">
					<GroupId>{e5f619a7-5c58-4927-90cd-75da2348a30f}</GroupId>
				</File>
			</Parameters>
		</Entry>
		<Entry Id="{2925ecd8-40dc-42bb-a972-da0de839dd4f}">
			<Type>AuditDenied</Type>
			<AccessMask>63</AccessMask>
			<Options>3</Options>
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
<summary>Add a row for Block Read and Write access to specific file</summary>  
   
   1. Click "Add"
   2. For Name, enter *Block Read and Write access to specific file*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B5038638c-9352-47bb-88df-8a659f0c02a7%7D/RuleData*
   5. For Data type, select *String (XML File)*
   
        
   6. Save this XML to a file. 
   ```xml
   <PolicyRule Id="{5038638c-9352-47bb-88df-8a659f0c02a7}" >
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B5038638c-9352-47bb-88df-8a659f0c02a7%7D/RuleData -->
	<Name>Block Read and Write access to specific file</Name>
	<IncludedIdList>
		<GroupId>{9b28fae8-72f7-4267-a1a5-685f747a7146}</GroupId>
	</IncludedIdList>
	<ExcludedIdList>
	</ExcludedIdList>
	<Entry Id="{1ecfdafb-9b7f-4b66-b3c5-f1d872b0961d}">
		<Type>Deny</Type>
		<AccessMask>40</AccessMask>
		<Options>0</Options>
		<Parameters MatchType="MatchAll">
			<File MatchType="MatchAny">
				<GroupId>{e5f619a7-5c58-4927-90cd-75da2348a30f}</GroupId>
			</File>
		</Parameters>
	</Entry>
	<Entry Id="{2925ecd8-40dc-42bb-a972-da0de839dd4f}">
		<Type>AuditDenied</Type>
		<AccessMask>63</AccessMask>
		<Options>3</Options>
	</Entry>
</PolicyRule>
   ```
   
   7. For Custom XML, select the file.
         
   
   
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
<details>
<summary>Add a row for Unauthorized File Group_0</summary>  
   
   1. Click "Add"
   2. For Name, enter *Unauthorized File Group_0*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7Be5f619a7-5c58-4927-90cd-75da2348a30f%7D/GroupData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *.\Intune OMA-URI\Unauthorized File Group.xml*
         
   
   
   7. Click "Save"
</details>


## Mac Policy

This policy is not supported on Mac because Unsupported Descriptor ID PathId

Learn more
- [Mac device control examples](../Removable%20Storage%20Access%20Control%20Samples/macOS/policy/examples/README.md)
