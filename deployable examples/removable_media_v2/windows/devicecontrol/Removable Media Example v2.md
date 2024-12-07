# Device control policy sample: Removable Media Example v2

**Description:** A policy              
**Device Type:** Windows Removable Device

A device control policy is a combination of [policy rules](#policy-rules), [groups](#groups) and [settings](#settings).  
This sample is based on the [sample files](#files).  
To configure the sample, follow the [deployment instructions](#deployment-instructions).  

## Policy Rules


<table>
    <tr>
        <th rowspan="2" valign="top">Name</th>
        <th colspan="2" valign="top"><center>Devices</center></th>
        <th rowspan="2" valign="top">Rule Type</th>
        <th colspan="6" valign="top"><center>Access</center></th>
        <th rowspan="2" valign="top">Notification</th>
        <th rowspan="2" valign="top">Conditions</th>
    </tr>
    <tr>
        <th>Included</th>
        <th>Excluded</th>
        <th>Disk Read</th>
		<th>Disk Write</th>
		<th>Disk Execute</th>
		<th>File Read</th>
		<th>File Write</th>
		<th>File Execute</th></tr><tr>
            <td rowspan="2" valign="top"><b>Deny access to all non-approved devices</b></td>
            <td rowspan="2 valign="top">
                <ul><li>Group: All Removable Media Devices<a href="#all-removable-media-devices" title="MatchAll {'PrimaryId': 'RemovableMediaDevices'}"> (details)</a>  
</ul>
            </td>
            <td rowspan="2" valign="top">
                <ul><li>Group: Allowed USBs<a href="#allowed-usbs" title="MatchAll {'SerialNumberId': '6EA9150055800605'}"> (details)</a>  
</ul>
            </td>
            <td>Deny</td>
            <td>:x:</td>
            <td>:x:</td>
            <td>:x:</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>None (0)</td> 
            <td>
                <center>-</center></td>
        </tr><tr>
            <td>Audit Denied</td>
            <td>:page_facing_up:</td>
            <td>:page_facing_up:</td>
            <td>:page_facing_up:</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>Show notification and Send event (3)</td>
            <td> 
                <center>-</center></td>
        </tr><tr>
            <td rowspan="2" valign="top"><b>Allow access to allowed USBs</b></td>
            <td rowspan="2 valign="top">
                <ul><li>Group: Allowed USBs<a href="#allowed-usbs" title="MatchAll {'SerialNumberId': '6EA9150055800605'}"> (details)</a>  
</ul>
            </td>
            <td rowspan="2" valign="top">
                <ul></ul>
            </td>
            <td>Allow</td>
            <td>:white_check_mark:</td>
            <td>:white_check_mark:</td>
            <td>:white_check_mark:</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>None (0)</td> 
            <td>
                <center>-</center></td>
        </tr><tr>
            <td>Audit Allowed</td>
            <td>-</td>
            <td>:page_facing_up:</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>Send event (2)</td>
            <td> 
                <center>-</center></td>
        </tr></table>


## Groups


### All Removable Media Devices



This is a group of type *Device*. 
The match type for the group is *MatchAll*.


|  Property | Value |
|-----------|-------|
| PrimaryId | RemovableMediaDevices |





<details>
<summary>View XML</summary>

```xml
<Group Id="{b7e99129-3e3c-44aa-b71e-f95e3f65336f}" Type="Device">
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7Bb7e99129-3e3c-44aa-b71e-f95e3f65336f%7D/GroupData -->
	<Name>All Removable Media Devices</Name>
	<MatchType>MatchAll</MatchType>
	<DescriptorIdList>
		<!--Windows Device Family(RemovableMediaDevices)-->
		<PrimaryId>RemovableMediaDevices</PrimaryId>
	</DescriptorIdList>
</Group>
```
</details>

### Allowed USBs



This is a group of type *Device*. 
The match type for the group is *MatchAll*.


|  Property | Value |
|-----------|-------|
| SerialNumberId | 6EA9150055800605 |





<details>
<summary>View XML</summary>

```xml
<Group Id="{5e233630-f613-483a-92d9-290d44b84ca2}" Type="Device">
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B5e233630-f613-483a-92d9-290d44b84ca2%7D/GroupData -->
	<Name>Allowed USBs</Name>
	<MatchType>MatchAll</MatchType>
	<DescriptorIdList>
		<!--Windows Device Serial Number(6EA9150055800605)-->
		<SerialNumberId>6EA9150055800605</SerialNumberId>
	</DescriptorIdList>
</Group>
```
</details>


## Settings






| Setting Name |  Setting Value | Description |Documentation |
|--------------|----------------|-------------|---------------|


## Files
This policy is based on information in the following files:

- [groups\All Removable Media Devices.xml](groups%5CAll%20Removable%20Media%20Devices.xml)
- [groups\Allowed USBs.xml](groups%5CAllowed%20USBs.xml)
- [rules\Deny access to all non-approved devices.xml](rules%5CDeny%20access%20to%20all%20non-approved%20devices.xml)
- [rules\Allow access to allowed USBs.xml](rules%5CAllow%20access%20to%20allowed%20USBs.xml)


# Deployment Instructions

Device control [policy rules](#policy-rules) and [groups](#groups) can be deployed through the following management tools:


## Windows
- [Intune UX](#intune-ux)
- [Intune Custom Settings](#intune-custom-settings)
- [Group Policy (GPO)](#group-policy-gpo)





## Intune UX

<details>
<summary>Create a reusable setting for All Removable Media Devices</summary> 

   1. Navigate to Home > Endpoint Security > Attack Surface Reduction
   2. Click on Reusable Settings
   3. Click (+) Add
   4. Enter the *All Removable Media Devices* for the name.  
   5. Optionally, enter a description
   6. Click on "Next"
   
   1. Create an entry for  *PrimaryId* = *RemovableMediaDevices* 
        1. Click (+) Add
        2. Select "Reusable storage"
        3. Click on "Configure setting"    
        4. Enter *PrimaryId( RemovableMediaDevices )* for Name
        5. Enter *RemovableMediaDevices* for PrimaryId
        6. Click "Save"


   
   7. Set the match type drop down to MatchAll
   8. Click "Next"
   9. Click "Add"
</details>
<details>
<summary>Create a reusable setting for Allowed USBs</summary> 

   1. Navigate to Home > Endpoint Security > Attack Surface Reduction
   2. Click on Reusable Settings
   3. Click (+) Add
   4. Enter the *Allowed USBs* for the name.  
   5. Optionally, enter a description
   6. Click on "Next"
   
   1. Create an entry for  *SerialNumberId* = *6EA9150055800605* 
        1. Click (+) Add
        2. Select "Reusable storage"
        3. Click on "Configure setting"    
        4. Enter *SerialNumberId( 6EA9150055800605 )* for Name
        5. Enter *6EA9150055800605* for SerialNumberId
        6. Click "Save"


   
   7. Set the match type drop down to MatchAll
   8. Click "Next"
   9. Click "Add"
</details>
<details>
<summary>Create a Device Control Rules configuration profile</summary>  

   1. Navigate to Home > Endpoint Security > Attack Surface Reduction
   2. Click on "Create Policy"
   3. Under Platform, select "Windows 10 and later"
   4. Under Profile, select "Device Control Rules"
   5. Click "Create"
   6. Under Name, enter **
   7. Optionally, enter a description
   8. Click "Next"
</details>

> [!IMPORTANT]
> This policy has more than 1 rule.  
> Policy ordering is not guaranteed by Intune.
> Make sure that policy is not dependent on order to achieve desired result.
> Consider using ```default deny```.   


<details>
<summary>Add a rule for Deny access to all non-approved devices to the policy</summary>


   1. Click on "+ Set reusable settings" under Included Id

   1. Click on *All Removable Media Devices*

   1. Click on "Select"


   1. Click on "+ Set reusable settings" under Excluded Id

   1. Click on *Allowed USBs*

   1. Click on "Select"

   1. Click on "+ Edit Entry"
   1. Enter *Deny access to all non-approved devices* for the name



   1. Select *Deny* from "Type"
   1. Select *None* from "Options"
   1. Select *Read, Write and Execute* from "Access mask"




   1. Add another entry.  Click on "+ Add"

   1. Select *Audit Denied* from "Type"
   1. Select *Show notification and Send event* from "Options"
   1. Select *Read, Write and Execute* from "Access mask"


   1. Click "OK"
</details>

<details>
<summary>Add a rule for Allow access to allowed USBs to the policy</summary>

   1. Add another rule.  Click on "+ Add"


   1. Click on "+ Set reusable settings" under Included Id

   1. Click on *Allowed USBs*

   1. Click on "Select"


   1. Click on "+ Edit Entry"
   1. Enter *Allow access to allowed USBs* for the name



   1. Select *Allow* from "Type"
   1. Select *None* from "Options"
   1. Select *Read, Write and Execute* from "Access mask"




   1. Add another entry.  Click on "+ Add"

   1. Select *Audit Allowed* from "Type"
   1. Select *Send event* from "Options"
   1. Select *Write* from "Access mask"


   1. Click "OK"
</details>



## Group Policy (GPO)
<details>
<summary>Define device control policy groups</summary>

   1. Go to Computer Configuration > Administrative Templates > Windows Components > Microsoft Defender Antivirus > Device Control > Define device control policy groups.
   2. Save the XML below to a network share.
```xml
<Groups>
	<Group Id="{b7e99129-3e3c-44aa-b71e-f95e3f65336f}" Type="Device">
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7Bb7e99129-3e3c-44aa-b71e-f95e3f65336f%7D/GroupData -->
		<Name>All Removable Media Devices</Name>
		<MatchType>MatchAll</MatchType>
		<DescriptorIdList>
			<!--Windows Device Family(RemovableMediaDevices)-->
			<PrimaryId>RemovableMediaDevices</PrimaryId>
		</DescriptorIdList>
	</Group>
	<Group Id="{5e233630-f613-483a-92d9-290d44b84ca2}" Type="Device">
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B5e233630-f613-483a-92d9-290d44b84ca2%7D/GroupData -->
		<Name>Allowed USBs</Name>
		<MatchType>MatchAll</MatchType>
		<DescriptorIdList>
			<!--Windows Device Serial Number(6EA9150055800605)-->
			<SerialNumberId>6EA9150055800605</SerialNumberId>
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
	<PolicyRule Id="{0632485f-12e0-491a-b9f4-1d8ca7d555a3}" >
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B0632485f-12e0-491a-b9f4-1d8ca7d555a3%7D/RuleData -->
		<Name>Deny access to all non-approved devices</Name>
		<IncludedIdList>
			<GroupId>{b7e99129-3e3c-44aa-b71e-f95e3f65336f}</GroupId>
		</IncludedIdList>
		<ExcludedIdList>
			<GroupId>{5e233630-f613-483a-92d9-290d44b84ca2}</GroupId>
		</ExcludedIdList>
		<Entry Id="{6527e180-415b-4a8f-96ac-c07db4b1267a}">
			<Type>Deny</Type>
			<AccessMask>7</AccessMask>
			<Options>0</Options>
		</Entry>
		<Entry Id="{da890c85-c193-40c8-a065-3e624c09b2c5}">
			<Type>AuditDenied</Type>
			<AccessMask>7</AccessMask>
			<Options>3</Options>
		</Entry>
	</PolicyRule>
	<PolicyRule Id="{6386d325-ae35-470e-b164-2f301dad4ac7}" >
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B6386d325-ae35-470e-b164-2f301dad4ac7%7D/RuleData -->
		<Name>Allow access to allowed USBs</Name>
		<IncludedIdList>
			<GroupId>{5e233630-f613-483a-92d9-290d44b84ca2}</GroupId>
		</IncludedIdList>
		<ExcludedIdList>
		</ExcludedIdList>
		<Entry Id="{b1388e02-42fb-44ed-a4fd-0e4eb97acfe1}">
			<Type>Allow</Type>
			<AccessMask>7</AccessMask>
			<Options>0</Options>
		</Entry>
		<Entry Id="{a2fbaf82-7181-4131-92b2-617678b8b2b7}">
			<Type>AuditAllowed</Type>
			<AccessMask>2</AccessMask>
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
<summary>Add a row for Allow access to allowed USBs</summary>  
   
   1. Click "Add"
   2. For Name, enter *Allow access to allowed USBs*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B6386d325-ae35-470e-b164-2f301dad4ac7%7D/RuleData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *C:\Users\jbreg\OneDrive\Documents\GitHub\mdatp-devicecontrol\deployable examples\removable_media_v2\windows\devicecontrol\rules\Allow access to allowed USBs.xml*
         
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for Deny access to all non-approved devices</summary>  
   
   1. Click "Add"
   2. For Name, enter *Deny access to all non-approved devices*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B0632485f-12e0-491a-b9f4-1d8ca7d555a3%7D/RuleData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *C:\Users\jbreg\OneDrive\Documents\GitHub\mdatp-devicecontrol\deployable examples\removable_media_v2\windows\devicecontrol\rules\Deny access to all non-approved devices.xml*
         
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for All Removable Media Devices</summary>  
   
   1. Click "Add"
   2. For Name, enter *All Removable Media Devices*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7Bb7e99129-3e3c-44aa-b71e-f95e3f65336f%7D/GroupData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *C:\Users\jbreg\OneDrive\Documents\GitHub\mdatp-devicecontrol\deployable examples\removable_media_v2\windows\devicecontrol\groups\All Removable Media Devices.xml*
         
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for Allowed USBs</summary>  
   
   1. Click "Add"
   2. For Name, enter *Allowed USBs*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B5e233630-f613-483a-92d9-290d44b84ca2%7D/GroupData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *C:\Users\jbreg\OneDrive\Documents\GitHub\mdatp-devicecontrol\deployable examples\removable_media_v2\windows\devicecontrol\groups\Allowed USBs.xml*
         
   
   7. Click "Save"
</details>



