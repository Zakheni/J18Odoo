/** @odoo-module **/

import { registry } from "@web/core/registry";
import { jsonrpc } from "@web/core/network/rpc_service";
import { TimesheetDashboard } from "@timesheet_analytics/js/timesheet_dashboard";

function getDefaultChartsState() {
    return {
        hours_per_employee: [],
        hours_over_time: [],
        hours_per_project: [],
        hours_per_organization: [],
        employee_task_breakdown: {},
        project_task_breakdown: {},
        day_breakdown: {},
    };
}

class PortalTimesheetDashboard extends TimesheetDashboard {
    async fetchTimesheetData(
        projectIds = false,
        taskIds = false,
        employeeIds = false,
        organizationIds = false,
        year = false,
        month = false,
        dateFrom = false,
        dateTo = false
    ) {
        const data = await jsonrpc("/my/timesheet-analytics/data", {
            project_id: projectIds,
            task_id: taskIds,
            employee_id: employeeIds,
            organization_id: organizationIds,
            year: year,
            month: month,
            date_from: dateFrom,
            date_to: dateTo,
        });

        this.timesheet_state.projects_count = data.projects_count || 0;
        this.timesheet_state.tasks_count = data.tasks_count || 0;
        this.timesheet_state.employees_count = data.employees_count || 0;
        this.timesheet_state.organizations_count = data.organizations_count || 0;
        this.timesheet_state.total_hours = data.total_hours || 0;

        this.timesheet_state.projects = data.projects || [];
        this.timesheet_state.tasks = data.tasks || [];
        this.timesheet_state.employees = data.employees || [];
        this.timesheet_state.organizations = data.organizations || [];
        this.timesheet_state.charts = data.charts || getDefaultChartsState();
        this.timesheet_state.timesheet_rows = data.timesheet_rows || [];

        this.updateFilteredList("projects", "project_search", "filtered_projects");
        this.updateFilteredList("tasks", "task_search", "filtered_tasks");
        this.updateFilteredList("employees", "employee_search", "filtered_employees");
        this.updateFilteredList("organizations", "organization_search", "filtered_organizations");

        this.timesheet_state.available_years = data.available_years || [];
        this.timesheet_state.available_months = data.available_months || [];
        this.timesheet_state.available_date_min = data.available_date_min || "";
        this.timesheet_state.available_date_max = data.available_date_max || "";

        let shouldApply = false;

        shouldApply = this.syncSelectionWithAvailable("selected_projects", this.timesheet_state.projects) || shouldApply;
        shouldApply = this.syncSelectionWithAvailable("selected_tasks", this.timesheet_state.tasks) || shouldApply;
        shouldApply = this.syncSelectionWithAvailable("selected_employees", this.timesheet_state.employees) || shouldApply;
        shouldApply = this.syncSelectionWithAvailable("selected_organizations", this.timesheet_state.organizations) || shouldApply;

        const availableMonthValues = (this.timesheet_state.available_months || []).map((m) => String(m));

        if (this.timesheet_state.selected_year !== "all") {
            if (this.timesheet_state.available_months.length === 1) {
                const onlyMonth = String(this.timesheet_state.available_months[0]);
                if (this.timesheet_state.selected_month !== onlyMonth) {
                    this.timesheet_state.selected_month = onlyMonth;
                    shouldApply = true;
                }
            } else if (
                this.timesheet_state.selected_month !== "all" &&
                !availableMonthValues.includes(this.timesheet_state.selected_month)
            ) {
                this.timesheet_state.selected_month = "all";
                shouldApply = true;
            }
        } else if (
            this.timesheet_state.selected_month !== "all" &&
            !availableMonthValues.includes(this.timesheet_state.selected_month)
        ) {
            this.timesheet_state.selected_month = "all";
            shouldApply = true;
        }

        const minDate = this.timesheet_state.available_date_min;
        const maxDate = this.timesheet_state.available_date_max;
        if (minDate && maxDate) {
            let normalizedDateFrom = this.timesheet_state.date_from;
            let normalizedDateTo = this.timesheet_state.date_to;
            let dateChanged = false;

            if (!normalizedDateFrom || normalizedDateFrom < minDate || normalizedDateFrom > maxDate) {
                normalizedDateFrom = minDate;
                dateChanged = true;
            }
            if (!normalizedDateTo || normalizedDateTo < minDate || normalizedDateTo > maxDate) {
                normalizedDateTo = maxDate;
                dateChanged = true;
            }
            if (normalizedDateFrom && normalizedDateTo && normalizedDateFrom > normalizedDateTo) {
                normalizedDateFrom = minDate;
                normalizedDateTo = maxDate;
                dateChanged = true;
            }

            if (dateChanged) {
                this.timesheet_state.date_from = normalizedDateFrom;
                this.timesheet_state.date_to = normalizedDateTo;
                shouldApply = true;
            }
        }

        this.reconcileDrillState();
        this.reconcileTimesheetTableFilters();

        if (shouldApply) {
            this.applyFilters();
        }
    }
}

registry.category("public_components").add(
    "web_timesheet_analytics.portal_timesheet_dashboard",
    PortalTimesheetDashboard
);
