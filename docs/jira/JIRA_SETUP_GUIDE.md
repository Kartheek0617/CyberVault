# CyberVault - Jira Setup Guide

## 1. Project Initialization
- **Project Name:** CyberVault SDEMS
- **Project Key:** CV
- **Template:** Scrum Software Development
- **Type:** Company-managed project

## 2. Issue Types Configuration
Ensure the following Issue Types are available in the project Schema:
- Epic (Major secure subsystems)
- Story (User-facing secure functionality)
- Task (Infrastructure/Security DevOps tasks)
- Sub-Task (Granular development steps)
- Bug / Vulnerability (Security defects)

## 3. Custom Fields
- **STRIDE Threat:** Dropdown (Spoofing, Tampering, Repudiation, Info. Disclosure, Denial of Service, Elevation)
- **CVSS Score:** Number format [0.0 - 10.0]
- **Story Points:** Number sequence (Fibonacci)

## 4. Workflow Configuration
Configure Kanban board columns:
1. BACKLOG
2. READY
3. IN PROGRESS (WIP Limit: 3)
4. CODE REVIEW
5. SECURITY TESTING
6. DONE

*Note: Transition to 'DONE' explicitly requires satisfaction of the CyberVault Definition of Done.*
