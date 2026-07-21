# Getting Started with Odoo 18

## Login and Navigation

Welcome to Odoo 18! This guide will walk you through the basics of accessing the system, understanding your dashboard, and navigating the interface like a pro. By the end of this module, you'll be comfortable logging in, finding your way around, and creating your first records.

---

## 1. Logging In

### 1.1 Accessing Odoo

Odoo is a web-based application, which means you access it through a web browser — no installation required on your computer.

1. Open your preferred web browser.
2. In the address bar, type the URL provided by your administrator (e.g., `https://odoo.yourcompany.com` or `http://localhost:8069` for local installations).
3. Press **Enter**.

> **Tip:** Bookmark this URL for quick access in the future. In most browsers, press `Ctrl+D` (Windows) or `Cmd+D` (Mac) to add it to your bookmarks.

### 1.2 Browser Requirements

Odoo 18 works best on modern, up-to-date browsers. The following browsers are officially supported:

| Browser               | Version        |
| --------------------- | -------------- |
| Google Chrome         | Latest 2 major |
| Mozilla Firefox       | Latest 2 major |
| Microsoft Edge        | Latest 2 major |
| Apple Safari (macOS)  | Latest 2 major |

> **Tip:** Keep your browser updated to the latest version for the best experience and security.

### 1.3 The Login Screen

When you first navigate to the Odoo URL, you will see the login screen:

![Login Screen Placeholder — A clean form with fields for Email and Password]

**Fields on the Login Screen:**

- **Email** — Your work email address or username (provided by your administrator).
- **Password** — Your secret password (you may receive a temporary one on your first day).
- **Remember Me** — Check this box to stay logged in on your current device. Do **not** use this on shared or public computers.
- **Log In** — Click this button to enter Odoo.

### 1.4 First-Time Login

If this is your first time logging in:

1. Ask your administrator for your login credentials (email and temporary password).
2. Enter the temporary password in the **Password** field.
3. Click **Log In**.
4. You will be prompted to **change your password** immediately. Choose a strong password that:
   - Is at least 8 characters long
   - Contains uppercase and lowercase letters
   - Contains at least one number
   - Contains at least one special character (e.g., `!@#$%^&*`)
5. Confirm your new password by typing it again.
6. Click **Change Password**.

> ⚠️ **Security Warning:** Never share your password with anyone. Your administrator will never ask for your password. If you suspect your account has been compromised, change your password immediately and notify your administrator.

### 1.5 Logging Out

1. Click on your **user avatar / profile picture** in the top-right corner of any screen.
2. Select **Log Out** from the dropdown menu.
3. You will be returned to the login screen.

---

## 2. Dashboard Overview

### 2.1 The Home Dashboard

After logging in, you are presented with the **Home Dashboard**. This is your central starting point in Odoo.

![Dashboard Placeholder — A clean layout showing the main menu bar at top, app grid, and a central content area]

The dashboard consists of several key areas:

| Area               | Description                                               |
| ------------------ | --------------------------------------------------------- |
| **Main Menu Bar**  | The horizontal bar at the top — contains the Apps icon, breadcrumb navigation, and user menu. |
| **Apps Switcher**  | The grid icon (⋮⋮⋮) on the far left — opens the full list of installed applications. |
| **Content Area**   | The main central space — displays the current module's dashboard or record list. |
| **User Menu**      | Top-right corner — your avatar icon for preferences, log out, and help. |
| **Search Bar**     | Found in most views — allows you to search records quickly. |

### 2.2 Understanding Dashboard Widgets

When you open an app (e.g., Sales, CRM, Inventory), its dashboard may display **widgets** — small summary cards that give you a quick snapshot of key metrics.

Common widget types include:

- **KPI Widgets** — Large numbers showing totals (e.g., "12 New Leads This Week"). Often color-coded (green = good, red = needs attention).
- **Graph Widgets** — Small bar charts or line charts showing trends over time.
- **List Widgets** — Compact lists of recently updated records (e.g., "Recent Orders").
- **Kanban Widgets** — Cards grouped by stage (e.g., "Pipeline by Stage" in CRM).
- **Button Widgets** — Action buttons for common tasks (e.g., "Create Invoice", "New Order").

> **Tip:** Many dashboard widgets are clickable. Clicking a KPI number often takes you directly to the filtered list of those records.

### 2.3 The "My Dashboard" vs App Dashboard

- **My Dashboard** — A personalized landing page you can customize with the widgets you use most. Access it from the grid icon → **Dashboard**.
- **App Dashboard** — Each application (Sales, Inventory, etc.) has its own dashboard showing app-specific KPIs. You reach it by clicking the app icon from the apps switcher.

---

## 3. Navigation

### 3.1 The Main Menu Bar

Once you are inside an app, the main menu bar at the top changes to show the app's internal navigation.

For example, inside the **Sales** app, you might see:

```
[⋮⋮⋮ Apps]  Sales  >  Orders  >  Quotations
```

This is your **breadcrumb trail** — it shows you exactly where you are and lets you click back to previous sections.

### 3.2 Using the Apps Switcher (Grid Icon)

The **Apps Switcher** is the icon in the top-left corner that looks like a 3x3 grid of dots (⋮⋮⋮).

1. Click the **⋮⋮⋮ (grid icon)** to open the app switcher panel.
2. You will see all installed applications displayed as icons or tiles.
3. Click any app icon to switch to that application.

> **Tip:** As your company installs more apps, this list grows. Common apps include: Sales, CRM, Invoicing, Inventory, Accounting, Projects, HR, and Manufacturing.

### 3.3 Navigating Within an App

Each app has its own menu structure, typically organized into sections:

- **Dashboard** — High-level KPIs and summary.
- **Master Data** — Configuration and setup records (products, customers, etc.).
- **Operations** — Day-to-day records (orders, invoices, deliveries).
- **Reporting** — Analytical views, pivot tables, and charts.
- **Configuration** — App-specific settings.

> **Example (Sales app):**
> - Dashboard
> - Orders → Quotations, Orders, Customers
> - Products → Products, Variants, Price Lists
> - Reporting → Sales Analysis, Pivot
> - Configuration → Settings, Sales Teams, Payment Acquirers

To navigate:
1. Hover over a menu section to expand its sub-items.
2. Click a sub-item to go to that view.
3. Use the **breadcrumb** at the top to go back one or more levels.

### 3.4 Recent Records

Odoo keeps track of the records you have recently viewed or edited.

1. Click on the **search bar** (without typing anything).
2. A dropdown list appears showing **Recent Records** — the last 5-10 records you accessed.
3. Click any record from the list to jump directly to it.

> **Tip:** This is a huge time-saver when you are working across multiple records. Instead of searching for the same record again, just click the search bar and pick it from the recent list.

### 3.5 Favorites (Starred Records)

You can mark important records as **favorites** for quick access.

**To favorite a record:**
1. Open any record (e.g., a customer, a sales order, a product).
2. Click the **star icon (☆)** next to the record name in the header.
3. The star fills in (★), indicating the record is now a favorite.

**To access your favorites:**
1. Click on the **search bar** in any list view.
2. In the dropdown, look for the **Favorites** section.
3. Click a favorite record to open it.

**To remove a favorite:**
- Click the filled star (★) again — it will return to an empty star (☆).

> **Tip:** Favorites are personal — only you can see your own starred records.

---

## 4. Views Explained

Odoo presents data in several different **views**. Understanding each view type is essential for working efficiently.

### 4.1 List View

![List View Placeholder — A table/ spreadsheet layout with columns and rows]

The **List View** displays records in a table format, similar to a spreadsheet.

- **Columns** — Each field is a column. You can sort by clicking a column header.
- **Rows** — Each row is a record. Click a row to open its detail form.
- **Column Width** — Drag column borders to resize.
- **Column Visibility** — Click the **gear icon (⚙) → Columns** to show/hide columns.

**Common actions in List View:**
- Click the checkbox on the leftmost column to select records for bulk actions.
- Use the **Actions** button at the top to perform bulk operations (e.g., delete, export, send email).
- Double-click a cell to quickly edit its value inline (if enabled).

### 4.2 Form View

![Form View Placeholder — A detailed layout of a single record with fields organized in tabs]

The **Form View** shows all details of a single record.

- **Header** — Top area with the record name, status badges, and action buttons (Create, Edit, Save, Discard, Delete, Print, Actions).
- **Tabs** — Below the header, you'll find tabbed sections (e.g., "Sales Order Items", "Other Information", "Notes").
- **Fields** — Text boxes, dropdowns, date pickers, checkboxes, and many other field types.
- **Status Bar** — A horizontal progress bar indicating the record's stage (e.g., Draft → Confirmed → Done).

**Form View modes:**
- **Read-only mode** — Default when opening a record. You can see all information but cannot edit it.
- **Edit mode** — Click the **Edit** button (or pencil icon) to make changes.

### 4.3 Kanban View

![Kanban View Placeholder — Cards organized in columns representing stages]

The **Kanban View** displays records as cards, organized into columns by stage or status.

- **Cards** — Each card shows key information about a record (e.g., customer name, opportunity value, deadline).
- **Columns** — Columns represent pipeline stages (e.g., New, Qualified, Won, Lost).
- **Drag & Drop** — Drag a card from one column to another to change its stage.

**Best for:**
- CRM pipelines
- Project tasks
- Recruitment stages
- Manufacturing orders

> **Tip:** You can customize what information appears on Kanban cards by clicking the **gear icon → Kanban** settings.

### 4.4 Pivot View

![Pivot View Placeholder — A dynamic cross-tabulation table with expandable rows and columns]

The **Pivot View** is a powerful data analysis tool that lets you summarize and cross-reference data.

- **Rows** — Drag fields into the Rows area to group data vertically.
- **Columns** — Drag fields into the Columns area to group data horizontally.
- **Measures** — The values being calculated (e.g., Sum of Revenue, Count of Orders, Average Amount).
- **Expand/Collapse** — Click the ➕/➖ icons on grouped rows to drill down.

**Example:** In Sales Analysis, you can set:
- Rows: Sales Team
- Columns: Month
- Measures: Total Revenue

This gives you a matrix showing revenue by team across months.

### 4.5 Graph View

![Graph View Placeholder — A bar chart, line chart, or pie chart]

The **Graph View** visualizes data as charts.

- **Chart Types** — Toggle between:
  - **Bar Chart** — Good for comparing categories.
  - **Line Chart** — Ideal for showing trends over time.
  - **Pie Chart** — Shows proportions of a whole.
- **Measures** — What you are measuring (e.g., Total Revenue, Count).
- **Group By** — How the data is grouped (e.g., by Month, by Salesperson).

> **Tip:** Click on a bar or slice of a pie chart to drill down into the details.

### 4.6 Calendar View

![Calendar View Placeholder — A month, week, or day calendar layout]

The **Calendar View** displays records with dates on a calendar.

- **Views** — Toggle between Day, Week, Month, and Year views.
- **Navigation** — Use the ◀ and ▶ arrows to move between periods.
- **Quick Create** — Click on an empty date/time slot to create a new record for that date.

**Common uses:**
- Meetings and events
- Tasks with deadlines
- Sales orders with commitment dates
- Leave requests

### 4.7 Activity View

![Activity View Placeholder — A timeline or list of scheduled activities and tasks]

The **Activity View** shows scheduled activities and to-dos related to records.

- **Activities** — Calls, meetings, emails, to-dos, and other follow-ups.
- **Status** — Each activity shows its due date, assigned person, and completion status.
- **Mark as Done** — Click the checkbox to complete an activity.

> **Tip:** Use activities to manage your follow-ups. When you call a customer, schedule the next call as an activity right from the current record.

### Switching Between Views

Most apps offer multiple views. The view switcher buttons are typically located at the top-right of the content area, just left of the search bar:

```
[List] [Kanban] [Pivot] [Graph] [Calendar]
```

Click any icon to switch to that view. Odoo remembers your last-used view and will show it again next time.

---

## 5. Search & Filter

### 5.1 The Search Bar

The **search bar** is located at the top of every list view, pivot view, and many other views.

![Search Bar Placeholder — A text input field with a magnifying glass icon]

**Basic search:**
1. Click inside the search bar.
2. Type a keyword (e.g., a customer name, an order number, a product).
3. Press **Enter** or click the **search icon (🔍)**.
4. Results are filtered in real time.

> **Tip:** The search bar searches across multiple fields simultaneously (e.g., name, reference number, email).

### 5.2 Filters

**Predefined Filters** are ready-made filters provided by your administrator or by the app itself.

1. Click the **Filters** button (funnel icon) next to the search bar.
2. A dropdown shows available filters (e.g., "My Orders", "Overdue Invoices", "This Month").
3. Click a filter to apply it. Active filters are highlighted.
4. To remove a filter, click it again.

### 5.3 Custom Filters (Advanced Search)

You can build your own precise filters using the **Advanced Search** feature.

1. Click the **⋮ (chevron)** icon at the right end of the search bar.
2. Select **Add Custom Filter**.
3. A filter builder appears with three parts:
   - **Field** — Choose which field to filter on (e.g., "Total Amount").
   - **Operator** — Choose the condition (e.g., "is greater than", "contains", "equals", "is set").
   - **Value** — Enter the value to compare against (e.g., "1000").
4. Click **Apply** to add the filter.

You can stack multiple custom filters:

| Example Combination                | Result                                        |
| ---------------------------------- | --------------------------------------------- |
| "Customer" "contains" "Acme"       | AND                                           |
| "Total" "greater than" "500"       | Shows orders from Acme over $500              |

> ⚠️ **Note:** Multiple filters are combined with AND logic by default — all conditions must be true.

### 5.4 Group By

**Group By** organizes your records into collapsible sections.

1. Click the **Group By** button next to the Filters button.
2. Select a field to group by (e.g., "Salesperson", "Stage", "Create Date").
3. The list view immediately reorganizes into groups.
4. Click each group header to expand or collapse the records inside.
5. To remove grouping, click **Group By → None** or click the active group name again.

**Multi-level grouping:** Apply Group By multiple times to drill down. For example:
- First group: Sales Team
- Second group: Salesperson
- Third group: Status

### 5.5 Favorites (Saved Searches)

Once you have set up the perfect combination of filters and grouping, you can save it as a **Favorite** for one-click access later.

1. Set up your filters and group-by as desired.
2. Click **Favorites** (star icon) next to the search bar.
3. Click **Save Current Search**.
4. Give your search a name (e.g., "My High-Value Opportunities This Quarter").
5. Optionally, check **Default** if you want this search to apply automatically every time you enter this view.
6. Click **Save**.

**To use a saved search:**
- Click **Favorites** → click your saved search name.

**To manage saved searches:**
- Click **Favorites** → hover over a saved search → click the ✏ (edit) or 🗑 (delete) icon.

> **Tip:** You can share saved searches with your team. Look for the "Share" option when saving. Shared favorites appear for all users in the same company.

### 5.6 Search Operators

For power users, the search bar supports special operators:

| Operator | Example                  | Result                                    |
| -------- | ------------------------ | ----------------------------------------- |
| `AND`    | `Acme AND invoice`       | Records containing both terms             |
| `OR`     | `Acme OR Beta`           | Records containing either term            |
| `"..."`  | `"Beta Corp"`            | Exact phrase match                        |
| `-`      | `Acme -invoice`          | Records with "Acme" but NOT "invoice"     |
| `*`      | `Acm*`                   | Wildcard — matches "Acme", "Acme Corp"    |

---

## 6. Creating & Editing Records

### 6.1 Creating a New Record

1. Navigate to the app and view where you want to create a record (e.g., Sales → Orders → Quotations).
2. Click the **New** button (usually in the top-left corner of the view).
3. A blank **Form View** opens.
4. Fill in the required fields. Required fields are typically marked with:
   - A **red border** or asterisk (*)
   - A bold label
5. Click **Save** to store the record.

> **Tip:** If you navigate away without saving, your unsaved changes will be lost. Odoo will warn you if you try to leave an unsaved form.

**Quick Create:** In some views (like Kanban and Calendar), you can create records inline:
- **Kanban:** Click the **+** (Add) button at the bottom of a column.
- **Calendar:** Click an empty time slot.

### 6.2 Editing an Existing Record

1. Open the record you want to edit.
2. Click the **Edit** button (pencil icon) in the header.
3. The form switches to **Edit Mode** — all editable fields become white/active.
4. Make your changes.
5. Click **Save** to apply the changes.

> **Tip:** You can double-click some fields in list view to edit them inline without opening the full form.

### 6.3 Saving vs Discarding

- **Save** ✓ — Confirms your changes. The record is updated immediately.
- **Discard** ✗ — Cancels all changes since you opened the form. The record reverts to its last saved state.
- **Save & New** — Saves the current record and opens a blank form to create another of the same type.

### 6.4 Deleting Records

> ⚠️ **Warning:** Deletion is permanent. Some records cannot be deleted if they are linked to other data.

1. Open the record you want to delete.
2. Click the **Actions** button (gear icon ⚙).
3. Select **Delete**.
4. A confirmation dialog appears. Read the warning carefully.
5. Click **OK** to confirm, or **Cancel** to abort.

**Bulk Delete:**
1. In List View, check the boxes next to the records you want to delete.
2. Click the **Actions** button at the top.
3. Select **Delete**.
4. Confirm the deletion.

> **Tip:** If a record is in use (e.g., a customer with existing orders), Odoo may prevent you from deleting it. In this case, consider **archiving** the record instead (see Section 6.5).

### 6.5 Archiving vs Deleting

**Archiving** hides a record from most views without permanently removing it.

**To archive a record:**
1. Open the record in Form View.
2. Click **Actions → Archive** (or toggle the Archive checkbox if visible).
3. The record disappears from active lists but remains in the database.

**To unarchive:**
1. In List View, add a filter for **Archived** (Filters → Archived).
2. Open the archived record.
3. Click **Actions → Unarchive** (or uncheck the Archive checkbox).

> **Tip:** Archive is safer than delete. Use it for employees who have left, products you no longer sell, or customers you no longer serve. You can always restore them later.

### 6.6 Duplicating Records

1. Open the record you want to duplicate.
2. Click **Actions → Duplicate**.
3. A copy of the record opens with " (copy)" appended to its name.
4. Edit as needed and click **Save**.

---

## 7. Actions & Tools

### 7.1 The Print Button

The **Print** button (printer icon 🖨) generates PDF reports for the current record.

1. Open the record you want to print.
2. Click the **Print** button.
3. A dropdown shows available report templates (e.g., "Quotation / Order", "Invoice", "Picking Report").
4. Click a report template.
5. The report is generated as a PDF and opens in a new browser tab or downloads, depending on your browser settings.
6. From there, you can print it or save it to your computer.

> **Tip:** If you select multiple records in a list view, the Print button will include all of them in one report (e.g., batch printing invoices).

### 7.2 The Action Menu

The **Actions** menu (gear icon ⚙) contains additional operations you can perform on records.

Common actions include:

| Action             | Description                                         |
| ------------------ | --------------------------------------------------- |
| **Delete**         | Permanently remove the record (use with caution)    |
| **Duplicate**      | Create a copy of the current record                 |
| **Archive/Unarchive** | Hide or restore a record                        |
| **Export**         | Download record data as an Excel/CSV file           |
| **Send Email**     | Open a compose window with the record attached      |
| **Follow / Unfollow** | Subscribe to email notifications for this record |

**To access the Action Menu:**
- In **Form View**: Click the **Actions** button in the header.
- In **List View**: Select records using checkboxes, then click **Actions**.

### 7.3 Exporting Data

1. Navigate to the list view containing the data you want to export.
2. (Optional) Apply filters to narrow down the records.
3. Click **Actions → Export**.
4. In the export dialog:
   - Choose **Which records** to export (selected records or all visible).
   - Choose **Format**: CSV or Excel (.xlsx).
   - Select the **fields** you want to include in the export.
5. Click **Export**.
6. The file downloads to your computer.

> **Tip:** You can save your export templates for reuse. After setting up the fields, click **Add to My Exports** to save the configuration.

### 7.4 The Chatter (Communication Log)

![Chatter Placeholder — A vertical timeline of messages, notes, and activities at the bottom of a form]

The **Chatter** is the communication log located at the bottom of most Form Views. It serves as the collaboration hub for each record.

The Chatter has three main sections:

| Tab         | Purpose                                                  |
| ----------- | -------------------------------------------------------- |
| **Message** | Send internal notes (visible to all users) or send emails to external contacts (customers, vendors). |
| **Log Note** | Record a note that only internal users can see.         |
| **Schedule Activity** | Create a follow-up task (call, meeting, to-do) linked to this record. |

**Sending a message:**
1. In the Chatter, click the **Message** tab.
2. Type your message in the text field.
3. To send an email to the customer/contact: check **Send Email** — a new field appears to compose the email.
4. Click **Send**.
5. The message appears in the Chatter timeline immediately.

**Adding a Log Note:**
1. Click the **Log Note** tab.
2. Type your note.
3. Click **Send**. Log notes are internal only — customers cannot see them.

**Scheduling an Activity:**
1. Click **Schedule Activity**.
2. Choose the **Activity Type** (Call, Meeting, To-Do, Email, etc.).
3. Fill in the **Summary** and due **Date**.
4. Optionally assign the activity to another user.
5. Click **Schedule**.

> **Tip:** The Chatter is a powerful collaboration tool. Use it to keep everyone informed without leaving the record you're working on. All communication history stays with the record forever.

### 7.5 Attachments

You can attach files to any record.

**To add an attachment:**
1. Open the record in Form View.
2. Scroll down to the **Chatter** section.
3. Click the **paperclip icon (📎)** or drag and drop a file directly onto the Chatter.
4. (Optional) Enter a description for the attachment.
5. Click **Save** (or the file is attached immediately if you drag-and-dropped it).

**Supported file types:**
- Documents: PDF, DOCX, XLSX, PPTX, TXT
- Images: PNG, JPG, GIF, SVG
- Others: ZIP, XML, CSV

> **Tip:** There is typically a file size limit (often 25MB). If you need to attach larger files, compress them first or use an external file-sharing service and paste the link in the Chatter.

---

## 8. User Preferences

### 8.1 Accessing Your Preferences

1. Click your **avatar / profile picture** in the top-right corner of any screen.
2. Select **My Profile** from the dropdown menu.
3. Your personal profile record opens in Form View.

Alternatively, you can access preferences directly:
1. Click your avatar → **Preferences** (or **My Odoo.com Account** depending on your setup).
2. The preferences dialog opens.

### 8.2 Changing Your Password

1. Go to your **Preferences** (avatar → Preferences).
2. Click the **Change Password** tab or button.
3. Enter your **Current Password**.
4. Enter your **New Password**.
5. Confirm the new password.
6. Click **Change Password**.

### 8.3 Language & Timezone

1. Go to your **Preferences** (avatar → Preferences).
2. Under the **Locale** section:
   - **Language** — Select your preferred language from the dropdown. Odoo supports 40+ languages. Once selected, the interface will immediately update to your chosen language.
   - **Timezone** — Select your timezone (e.g., America/New_York, Europe/London, Asia/Tokyo). This ensures dates and times appear correctly in your local time.
3. Click **Save**.

> **Tip:** You can change your language at any time, even if your organization uses a default language. This only affects your own account.

### 8.4 Notification Preferences

Control how and when Odoo notifies you about activities.

1. Go to your **Preferences** (avatar → Preferences).
2. Under the **Notifications** section:

| Setting                | Options                            | Description                                      |
| ---------------------- | ---------------------------------- | ------------------------------------------------ |
| **On Document Alerts** | Handle Locally / In Odoo / Both    | How to receive notifications about document updates |
| **Schedule Activities** | Never / All / Only if I am the assignee | Which activity notifications to send |

- **Handle Locally** — Receive notifications only within Odoo (bell icon).
- **In Odoo** — Receive notifications in Odoo and via email.
- **Both** — Receive notifications in Odoo and via email.

3. Click **Save**.

### 8.5 Customizing Your Dashboard

You can personalize your home dashboard with the widgets you use most.

1. Navigate to your personal dashboard (⋮⋮⋮ → Dashboard).
2. Click the **Edit** (pencil) button or the **+ Add Widget** button.
3. Select from available widgets (e.g., "My Tasks", "My Activities", "CRM Analysis").
4. Arrange widgets by dragging them into your preferred order.
5. Resize widgets by dragging the bottom-right corner.
6. Click **Save** to lock in your layout.

> **Tip:** You can remove widgets by clicking the **✗** icon in the top-right corner of each widget.

### 8.6 Setting Your Signature

1. Go to your **Preferences** (avatar → Preferences).
2. In the **Signature** field, enter your email signature (HTML is supported for rich formatting).
3. Click **Save**.

Your signature will automatically be appended to emails sent from Odoo.

---

## 9. Keyboard Shortcuts

Odoo 18 includes several keyboard shortcuts to speed up your work.

### 9.1 Global Shortcuts

| Shortcut (Windows/Linux)  | Shortcut (Mac)        | Action                       |
| ------------------------ | --------------------- | ---------------------------- |
| `Alt + 1`                | `Option + 1`          | Go to Dashboard              |
| `Alt + 2`                | `Option + 2`          | Open Search                  |
| `Alt + S`                | `Option + S`          | Save current record          |
| `Alt + D`                | `Option + D`          | Discard changes              |
| `Alt + N`                | `Option + N`          | New record                   |
| `Alt + E`                | `Option + E`          | Edit current record          |
| `Alt + A`                | `Option + A`          | Open Actions menu            |
| `Alt + P`                | `Option + P`          | Open Printing menu           |
| `Alt + R`                | `Option + R`          | Refresh / Reload view        |
| `Alt + T`                | `Option + T`          | Open Settings (if applicable)|
| `Alt + Q`                | `Option + Q`          | Quick create                 |
| `Ctrl + S`               | `Cmd + S`             | Save (also works as fallback)|
| `Ctrl + Shift + ?`       | `Cmd + Shift + ?`     | Show keyboard shortcuts help |

### 9.2 Navigational Shortcuts

| Shortcut (Windows/Linux)     | Shortcut (Mac)            | Action                                   |
| ---------------------------- | ------------------------- | ---------------------------------------- |
| `Alt + ←` / `Alt + →`       | `Option + ←` / `Option + →` | Navigate calendar weeks / pagination |
| `Alt + K`                    | `Option + K`              | Switch to Kanban view                    |
| `Alt + L`                    | `Option + L`              | Switch to List view                      |
| `Alt + G`                    | `Option + G`              | Switch to Graph view                     |
| `Alt + V`                    | `Option + V`              | Switch to Pivot view                     |
| `Alt + C`                    | `Option + C`              | Switch to Calendar view                  |
| `Alt + I`                    | `Option + I`              | Switch to Activity view                  |

### 9.3 Chatter Shortcuts

| Shortcut (Windows/Linux) | Shortcut (Mac)    | Action                                |
| ------------------------ | ----------------- | ------------------------------------- |
| `Ctrl + Enter`           | `Cmd + Enter`     | Send message / log note in Chatter    |
| `Alt + M`                | `Option + M`      | Focus the Message tab in Chatter      |
| `Alt + N` (in Chatter)   | `Option + N`      | Focus the Log Note tab                |
| `Alt + K` (in Chatter)   | `Option + K`      | Schedule an activity                  |

> **Tip:** Press `Ctrl + Shift + ?` (Windows) or `Cmd + Shift + ?` (Mac) at any time to open a keyboard shortcut reference overlay within Odoo.

---

## Quick Reference Card

| Task                              | How To                                                     |
| --------------------------------- | ---------------------------------------------------------- |
| Log in to Odoo                    | URL → Enter email & password → Log In                      |
| Switch apps                       | Click grid icon (⋮⋮⋮) → Click app                         |
| Create a record                   | Navigate to view → Click **New** → Fill fields → **Save**  |
| Edit a record                     | Open record → Click **Edit** → Make changes → **Save**     |
| Delete a record                   | Open record → **Actions → Delete** → Confirm               |
| Archive a record                  | Open record → **Actions → Archive**                        |
| Search records                    | Type in search bar → Press **Enter**                       |
| Apply a filter                    | Click **Filters** → Select filter                          |
| Save a search                     | Set filters → Click **Favorites → Save Current Search**     |
| Export to Excel                   | **Actions → Export** → Choose fields → **Export**          |
| Print a report                    | Click **Print** → Choose report template                   |
| Change password                   | Avatar → **Preferences** → Change Password                 |
| Change language                   | Avatar → **Preferences** → Language dropdown               |
| Log out                           | Avatar → **Log Out**                                       |
| View keyboard shortcuts           | `Ctrl + Shift + ?` (Win) / `Cmd + Shift + ?` (Mac)        |

---

*Congratulations! You have completed the "Login and Navigation" module. You are now ready to start using Odoo 18 with confidence. Remember, practice makes perfect — explore different apps, try creating sample records, and don't be afraid to use the Chatter to collaborate with your team.*

*Next recommended module: Working with Customers and Contacts*
