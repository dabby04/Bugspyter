#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 <CSV file>"
    echo "The CSV should have the following headers:"
    echo "Id, URL Repository, URL Commit, Files, Hash, BugType1, BugType2, RootCause, ImpactsFromBugs, Lines Changed Total Added, Lines Changed Total Deleted, Lines Changed File Added, Lines Changed File Deleted, Message Commit"
    echo "Example: $0 file_list.csv"
    exit 1
}

# Check if a CSV file is provided
if [ $# -ne 1 ]; then
    usage
fi

CSV_FILE=$1

# Check if the file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "File '$CSV_FILE' not found."
    exit 1
fi

# Create directories for the file if needed
mkdir -p "notebooks"
cd "notebooks"

# Read the CSV file line by line (skipping the header row)
{ read -r; while IFS="," read -r ID REPO_URL COMMIT_URL FILE_PATH HASH BUGTYPE1 BUGTYPE2 ROOTCAUSE IMPACTS ADDED DELETED FILE_ADDED FILE_DELETED MSG; do
    # Skip empty lines or lines starting with # (comments)
    if [[ -z "$REPO_URL" || "$REPO_URL" == "#"* ]]; then
        continue
    fi

    # Construct the raw file URL
    # REPO_OWNER=$(basename $(dirname "$REPO_URL"))
    # REPO_NAME=$(basename "$REPO_URL")
    NEW_REPO_URL="${REPO_URL/github.com/raw.githubusercontent.com}"
    RAW_URL="$NEW_REPO_URL/$HASH/$FILE_PATH"
    
    # Extract the filename from the file path
    FILE_NAME=$(basename "$FILE_PATH")
    TARGET_NAME="${FILE_NAME%.*}-$HASH.${FILE_NAME##*.}"

    # Download the file
    echo "Downloading $FILE_NAME from $RAW_URL..."
    RAW_URL="${RAW_URL// /%20}"
    curl -L -o "$TARGET_NAME" "$RAW_URL"

    if [ $? -eq 0 ]; then
        echo "File '$TARGET_NAME' downloaded successfully."
    else
        echo "Failed to download '$TARGET_NAME'. Check the URL or network connection."
    fi

done; } < "$CSV_FILE"
