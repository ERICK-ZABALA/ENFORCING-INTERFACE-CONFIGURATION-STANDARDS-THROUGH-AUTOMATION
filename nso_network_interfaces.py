#!
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
    print("Deploying standard interface description to network.")

    # Read data from CSV source of truth
    # Generate desired interface description configurations
    # Load pyATS testbed and connect to devices
    # Lookup current interface descriptions
    # Apply new interface description (with configuration)
    # Gather CDP/LLDP neighbor match Source of Truth
    # Checking
    # Generate CSV File