#!/bin/bash
sudo apt-get install python-dnspython
sudo apt install chisel
sudo apt install merlin
sudo apt install merlin-server
sudo apt install veil
sudo apt install covenant-kbx
# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation commands map
declare -A INSTALL_COMMANDS=(
    # Reconnaissance
    ["subbrute"]="git clone https://github.com/TheRook/subbrute.git /opt/subbrute && echo 'export PATH=$PATH:/opt/subbrute' >> ~/.bashrc"
    ["MassDNS"]="git clone https://github.com/blechschmidt/massdns.git /opt/massdns && cd /opt/massdns && make"
    ["dmitry"]="sudo apt install -y dmitry"
    ["metagoofil"]="sudo apt install -y metagoofil"
    ["Amass"]="sudo apt install -y amass"
    ["knocker"]="sudo apt install -y knocker"
    
    # Vulnerability Scanning
    ["Nuclei"]="go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
    ["CrackMapExec"]="sudo pip3 install crackmapexec"
    
    # Credential Attacks
    ["patator"]="sudo apt install -y patator"
    ["Kerbrute"]="go install github.com/ropnop/kerbrute@latest"
    
    # Post-Exploitation
    ["evil-winrm"]="sudo gem install evil-winrm"
    ["chisel"]="go install github.com/jpillora/chisel@latest"
    ["psexec.py"]="sudo apt install -y python3-impacket"
    ["secretsdump.py"]="sudo apt install -y python3-impacket"
    
    # C2
    ["Merlin"]="go install github.com/Ne0nd0g/merlin@latest"
    ["Sliver"]="curl https://sliver.sh/install | sudo bash"
    
    # Network Pivoting
    ["rpivot"]="git clone https://github.com/artkond/rpivot.git /opt/rpivot"
    
    # Social Engineering
    ["Gophish"]="wget https://github.com/gophish/gophish/releases/latest/download/gophish-v0.12.1-linux-64bit.zip -O /tmp/gophish.zip && unzip /tmp/gophish.zip -d /opt/gophish"
    
    # Data Exfiltration
    ["Cloakify"]="git clone https://github.com/TryCatchHCF/Cloakify /opt/cloakify"
    ["Dnsteal"]="git clone https://github.com/m57/dnsteal.git /opt/dnsteal"
)

# Special cases (Windows/Non-Linux tools)
declare -A WINDOWS_TOOLS=(
    ["Mimikatz"]=1
    ["Covenant"]=1
    ["SharPersist"]=1
    ["Invoke-Obfuscation"]=1
)

# Counters
total=0
installed=0
new_installed=0
manual_required=0
windows_tools=0

# Get list of tools from the YAML structure
TOOLS=$(grep -E '^  - [a-zA-Z0-9]' approved_commands.yaml | awk '{print $2}')

echo -e "${BLUE}Starting tool installation check...${NC}\n"

for tool in $TOOLS; do
    ((total++))
    echo -e "${BLUE}Checking $tool...${NC}"
    
    # Skip Windows tools
    if [[ -n "${WINDOWS_TOOLS[$tool]}" ]]; then
        echo -e "${YELLOW}  Skip: Windows tool - cannot install on Linux${NC}"
        ((windows_tools++))
        continue
    fi

    # Check if already installed
    if command -v "$tool" &>/dev/null || dpkg -l | grep -qi "$tool"; then
        echo -e "${GREEN}  Already installed${NC}"
        ((installed++))
        continue
    fi

    # Check installation method
    if [[ -n "${INSTALL_COMMANDS[$tool]}" ]]; then
        echo -e "${YELLOW}  Installing $tool...${NC}"
        
        # Run installation command
        if eval "${INSTALL_COMMANDS[$tool]}"; then
            echo -e "${GREEN}  Successfully installed $tool${NC}"
            ((new_installed++))
        else
            echo -e "${RED}  Failed to install $tool${NC}"
            ((manual_required++))
        fi
    else
        echo -e "${RED}  No auto-install configured - requires manual installation${NC}"
        ((manual_required++))
    fi
done

# Print summary
echo -e "\n${BLUE}=== Installation Summary ===${NC}"
echo -e "Total tools checked: ${total}"
echo -e "${GREEN}Already installed: ${installed}${NC}"
echo -e "${GREEN}Newly installed: ${new_installed}${NC}"
echo -e "${RED}Requires manual installation: ${manual_required}${NC}"
echo -e "${YELLOW}Windows tools skipped: ${windows_tools}${NC}"

# Post-install notes
echo -e "\n${YELLOW}Important Notes:"
echo -e "1. Some tools installed to /opt may need to be added to your PATH"
echo -e "2. Restart your shell or run 'source ~/.bashrc' to update PATH"
echo -e "3. Go-based tools are installed in ~/go/bin (add to PATH if needed)"
echo -e "4. Manual installation required for tools marked in red"
echo -e "5. Windows tools cannot be installed on Kali Linux${NC}"
