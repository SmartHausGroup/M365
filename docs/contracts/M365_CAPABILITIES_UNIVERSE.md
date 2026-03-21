# M365 Capabilities — Full Universe (The List)

**One list. Everything we want to support.** No code, no process—just the capabilities. Source: Microsoft Graph API, Teams, SharePoint, Outlook, OneDrive (permissions reference + API overview).

---

## Identity & directory

- list_users
- get_user
- create_user
- update_user
- disable_user
- delete_user
- reset_user_password
- get_user_photo
- set_user_photo
- list_user_owned_objects
- list_user_created_objects
- list_user_member_of
- list_user_license_details
- assign_user_license
- remove_user_license
- list_groups
- get_group
- create_group
- update_group
- delete_group
- list_group_members
- add_group_member
- remove_group_member
- list_group_owners
- add_group_owner
- remove_group_owner
- list_group_member_of
- list_devices
- get_device
- create_device
- update_device
- delete_device
- list_applications
- get_application
- create_application
- update_application
- delete_application
- list_service_principals
- get_service_principal
- create_service_principal
- update_service_principal
- delete_service_principal
- list_directory_roles
- get_directory_role
- assign_directory_role
- remove_directory_role
- list_directory_role_members
- list_domains
- get_organization
- list_administrative_units
- get_administrative_unit
- create_administrative_unit
- update_administrative_unit
- delete_administrative_unit
- list_administrative_unit_members
- add_administrative_unit_member
- remove_administrative_unit_member
- list_org_contacts
- get_org_contact

---

## Mail (Outlook)

- list_messages
- get_message
- create_message
- send_mail
- update_message
- delete_message
- move_message
- copy_message
- list_mail_folders
- get_mail_folder
- create_mail_folder
- update_mail_folder
- delete_mail_folder
- get_mailbox_settings
- update_mailbox_settings
- list_message_attachments
- get_attachment
- create_attachment
- search_mail

---

## Calendar

- list_calendars
- get_calendar
- create_calendar
- update_calendar
- delete_calendar
- list_calendar_groups
- get_calendar_group
- list_events
- get_event
- create_event
- update_event
- delete_event
- cancel_event
- accept_event
- decline_event
- tentatively_accept_event
- get_schedule
- get_schedule_availability
- list_events_in_schedule

---

## Contacts (Outlook)

- list_contacts
- get_contact
- create_contact
- update_contact
- delete_contact
- list_contact_folders
- get_contact_folder
- create_contact_folder

---

## Drive & files (OneDrive / SharePoint libraries)

- get_drive
- list_drives
- list_drive_items
- get_drive_item
- create_folder
- upload_file
- upload_file_content
- update_drive_item
- delete_drive_item
- copy_drive_item
- move_drive_item
- create_upload_session
- download_file
- get_drive_item_children
- get_drive_item_thumbnails
- share_drive_item
- create_sharing_link
- revoke_sharing_link
- list_drive_shared_with_me
- follow_drive_item
- unfollow_drive_item
- check_out_drive_item
- check_in_drive_item
- list_drive_changes

---

## Documents, spreadsheets, and presentations

- create_document
- update_document
- create_workbook
- update_workbook
- create_presentation
- update_presentation

---

## SharePoint (sites, lists, pages)

- list_sites
- get_site
- create_site
- update_site
- delete_site
- list_site_lists
- get_list
- create_list
- update_list
- delete_list
- list_list_items
- get_list_item
- create_list_item
- update_list_item
- delete_list_item
- get_list_item_versions
- restore_list_item_version
- list_site_pages
- get_site_page
- create_site_page
- update_site_page
- delete_site_page
- publish_site_page
- get_site_analytics

---

## Teams

- list_teams
- get_team
- create_team
- update_team
- delete_team
- archive_team
- unarchive_team
- list_team_members
- add_team_member
- remove_team_member
- update_team_member
- list_team_owners
- add_team_owner
- list_channels
- get_channel
- create_channel
- update_channel
- delete_channel
- list_channel_messages
- get_channel_message
- send_channel_message
- reply_to_channel_message
- update_channel_message
- delete_channel_message
- list_channel_tabs
- add_channel_tab
- update_channel_tab
- remove_channel_tab
- list_channel_members
- add_channel_member
- remove_channel_member
- list_chats
- get_chat
- create_chat
- list_chat_messages
- send_chat_message
- list_chat_members
- add_chat_member
- remove_chat_member
- list_teamwork_installed_apps
- install_team_app
- upgrade_team_app
- uninstall_team_app

---

## Planner & tasks

- list_plans
- get_plan
- create_plan
- update_plan
- delete_plan
- list_plan_tasks
- get_plan_task
- create_plan_task
- update_plan_task
- delete_plan_task
- assign_plan_task
- list_plan_buckets
- get_plan_bucket
- create_plan_bucket
- update_plan_bucket
- delete_plan_bucket

---

## Power Automate

- list_flows_admin
- get_flow_admin
- list_http_flows
- list_flow_owners
- list_flow_runs
- set_flow_owner_role
- remove_flow_owner_role
- enable_flow
- disable_flow
- delete_flow
- restore_flow
- invoke_flow_callback

---

## Power Apps

- list_powerapps_admin
- get_powerapp_admin
- list_powerapp_role_assignments
- set_powerapp_owner
- remove_powerapp_role_assignment
- delete_powerapp
- list_powerapp_environments
- get_powerapp_environment
- list_powerapp_environment_role_assignments
- set_powerapp_environment_role_assignment
- remove_powerapp_environment_role_assignment

---

## Power BI

- list_powerbi_workspaces
- get_powerbi_workspace
- list_powerbi_reports
- get_powerbi_report
- list_powerbi_datasets
- get_powerbi_dataset
- refresh_powerbi_dataset
- list_powerbi_dataset_refreshes
- list_powerbi_dashboards
- get_powerbi_dashboard

---

## Forms / Approvals / Connectors

Direct Microsoft Forms authoring and native response APIs are not claimed as implemented runtime
actions in E3D. The bounded E3D slice formalizes that boundary and implements approval and
connector-backed surfaces instead.

- get_approval_solution
- list_approval_items
- get_approval_item
- create_approval_item
- list_approval_item_requests
- respond_to_approval_item
- list_external_connections
- get_external_connection
- create_external_connection
- register_external_connection_schema
- get_external_item
- upsert_external_item
- create_external_group
- add_external_group_member

---

## OneNote

- list_notebooks
- get_notebook
- create_notebook
- update_notebook
- list_notebook_sections
- get_section
- create_section
- update_section
- delete_section
- list_section_pages
- get_page
- create_page
- update_page
- delete_page
- get_page_content

---

## To Do / tasks (Microsoft To Do)

- list_task_lists
- get_task_list
- create_task_list
- update_task_list
- delete_task_list
- list_tasks
- get_task
- create_task
- update_task
- delete_task
- complete_task

---

## Subscriptions & webhooks

- list_subscriptions
- create_subscription
- update_subscription
- delete_subscription
- renew_subscription

---

## Search

- search_query
- search_messages
- search_drive_items
- search_events
- search_people

---

## Reports & analytics

- get_report
- get_usage_reports
- get_activity_reports

---

## Access reviews & governance

- list_access_reviews
- get_access_review
- create_access_review
- list_access_review_decisions
- record_access_review_decision

---

## Security & compliance (where exposed via Graph)

- list_security_alerts
- get_security_alert
- list_security_incidents
- get_security_incident
- list_risk_detections
- list_secure_scores
- get_secure_score_profile
- update_security_incident

---

## Devices / endpoint management

- list_devices
- get_device
- list_device_compliance_summaries
- execute_device_action

---

## Provisioning / composite (our conveniences)

- provision_service
- list_automation_recipes
- get_automation_recipe
- provision_user_and_license
- offboard_user

---

**Count (this document):** ~220+ capability names.
**Implemented today:** 9.
**Universe:** this list. Close the gap by implementing from here.
