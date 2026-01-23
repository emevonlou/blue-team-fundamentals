# Blue Team Fundamentals

Welcome to my Blue Team learning repository!  
This repository documents my journey in defensive cybersecurity, focusing on core principles, tools, and practical exercises.


##  Objectives

- Learn and document defensive security fundamentals  
- Understand SOC (Security Operations Center) workflow  
- Apply security principles such as the CIA Triad  
- Explore the MITRE ATT&CK framework for detection and mitigation  
- Develop scripts and playbooks for incident response  


##  CIA Triad

The CIA Triad is a fundamental model in information security:

- **Confidentiality**: Ensuring that sensitive data is accessible only to authorized users  
- **Integrity**: Ensuring that data is accurate and cannot be tampered with  
- **Availability**: Ensuring that systems and data are accessible when needed  

This model guides all Blue Team strategies.


##  SOC (Security Operations Center) Workflow

A SOC monitors, detects, and responds to security incidents:

1. **Monitoring**: Collect logs and alerts from networks, servers, and applications  
2. **Detection**: Identify potential threats using SIEM, IDS/IPS, and alerting rules  
3. **Analysis**: Investigate alerts to determine severity and scope  
4. **Response**: Contain and remediate threats following playbooks  
5. **Reporting & Lessons Learned**: Document incidents for continuous improvement  


##  MITRE ATT&CK Framework (Overview)

MITRE ATT&CK provides a **knowledge base of tactics and techniques** used by attackers:

- **Initial Access**: How attackers gain entry (phishing, exploits)  
- **Execution**: Running malicious code  
- **Persistence**: Maintaining access over time  
- **Privilege Escalation**: Gaining higher access  
- **Defense Evasion**: Avoiding detection  
- **Credential Access**: Stealing passwords or tokens  
- **Discovery & Lateral Movement**: Mapping and moving within networks  
- **Impact**: Actions to disrupt or destroy resources  

> Each project and exercise in this repository will reference relevant MITRE techniques.


##  Structure of this Repository

- `linux-hardening/` → Security hardening techniques for Linux systems  
- `log-analysis/` → Examples and exercises in log analysis  
- `incident-response/` → Playbooks for common security incidents  
- `detection-engineering/` → Rules, alerts, and MITRE ATT&CK mapping  
- `scripts-blue-team/` → Python and Bash scripts to automate defensive tasks


##  Notes

This repository is for **learning and professional growth** in Information Security.  
All examples are educational and safe to practice in lab environments.
