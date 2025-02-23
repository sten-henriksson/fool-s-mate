#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Get list of tools from the YAML structure (formatted as in your example)
TOOLS=$(grep -E '^  - [a-zA-Z0-9]' approved_commands.yaml | awk '{print $2}')

# Special cases that need different checking
declare -A SPECIAL_CHECKS=(
    ["psexec.py"]="impacket-psexec"
    ["secretsdump.py"]="impacket-secretsdump"
    ["Meterpreter"]="msfconsole"
    ["dnscat2"]="dnscat2-server"
)

# Counters
total=0
installed=0
missing=0

echo -e "Checking installed tools...\n"

for tool in $TOOLS; do
    ((total++))
    # Handle special cases
    if [[ -n "${SPECIAL_CHECKS[$tool]}" ]]; then
        check_tool="${SPECIAL_CHECKS[$tool]}"
    else
        check_tool="$tool"
    fi

    # Check if tool is installed
    if command -v "$check_tool" &> /dev/null || dpkg -l | grep -q "$check_tool"; then
        echo -e "${GREEN}[+] Installed: $tool${NC}"
        ((installed++))
    else
        echo -e "${RED}[-] Missing:   $tool${NC}"
        ((missing++))
    fi
done

# Print summary
echo -e "\nSummary:"
echo -e "Total tools checked: $total"
echo -e "${GREEN}Installed: $installed${NC}"
echo -e "${RED}Missing:   $missing${NC}"

# Print special notes
echo -e "\n${YELLOW}Notes:"
echo -e "1. Some tools (like Mimikatz, Covenant) are Windows-based or require special installation"
echo -e "2. Python/Perl/Ruby tools might need to be run directly from their directory"
echo -e "3. Some tools (e.g., Impacket scripts) might be in /usr/share/doc/python3-impacket/examples/${NC}"
