# zDash Terraform Skeleton

This directory contains a provider-neutral skeleton for deploying zDash to cloud providers (AWS, GCP, Azure, or local VMs).

**NOTE**: It is provider-agnostic. You should adapt the modules to use specific provider resources (e.g., `aws_db_instance` for AWS, `google_sql_database_instance` for GCP).

No credentials should ever be committed here.
