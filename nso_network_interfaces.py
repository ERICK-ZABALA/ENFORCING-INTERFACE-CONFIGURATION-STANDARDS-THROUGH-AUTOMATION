#!/home/devnet/Documents/ENFORCING-INTERFACE-CONFIGURATION-STANDARDS-THROUGH-AUTOMATION/enforcing/bin/python
import argparse
import csv
from jinja2 import Template
from collections import defaultdict

from pyats.topology.loader import load
"""
A script to create and apply interface description from 
CSV file based source of truth.
Goal:
- Create interface description config from CSV file 
- Apply configurations to devices with configuration
- Record initial/old interface description back to CSV
- Verify if interfaces are connected as documented in CSV
"""

# Script enrtry point
if __name__ == "__main__":
    print("\n\033[92mDeploying standard interface description to network.\033[0m")
    # Use argparse retrieve script options
    parser = argparse.ArgumentParser(
        description="\n\033[95mDeploying standard interface description to network.\n\033[0m")

    parser.add_argument('--testbed', required=True, type=str, help="pyATS Testbed File")
    parser.add_argument('--sot', required=True, type=str, help="Interface Connection Source of Truth Spreadsheet")
    parser.add_argument('--apply', action='store_true', help="Should configurations be applied to network. If not set, config not applied.")

    args = parser.parse_args()

    print(f"\n\033[95mGenerating interface descriptions from file {args.sot} for testbed {args.testbed}.\n\033[0m")

    if args.apply:
        print("\033[96mConfigurations will be applied to devices.\033[0m")
    else:
        print("\033[93mConfigurations will NOT be applied to devices. They will be output to the screen only.\033[0m")
    
    
    # Read data from CSV source of truth

    print(f"\nOpening and readying Source of Truth File: {args.sot}\n")
    with open(args.sot, "r") as sot_file:
        sot = csv.DictReader(sot_file)

        #Loop over each row in the Source of Truth
        for row in sot:
            # For debugging, print out the raw data
            # Green
            print(f'\033[92mDevice {row["Device Name"]:15} Interface {row["Interface"]:25} SOT connection: {row["Connected Device"]} {row["Connected Interface"]}\033[0m')
    
        print("\n\033[96mConfigurations will be applied to devices - JINJA2 IN ACTION.\033[0m")

        # Create Jinja Template for Interface configuration
        with open("interface_config_template.j2") as f:
            interface_template = Template(f.read())
        
        # defaultdict variable for holding configurations
        new_config = defaultdict(dict)

        print("\nOpening and readying Source of Truth File.\n")
        with open(args.sot, "r") as sot_file:
            sot = csv.DictReader(sot_file)

            # Loop over each row in Source of Truth
            for row in sot:
                if row["Device Name"]:
                    # Generate desired configurations
                    new_config[row["Device Name"]][row["Interface"]] = interface_template.render(
                        interface_name=row["Interface"],
                        connected_device=row["Connected Device"],
                        connected_interface=row["Connected Interface"],
                        purpose=row["Purpose"]
                        )
                # For debugging, print out the new_configurations data 
                # Blue
            print("\033[94mJinja Template rendered configuration data.\n\033[0m")
                # Yellow
            print(f"\033[93m{new_config}\033[0m")
        
        print("New devices an Configuration")
        print("--------------------------------------")

        for device, interfaces in new_config.items():
            print(f"! Device {device}")
            for interface_name, interface_config in interfaces.items():
                print(interface_config)
            print("!\n")

        #### Connection with DEVICES VIA TESTBED ####
        # Load pyATS testbed and connect to devices with testbed
        print(f"\nLoading testbed file {args.testbed}")
        testbed = load(args.testbed)
        
        print(f"\033[98mConnecting to all devices in testbed {testbed.name}\n\033[0m")
        testbed.connect(log_stdout=False)

        print("\nTestDevices:", testbed.devices)    
        # Gather interface State
        # Lookup current interface descriptions - But only for
        # devices in SoT
        current_interface_details = {}
        for device in new_config.keys():
            try:
                print(f'\n\033[96mLearning current state on device {device}\033[0m')
                current_interface_details[device] = testbed.devices[device].learn("interface")
            except KeyError:
                print(f"\n\033[97m ⚠️ Error: Device {device} from Source of Truth is NOT in the testbed\033[0m")

            # For debugging, print the current_interface_details
            print("Output from learn interface operation")
            print(current_interface_details)

        # Checking Format about object interface
        for device, interfaces in current_interface_details.items():
            print(f'Device {device} Current Interface Descriptions are:')

            for interface, details in interfaces.info.items():
                try:
                    print(f' {interface}: {details["description"]}')
                # Interface without description won'have a the key
                except KeyError:
                    print(f' {interface} : ')

        # Generate desired interface description configurations
        # Load pyATS testbed and connect to devices
        # Lookup current interface descriptions
        # Apply new interface description (with configuration)
        # Gather CDP/LLDP neighbor match Source of Truth
        # Check if neighbor details match Source of Truth
        # Generate CSV File

        # Disconnect from devices using testbed
        for device in testbed.devices:
            print(f"\033[94mDisconnecting from device {device},\033[0m")
            testbed.devices[device].disconnect()



