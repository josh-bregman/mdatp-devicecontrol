# Device Control Policy: Allow any printer

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
            <td rowspan="1"><b>Default Printer Allow</b></td>
            <td rowspan="1 valign="top">
                <ul><li>Any Printer<a href="#any-printer" title="MatchAny [{'PrimaryId': 'PrinterDevices'}]"> (details)</a></ul>
            </td>
            <td rowspan="1" valign="top">
                <ul></ul>
            </td>
            <td>Allow</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>:white_check_mark:</td>
            <td>Disable (4)</td> 
            <td>All Users</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr></table>

## Groups


### Any Printer

This is a group of type *Device*. 
The match type for the group is *MatchAny*.

|  Property | Value |
|-----------|-------|
| PrimaryId | PrinterDevices |

<details>
<summary>View XML</summary>

```xml
<Group Id="{090b8e1d-5c7b-4f69-a4f2-fb76fa0535fc}" Type="Device">
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B090b8e1d-5c7b-4f69-a4f2-fb76fa0535fc%7D/GroupData -->
	<Name>Any Printer</Name>
	<MatchType>MatchAny</MatchType>
	<DescriptorIdList>
		<PrimaryId>PrinterDevices</PrimaryId>
	</DescriptorIdList>
</Group>
```
</details>


## Files
This policy is based on information in the following files:

- Printer Protection Samples\Intune OMA-URI\Allow any printer.xml
- Printer Protection Samples\Group Policy\Printer_Groups.xml


## Intune UX

<details>
<summary>Create a reusable setting for Any Printer</summary> 

   1. Navigate to Home > Endpoint Security > Attack Surface Reduction
   2. Click on Reusable Settings
   3. Click (+) Add
   4. Enter the Any Printer for the name.  
   5. Optionally, enter a description
   6. Click on "Next"
   7. Set the match type toggle to MatchAny
   
      
   8. Add a Removable Storage object for PrimaryId
        1. Click (+) Add
        2. Select "Reusable storage"
        3. Click on "Edit Instance"    
        4. Enter *PrimaryId* for Name
        5. Enter *PrinterDevices* for PrimaryId
        6. Click "Save"
    
   
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
   6. Under Name, enter *Allow any printer*
   7. Optionally, enter a description
   8. Click "Next"
</details>


<details>
<summary>Add a rule for Default Printer Allow to the policy</summary>


   1. Click on "+ Set reusable settings" under Included Id

   1. Click on *Any Printer*

   1. Click on "Select"


   1. Click on "+ Edit Entry"
   1. Enter *Default Printer Allow* for the name



   1. Select *Allow* from "Type"
   1. Select *Disable* from "Options"
   1. Select *Print* from "Access mask"


   1. Click "OK"
</details>



## GPO
### Groups
```xml
<Groups>
	<Group Id="{090b8e1d-5c7b-4f69-a4f2-fb76fa0535fc}" Type="Device">
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B090b8e1d-5c7b-4f69-a4f2-fb76fa0535fc%7D/GroupData -->
		<Name>Any Printer</Name>
		<MatchType>MatchAny</MatchType>
		<DescriptorIdList>
			<PrimaryId>PrinterDevices</PrimaryId>
		</DescriptorIdList>
	</Group>
</Groups>
```
### Rules
```xml
<PolicyRules>
	<PolicyRule Id="{2f746a4d-4ae1-4bc0-aaef-136d12518fd4}" >
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B2f746a4d-4ae1-4bc0-aaef-136d12518fd4%7D/RuleData -->
		<Name>Default Printer Allow</Name>
		<IncludedIdList>
			<GroupId>{090b8e1d-5c7b-4f69-a4f2-fb76fa0535fc}</GroupId>
		</IncludedIdList>
		<ExcludedIdList>
		</ExcludedIdList>
		<Entry Id="{ddcac8c7-e492-4cb9-ac46-28813e195d56}">
			<Type>Allow</Type>
			<AccessMask>64</AccessMask>
			<Options>4</Options>
		</Entry>
	</PolicyRule>
</PolicyRules>
```
## Intune Custom Settings

<details>
<summary>Create custom intune configuration</summary>

   1. Navigate to Devices > Configuration profiles
   2. Click Create (New Policy)
   3. Select Platform "Windows 10 and Later"
   4. Select Profile "Templates"
   5. Select Template Name "Custom"
   6. Click "Create"
   7. Under Name, enter *Allow any printer*
   8. Optionally, enter a description
   9. Click "Next" 
</details>
<details>
<summary>Add a row for Default Printer Allow</summary>  
   
   1. Click "Add"
   2. For Name, enter *Default Printer Allow*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B2f746a4d-4ae1-4bc0-aaef-136d12518fd4%7D/RuleData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *Printer Protection Samples\Intune OMA-URI\Allow any printer.xml*
         
   
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for Any Printer</summary>  
   
   1. Click "Add"
   2. For Name, enter *Any Printer*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B090b8e1d-5c7b-4f69-a4f2-fb76fa0535fc%7D/GroupData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *Printer Protection Samples\Intune OMA-URI\Any printer group.xml*
         
   
   
   7. Click "Save"
</details>


## Mac

This policy is not supported on Mac because Primary ID [PrinterDevices] is not supported on macOS.
