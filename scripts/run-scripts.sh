#!/bin/bash -l

display_usage() {
    echo "Start Bash scripts in a directory one-by-one."
    echo -e "\nUsage:\n$0 [script directory] \n"
}

exe_script() {
    local temp_loc="$(mktemp -u)"
    mv "$1" "$temp_loc"
    bash "$temp_loc"
}

# if no script dir as argument
if [[ $# -eq 0 ]]; then
    display_usage
    exit 1
fi

for script in "${1}"/*;
do
    filename=$(basename "$script")
    extension="${filename##*.}"
    if [ "$extension" == "sh" ]; then
        echo "executing script: ${script}"
        #exe_script $script
    fi
done

exit 0
