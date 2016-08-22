#!/bin/bash -l

display_usage() {
    echo "Start all analysis scripts in a given folder."
    echo -e "\nUsage:\n$0 [list of files] \n"
}

exe_script() {
    local temp_loc="$(mktemp -u)"
    mv "$1" "$temp_loc"
    bash "$temp_loc"
}

# if no root dir as argument
if [[ $# -eq 0 ]]; then
    display_usage
    exit 1
fi

for script in "$@"
do
    echo "starting script: ${script}"
    exe_script $script
done

exit 0
