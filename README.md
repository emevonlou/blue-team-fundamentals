# Blue Team Fundamentals

This repository demonstrates foundational Blue Team practices focused on
system monitoring, log analysis, and defensive security automation.

## Project Goals
- Practice real-world Blue Team techniques
- Build security monitoring scripts used in SOC environments
- Demonstrate secure scripting and operational awareness

## Repository Structure
scripts-blue-team/
Bash scripts for system monitoring and integrity checks

python-tools/
Python scripts for log analysis and automation

reports/
Generated daily security reports

docs/
Threat modeling and documentation

## Key Features
- SSH failed login monitoring
- File integrity checking with protected hash database
- Logged-in user monitoring
- Automated daily security reports with retention policy
- Threat model documentation

## Security Considerations
- Scripts validate dependencies before execution
- Sensitive operations require elevated privileges
- Integrity databases are protected with strict permissions
- Fail-fast behavior to avoid silent errors

## Disclaimer
This project is for educational and portfolio purposes only.



