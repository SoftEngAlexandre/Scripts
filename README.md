# Genesys Cloud Automation (Python)

Automations developed in Python to manage and optimize operational processes in Genesys Cloud using REST API.

## 🚀 Overview

This repository contains scripts used in real-world scenarios to automate daily tasks such as user management, queue configuration, and data extraction.

These automations reduce manual work, minimize errors, and improve operational efficiency.

## 🛠️ Technologies

- Python
- REST API (Genesys Cloud)
- OAuth2 Authentication
- CSV / Excel
- SQL
- Postman

## 📦 Features

- User management (create, update, delete)
- Queue and routing configuration
- Wrap-up code management
- Auto-answer configuration
- Bulk operations using CSV
- Data extraction and reporting

## 📂 Scripts

- `get_users.py` → Retrieve all users
- `get_queue.py` → Retrieve queue data
- `delete_wrapup_from_queue.py` → Remove wrap-up codes
- `add_auto_answer.py` → Configure auto-answer
- `update_email.py` → Update user emails

## 💡 Use Case

These scripts are used in production environments to automate Genesys Cloud operations, reducing manual effort and increasing reliability.

## ▶️ How to Use

1. Configure your `.env` file with:
   - CLIENT_ID
   - CLIENT_SECRET
   - REGION

2. Run the script:

```bash
python script_name.py
