# Resident Portal Maintenance HTML Evidence

Purpose:

```text
Record what the saved RENTCafe maintenance-page HTML confirms about Pacific Rose resident maintenance workflows.
```

Source:

```text
File: C:\Users\felix\Downloads\Pacific Rose _ Apartments in LOS ANGELES, CA _ RENTCafe.html
Captured / last modified locally: 2026-08-14 3:53:20 PM
SHA-256: FAEFF93B5CFDB59B6ADD424F069D780E1DF848A4084FC79D8815BE218E90DFE8
Evidence status: local saved HTML, inspected 2026-08-14.
```

Related loaded-form screenshot:

```text
File: C:\Users\felix\AppData\Local\Temp\codex-clipboard-248d2174-d1b3-4fcd-9d05-9d6c9046ebb0.png
Captured / last modified locally: 2026-08-14 4:11:10 PM
SHA-256: 8EF4BCC9C749E098B6A367A5B59EBA9DA52F3B66DABFFBA750FE703A4BEEE3EA
Evidence status: user-provided screenshot of loaded Submit Maintenance Request tab.
```

Confirmed HTML Findings:

```text
The saved page is the Pacific Rose RENTCafe resident maintenance page.
The canonical URL in the saved HTML points to /residentservices/pacific-rose0/maintenance.aspx.
The resident services content area is labeled Maintenance Request.
The page contains a Submit Maintenance Request tab.
The page contains a Request History tab.
The Submit Maintenance Request tab has contentclass MaintenanceRequestAdd.
The Request History tab has contentclass MaintenanceRequestView.
The page loads both tab bodies through ResidentCafeLoadContent.ashx.
The saved outer HTML includes empty tab panes for SubmitMaintenanceRequest and RequestHistory.
The saved outer HTML includes a Work Order Rating modal.
The hidden RequestTypeSelected value is maintenance.aspx.
Sidebar text states that residents can view maintenance request history, including pending and completed requests.
Sidebar text states that residents can submit a maintenance request directly to the maintenance technician or property management office.
```

Coverage Implication:

```text
The resident portal already exposes maintenance submission and request-history surfaces.
This makes maintenance visibility the strongest first pilot candidate.
The loaded Submit Maintenance Request screenshot confirms form fields for priority, category, sub category, full description, access instructions, permission to enter, pet status, and attachment upload.
AgencyOS Teams should not yet claim access to complete category/sub-category lists, request-history fields, statuses, SLA timestamps, or historical request records because those details are not fully captured.
```

Next Evidence Needed:

```text
Capture or export the loaded Request History tab after it renders.
Export complete Category and Sub Category option lists if available.
Record visible request-history status labels, date fields, work-order IDs, and rating fields.
Confirm whether Toya/Cirrus can export request history safely from RENTCafe.
```
