# usage-monitor

# Requirements
Modules beyond just the base Python installation

python pip -m install pywin32
python pip -m install boto3
python pip -m install pandas
python pip -m install pyyaml

# AWS Support
The yaml creds.yml file should be placed in a safe place and outside of the repository file structure.
A sample file is provided but the file should be moved and the extension .sample should be removed.

# Current Implementation
When either the mouse moves or a new window is in focus the usage is tracked.  The unix timestamp, mouse position, window name are stored.

# Coming Soon
* Build web interface in PHP to analyze usage.  Pull from S3 bucket for visualization.
* Calculate usage for web screen by what window was in focus.
* Clean up dataset
