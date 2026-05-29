/** @odoo-module **/

import { registry } from "@web/core/registry";
import { jsonrpc } from "@web/core/network/rpc_service";
import { download } from "@web/core/network/download";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";

const { Component, useState, onWillStart, onMounted, onPatched, onWillUnmount, useRef } = owl;
const { DateTime } = luxon;

const EXPORT_COLUMNS = [
    { key: "date", label: "Date" },
    { key: "year", label: "Year" },
    { key: "month", label: "Month" },
    { key: "employee", label: "Employee" },
    { key: "organization", label: "Organization" },
    { key: "project", label: "Project" },
    { key: "task", label: "Task" },
    { key: "description", label: "Description" },
    { key: "hours", label: "Hours" },
    { key: "user", label: "Timesheet User" },
    { key: "company", label: "Company" },
];

const DEFAULT_EXPORT_COLUMNS = ["date", "year", "month", "employee", "organization", "project", "task", "description", "hours"];
const NAV_ITEMS = [
    { key: "hours_summary", label: "Hours Summary / Overview" },
    { key: "projects_analysis", label: "Projects Analysis" },
    { key: "employees_analysis", label: "Employees Analysis" },
    { key: "timesheets", label: "Timesheets" },
];
const COMPANY_COLORS = [
    "#2563eb",
    "#0ea5e9",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#6366f1",
    "#14b8a6",
    "#f97316",
    "#ec4899",
];

function formatCompactValue(val) {
    const n = Number(val || 0);
    if (n >= 1000) return `${(n / 1000).toFixed(2)} K`;
    return n.toFixed(2);
}

function getPieSliceLabelsPlugin() {
    return {
        id: "pieSliceLabels",
        afterDatasetsDraw(chart) {
            if (chart.config.type !== "pie" && chart.config.type !== "doughnut") return;
            const { ctx, data } = chart;
            const dataset = data.datasets?.[0];
            if (!dataset?.data?.length) return;
            const total = dataset.data.reduce((s, v) => s + Number(v || 0), 0);
            if (!total) return;
            const meta = chart.getDatasetMeta(0);
            meta.data.forEach((arc, i) => {
                const value = Number(dataset.data[i] || 0);
                const pct = ((value / total) * 100).toFixed(2);
                const { x, y, startAngle, endAngle, outerRadius } = arc;
                const midAngle = (startAngle + endAngle) / 2;
                const radius = outerRadius * 0.75;
                const tx = x + Math.cos(midAngle) * radius;
                const ty = y + Math.sin(midAngle) * radius;
                ctx.save();
                ctx.font = "600 11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
                ctx.fillStyle = "#ffffff";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(`${pct}%`, tx, ty);
                ctx.restore();
            });
        },
    };
}

function getDefaultChartsState() {
    return {
        hours_per_employee: [],
        hours_per_employee_hierarchy: [],
        hours_over_time: [],
        hours_per_project: [],
        hours_per_project_hierarchy: [],
        hours_per_organization: [],
        employees_per_company: [],
        employee_task_breakdown: {},
        project_task_breakdown: {},
        day_breakdown: {},
    };
}

export class TimesheetDashboard extends Component {
    static components = { DateTimeInput };

    setup() {
        this.notification = useService("notification");
        this.employeeChart = null;
        this.lineChart = null;
        this.projectChart = null;
        this.organizationChart = null;
        this.projectsOrganizationChart = null;
        this.projectsOrganizationPieChart = null;
        this.projectsOverTimeChart = null;
        this.projectsHoursPerProjectChart = null;
        this.employeesProjectsChart = null;
        this.employeesHoursPerEmployeeChart = null;
        this.employeesOrganizationPieChart = null;
        this.employeesOverTimeChart = null;
        this.employeeChartFingerprint = "";
        this.lineChartFingerprint = "";
        this.projectChartFingerprint = "";
        this.organizationChartFingerprint = "";
        this.projectsOrganizationChartFingerprint = "";
        this.projectsOrganizationPieChartFingerprint = "";
        this.projectsOverTimeChartFingerprint = "";
        this.projectsHoursPerProjectChartFingerprint = "";
        this.employeesProjectsChartFingerprint = "";
        this.employeesHoursPerEmployeeChartFingerprint = "";
        this.employeesOrganizationPieChartFingerprint = "";
        this.employeesOverTimeChartFingerprint = "";
        this.employeeChartCanvasRef = useRef("employeeChartCanvas");
        this.employeeChartCardRef = useRef("employeeChartCard");
        this.lineChartCanvasRef = useRef("lineChartCanvas");
        this.lineChartCardRef = useRef("lineChartCard");
        this.projectChartCanvasRef = useRef("projectChartCanvas");
        this.projectChartCardRef = useRef("projectChartCard");
        this.organizationChartCanvasRef = useRef("organizationChartCanvas");
        this.organizationChartCardRef = useRef("organizationChartCard");
        this.projectsOrganizationChartCanvasRef = useRef("projectsOrganizationChartCanvas");
        this.projectsOrganizationPieChartCanvasRef = useRef("projectsOrganizationPieChartCanvas");
        this.projectsOverTimeChartCanvasRef = useRef("projectsOverTimeChartCanvas");
        this.projectsHoursPerProjectChartCanvasRef = useRef("projectsHoursPerProjectChartCanvas");
        this.employeesProjectsChartCanvasRef = useRef("employeesProjectsChartCanvas");
        this.employeesHoursPerEmployeeChartCanvasRef = useRef("employeesHoursPerEmployeeChartCanvas");
        this.employeesOrganizationPieChartCanvasRef = useRef("employeesOrganizationPieChartCanvas");
        this.employeesOverTimeChartCanvasRef = useRef("employeesOverTimeChartCanvas");
        this.timesheetTableCardRef = useRef("timesheetTableCard");
        this.onFullscreenChange = this.onFullscreenChange.bind(this);
        this.timesheet_state = useState({
            projects_count: 0,
            tasks_count: 0,
            employees_count: 0,
            organizations_count: 0,
            total_hours: 0,

            projects: [],
            filtered_projects: [],
            selected_projects: [],
            project_search: "",
            project_filter_open: false,

            tasks: [],
            filtered_tasks: [],
            selected_tasks: [],
            task_search: "",
            task_filter_open: false,

            employees: [],
            filtered_employees: [],
            selected_employees: [],
            employee_search: "",
            employee_filter_open: false,

            organizations: [],
            filtered_organizations: [],
            selected_organizations: [],
            organization_search: "",
            organization_filter_open: false,

            selected_year: "all",
            selected_month: "all",
            date_from: "",
            date_to: "",
            timesheet_rows: [],
            timesheet_table_search: "",
            timesheet_table_employee: "all",
            timesheet_table_project: "all",
            timesheet_table_organization: "all",
            timesheet_table_task: "all",
            available_years: [],
            available_months: [],
            available_date_min: "",
            available_date_max: "",
            year_dropdown_open: false,
            month_dropdown_open: false,

            export_dialog_open: false,
            export_in_progress: false,
            export_columns: EXPORT_COLUMNS,
            selected_export_columns: [...DEFAULT_EXPORT_COLUMNS],
            export_type: "raw", // raw | pivot
            pivot_presets_selected: ["employee_project_month"],

            active_nav: "hours_summary",
            nav_items: NAV_ITEMS,
            charts: getDefaultChartsState(),
            selected_project_drill: false,
            selected_month_drill: "",
            selected_day_drill: "",
            selected_organization_drill: false,
            line_chart_previous_date_filters: false,
            employee_chart_fullscreen: false,
            line_chart_fullscreen: false,
            project_chart_fullscreen: false,
            organization_chart_fullscreen: false,
            timesheets_table_fullscreen: false,

            project_chart_view: "bar",
            project_chart_display: "chart",
            employee_chart_display: "chart",
            project_hours_per_project_view: "bar",
            employee_hours_per_employee_view: "bar",
            project_hours_table_expanded: {},
            employee_hours_table_expanded: {},
        });

        this.months = [
            { value: "1", label: "January" },
            { value: "2", label: "February" },
            { value: "3", label: "March" },
            { value: "4", label: "April" },
            { value: "5", label: "May" },
            { value: "6", label: "June" },
            { value: "7", label: "July" },
            { value: "8", label: "August" },
            { value: "9", label: "September" },
            { value: "10", label: "October" },
            { value: "11", label: "November" },
            { value: "12", label: "December" },
        ];

        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.onWillStart();
        });

        onMounted(() => {
            document.addEventListener("fullscreenchange", this.onFullscreenChange);
            document.addEventListener("webkitfullscreenchange", this.onFullscreenChange);
            this.renderEmployeeChart();
            this.renderLineChart();
            this.renderProjectChart();
            this.renderOrganizationChart();
            this.renderProjectsOrganizationChart();
            this.renderProjectsOrganizationPieChart();
            this.renderProjectsOverTimeChart();
            this.renderProjectsHoursPerProjectChart();
            this.renderEmployeesProjectsChart();
            this.renderEmployeesHoursPerEmployeeChart();
            this.renderEmployeesOrganizationPieChart();
            this.renderEmployeesOverTimeChart();
        });

        onPatched(() => {
            this.renderEmployeeChart();
            this.renderLineChart();
            this.renderProjectChart();
            this.renderOrganizationChart();
            this.renderProjectsOrganizationChart();
            this.renderProjectsOrganizationPieChart();
            this.renderProjectsOverTimeChart();
            this.renderProjectsHoursPerProjectChart();
            this.renderEmployeesProjectsChart();
            this.renderEmployeesHoursPerEmployeeChart();
            this.renderEmployeesOrganizationPieChart();
            this.renderEmployeesOverTimeChart();
        });

        onWillUnmount(() => {
            document.removeEventListener("fullscreenchange", this.onFullscreenChange);
            document.removeEventListener("webkitfullscreenchange", this.onFullscreenChange);
            this.destroyEmployeeChart();
            this.destroyLineChart();
            this.destroyProjectChart();
            this.destroyOrganizationChart();
            this.destroyProjectsOrganizationChart();
            this.destroyProjectsOrganizationPieChart();
            this.destroyProjectsOverTimeChart();
            this.destroyProjectsHoursPerProjectChart();
            this.destroyEmployeesProjectsChart();
            this.destroyEmployeesHoursPerEmployeeChart();
            this.destroyEmployeesOrganizationPieChart();
            this.destroyEmployeesOverTimeChart();
        });
    }

    async onWillStart() {
        await this.fetchTimesheetData();
    }

    toPayloadIds(ids) {
        return ids.length ? ids : false;
    }

    getSelectedIds(selectElement) {
        return Array.from(selectElement.selectedOptions || [])
            .map((option) => parseInt(option.value, 10))
            .filter((id) => Number.isInteger(id) && id > 0);
    }

    syncSelectionWithAvailable(stateField, records) {
        const availableIds = new Set((records || []).map((record) => Number(record.id)));
        const currentSelection = this.timesheet_state[stateField] || [];
        const validSelection = currentSelection.filter((id) => availableIds.has(Number(id)));

        if (validSelection.length !== currentSelection.length) {
            this.timesheet_state[stateField] = validSelection;
            return true;
        }
        return false;
    }

    updateFilteredList(sourceField, queryField, targetField) {
        const query = (this.timesheet_state[queryField] || "").toLowerCase();
        const sourceRecords = this.timesheet_state[sourceField] || [];
        this.timesheet_state[targetField] = query
            ? sourceRecords.filter((record) => (record.name || "").toLowerCase().includes(query))
            : sourceRecords;
    }

    reconcileDrillState() {
        const projectKey = String(this.timesheet_state.selected_project_drill || "");
        if (projectKey && !this.timesheet_state.charts.project_task_breakdown[projectKey]) {
            this.timesheet_state.selected_project_drill = false;
        }

        const selectedMonth = this.timesheet_state.selected_month_drill || "";
        if (selectedMonth) {
            const availableMonths = new Set(
                (this.getHoursOverTime() || [])
                    .map((row) => String(row.date || "").slice(0, 7))
                    .filter((month) => month)
            );
            if (!availableMonths.has(selectedMonth)) {
                this.timesheet_state.selected_month_drill = "";
                this.timesheet_state.line_chart_previous_date_filters = false;
                this.timesheet_state.selected_day_drill = "";
            }
        }

        const dayKey = this.timesheet_state.selected_day_drill;
        if (dayKey && !this.timesheet_state.charts.day_breakdown?.[dayKey]) {
            this.timesheet_state.selected_day_drill = "";
        }

        const selectedOrganizations = this.timesheet_state.selected_organizations || [];
        this.timesheet_state.selected_organization_drill =
            selectedOrganizations.length === 1 ? Number(selectedOrganizations[0]) : false;

        const organizationRows = this.getHoursPerOrganization();
        if (
            this.timesheet_state.selected_organization_drill &&
            !organizationRows.some(
                (row) => Number(row.organization_id) === Number(this.timesheet_state.selected_organization_drill)
            )
        ) {
            this.timesheet_state.selected_organization_drill = false;
        }
    }

    getTimesheetTableFilterOptions(field) {
        const values = new Set();
        for (const row of this.timesheet_state.timesheet_rows || []) {
            const value = String(row?.[field] || "").trim();
            if (value) {
                values.add(value);
            }
        }
        return Array.from(values).sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" }));
    }

    reconcileTimesheetTableFilters() {
        const filters = [
            { stateKey: "timesheet_table_employee", field: "employee" },
            { stateKey: "timesheet_table_project", field: "project" },
            { stateKey: "timesheet_table_organization", field: "organization" },
            { stateKey: "timesheet_table_task", field: "task" },
        ];

        for (const filter of filters) {
            const selected = this.timesheet_state[filter.stateKey];
            if (selected === "all") {
                continue;
            }
            const options = this.getTimesheetTableFilterOptions(filter.field);
            if (!options.includes(selected)) {
                this.timesheet_state[filter.stateKey] = "all";
            }
        }
    }

    async fetchTimesheetData(projectIds = false, taskIds = false, employeeIds = false, organizationIds = false, year = false, month = false, dateFrom = false, dateTo = false) {
        const data = await jsonrpc("/get/project/data", {
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

    onProjectFilterChange(ev) {
        this.timesheet_state.selected_projects = this.getSelectedIds(ev.target);
        this.applyFilters();
    }

    onProjectSearch(ev) {
        this.timesheet_state.project_search = ev.target.value.toLowerCase();
        this.updateFilteredList("projects", "project_search", "filtered_projects");
    }

    toggleProjectFilter() {
        this.timesheet_state.project_filter_open = !this.timesheet_state.project_filter_open;
    }

    onTaskFilterChange(ev) {
        this.timesheet_state.selected_tasks = this.getSelectedIds(ev.target);
        this.applyFilters();
    }

    onTaskSearch(ev) {
        this.timesheet_state.task_search = ev.target.value.toLowerCase();
        this.updateFilteredList("tasks", "task_search", "filtered_tasks");
    }

    toggleTaskFilter() {
        this.timesheet_state.task_filter_open = !this.timesheet_state.task_filter_open;
    }

    onEmployeeFilterChange(ev) {
        this.timesheet_state.selected_employees = this.getSelectedIds(ev.target);
        this.applyFilters();
    }

    onEmployeeSearch(ev) {
        this.timesheet_state.employee_search = ev.target.value.toLowerCase();
        this.updateFilteredList("employees", "employee_search", "filtered_employees");
    }

    toggleEmployeeFilter() {
        this.timesheet_state.employee_filter_open = !this.timesheet_state.employee_filter_open;
    }

    applyEmployeeChartFilter(employeeId) {
        const nextEmployeeId = Number(employeeId || 0);
        if (!nextEmployeeId) {
            return;
        }
        const currentSelection = this.timesheet_state.selected_employees || [];
        const alreadySelected =
            currentSelection.length === 1 &&
            Number(currentSelection[0]) === nextEmployeeId;
        this.timesheet_state.selected_employees = alreadySelected ? [] : [nextEmployeeId];
        this.applyFilters();
    }

    applyProjectChartDrill(projectId) {
        const nextProjectId = Number(projectId || 0);
        if (!nextProjectId) {
            return;
        }
        this.timesheet_state.selected_project_drill = nextProjectId;
        const currentProjects = this.timesheet_state.selected_projects || [];
        const currentTasks = this.timesheet_state.selected_tasks || [];
        const projectChanged =
            currentProjects.length !== 1 ||
            Number(currentProjects[0]) !== nextProjectId;
        const hadTasks = Boolean(currentTasks.length);
        this.timesheet_state.selected_projects = [nextProjectId];
        if (hadTasks) {
            this.timesheet_state.selected_tasks = [];
        }
        if (projectChanged || hadTasks) {
            this.applyFilters();
        }
    }

    applyProjectTaskChartFilter(taskId) {
        const nextTaskId = Number(taskId || 0);
        if (!nextTaskId) {
            return;
        }
        const currentTasks = this.timesheet_state.selected_tasks || [];
        const alreadySelected =
            currentTasks.length === 1 &&
            Number(currentTasks[0]) === nextTaskId;
        this.timesheet_state.selected_tasks = alreadySelected ? [] : [nextTaskId];
        this.applyFilters();
    }

    setProjectChartView(view) {
        this.timesheet_state.project_chart_view = view;
    }

    setProjectChartBarView() {
        this.timesheet_state.project_chart_display = "chart";
        this.timesheet_state.project_chart_view = "bar";
    }

    setProjectChartPieView() {
        this.timesheet_state.project_chart_display = "chart";
        this.timesheet_state.project_chart_view = "pie";
    }

    setProjectHoursPerProjectView(view) {
        this.timesheet_state.project_hours_per_project_view = view;
    }

    setEmployeeHoursPerEmployeeView(view) {
        this.timesheet_state.employee_hours_per_employee_view = view;
    }

    toggleProjectHoursRow(key) {
        const exp = this.timesheet_state.project_hours_table_expanded || {};
        this.timesheet_state.project_hours_table_expanded = { ...exp, [key]: !exp[key] };
    }

    setProjectChartDisplay(display) {
        this.timesheet_state.project_chart_display = display;
    }

    setEmployeeChartDisplay(display) {
        this.timesheet_state.employee_chart_display = display;
    }

    toggleEmployeeHoursRow(key) {
        const exp = this.timesheet_state.employee_hours_table_expanded || {};
        this.timesheet_state.employee_hours_table_expanded = { ...exp, [key]: !exp[key] };
    }

    getEmployeeHoursTreeRows() {
        const flat = this.timesheet_state.charts.hours_per_employee_hierarchy || [];
        const expanded = this.timesheet_state.employee_hours_table_expanded || {};
        if (!flat.length) return [];
        const monthLabels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const monthNames = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"];
        const parseDateMonth = (val) => {
            if (Array.isArray(val) && val.length >= 2) {
                const y = parseInt(val[0], 10);
                const m = parseInt(val[1], 10);
                if (!isNaN(y) && !isNaN(m) && m >= 1 && m <= 12) return { year: y, month: m };
            }
            const str = String(val || "").trim();
            const match = str.match(/(\w+)\s+(\d{4})/i);
            if (match) {
                const monthPart = match[1].toLowerCase();
                const year = parseInt(match[2], 10);
                const mi = monthNames.findIndex((n) => monthPart.startsWith(n.slice(0, 3)));
                const m = mi >= 0 ? mi + 1 : 1;
                if (!isNaN(year) && m >= 1 && m <= 12) return { year, month: m };
            }
            return null;
        };
        const tree = {};
        for (const row of flat) {
            const eid = row.employee_id;
            const dm = row["date:month"];
            const pid = row.project_id;
            const tid = row.task_id;
            if (!eid) continue;
            if (!tree[eid]) {
                tree[eid] = { name: row.employee_name, hours: 0, months: {} };
            }
            tree[eid].hours += row.hours;
            if (!dm) continue;
            const parsed = parseDateMonth(dm);
            const monthKey = parsed ? `${parsed.year}-${String(parsed.month).padStart(2, "0")}` : String(dm);
            const period = parsed ? `${monthLabels[parsed.month - 1] || parsed.month}-${String(parsed.year).slice(-2)}` : monthKey;
            if (!tree[eid].months[monthKey]) {
                tree[eid].months[monthKey] = { period, hours: 0, year: parsed?.year ?? 0, month: parsed?.month ?? 1, projects: {} };
            }
            tree[eid].months[monthKey].hours += row.hours;
            if (!pid) continue;
            if (!tree[eid].months[monthKey].projects[pid]) {
                tree[eid].months[monthKey].projects[pid] = { name: row.project_name, hours: 0, tasks: [] };
            }
            tree[eid].months[monthKey].projects[pid].hours += row.hours;
            if (tid) {
                tree[eid].months[monthKey].projects[pid].tasks.push({
                    id: tid,
                    name: row.task_name || `Task ${tid}`,
                    hours: row.hours,
                });
            }
        }
        const rows = [];
        let grandTotal = 0;
        const employeeIds = Object.keys(tree).sort((a, b) => tree[b].hours - tree[a].hours);
        for (const eid of employeeIds) {
            const emp = tree[eid];
            const empKey = `emp_${eid}`;
            const empExpanded = expanded[empKey] === true;
            const monthKeys = Object.keys(emp.months).sort((a, b) => {
                const ma = emp.months[a];
                const mb = emp.months[b];
                return ma.year !== mb.year ? ma.year - mb.year : ma.month - mb.month;
            });
            rows.push({
                key: empKey,
                employee: emp.name,
                month: "",
                project: "",
                task: "",
                hours: Math.round(emp.hours * 100) / 100,
                level: 0,
                hasChildren: monthKeys.length > 0,
                expanded: empExpanded,
                rowClass: "hours-table-row-employee",
                isTotal: false,
            });
            if (!empExpanded) continue;
            for (const monthKey of monthKeys) {
                const mon = emp.months[monthKey];
                const monKey = `${empKey}_month_${monthKey}`;
                const monExpanded = expanded[monKey] === true;
                const projectIds = Object.keys(mon.projects).sort((a, b) => mon.projects[b].hours - mon.projects[a].hours);
                rows.push({
                    key: monKey,
                    employee: "",
                    month: mon.period,
                    project: "",
                    task: "",
                    hours: Math.round(mon.hours * 100) / 100,
                    level: 1,
                    hasChildren: projectIds.length > 0,
                    expanded: monExpanded,
                    rowClass: "hours-table-row-month",
                    isTotal: false,
                });
                if (!monExpanded) continue;
                for (const pid of projectIds) {
                    const proj = mon.projects[pid];
                    const projKey = `${monKey}_proj_${pid}`;
                    const projExpanded = expanded[projKey] === true;
                    const tasks = (proj.tasks || []).sort((a, b) => b.hours - a.hours);
                    rows.push({
                        key: projKey,
                        employee: "",
                        month: "",
                        project: proj.name,
                        task: "",
                        hours: Math.round(proj.hours * 100) / 100,
                        level: 2,
                        hasChildren: tasks.length > 0,
                        expanded: projExpanded,
                        rowClass: "hours-table-row-project",
                        isTotal: false,
                    });
                    if (!projExpanded) continue;
                    for (const t of tasks) {
                        rows.push({
                            key: `${projKey}_task_${t.id}`,
                            employee: "",
                            month: "",
                            project: "",
                            task: t.name,
                            hours: Math.round(t.hours * 100) / 100,
                            level: 3,
                            hasChildren: false,
                            expanded: false,
                            rowClass: "hours-table-row-task",
                            isTotal: false,
                        });
                    }
                    rows.push({
                        key: `${projKey}_total`,
                        employee: "",
                        month: "",
                        project: "Total",
                        task: "",
                        hours: Math.round(proj.hours * 100) / 100,
                        level: 2,
                        hasChildren: false,
                        expanded: false,
                        rowClass: "hours-table-row-total",
                        isTotal: true,
                    });
                }
                rows.push({
                    key: `${monKey}_total`,
                    employee: "",
                    month: "Total",
                    project: "",
                    task: "",
                    hours: Math.round(mon.hours * 100) / 100,
                    level: 1,
                    hasChildren: false,
                    expanded: false,
                    rowClass: "hours-table-row-total",
                    isTotal: true,
                });
            }
            rows.push({
                key: `${empKey}_total`,
                employee: "Total",
                month: "",
                project: "",
                task: "",
                hours: Math.round(emp.hours * 100) / 100,
                level: 0,
                hasChildren: false,
                expanded: false,
                rowClass: "hours-table-row-total",
                isTotal: true,
            });
            grandTotal += emp.hours;
        }
        rows.push({
            key: "_grand_total",
            employee: "Total",
            month: "",
            project: "",
            task: "",
            hours: Math.round(grandTotal * 100) / 100,
            level: 0,
            hasChildren: false,
            expanded: false,
            rowClass: "hours-table-row-total",
            isTotal: true,
        });
        return rows;
    }

    applyOrganizationChartFilter(organizationId) {
        const nextOrganizationId = Number(organizationId || 0);
        if (!nextOrganizationId) {
            return;
        }
        const currentSelection = this.timesheet_state.selected_organizations || [];
        const alreadySelected =
            currentSelection.length === 1 &&
            Number(currentSelection[0]) === nextOrganizationId;
        this.timesheet_state.selected_organizations = alreadySelected ? [] : [nextOrganizationId];
        this.timesheet_state.selected_organization_drill = alreadySelected ? false : nextOrganizationId;
        this.applyFilters();
    }

    onOrganizationFilterChange(ev) {
        const selectedOrganizations = this.getSelectedIds(ev.target);
        this.timesheet_state.selected_organizations = selectedOrganizations;
        this.timesheet_state.selected_organization_drill =
            selectedOrganizations.length === 1 ? Number(selectedOrganizations[0]) : false;
        this.applyFilters();
    }

    onOrganizationSearch(ev) {
        this.timesheet_state.organization_search = ev.target.value.toLowerCase();
        this.updateFilteredList("organizations", "organization_search", "filtered_organizations");
    }

    toggleOrganizationFilter() {
        this.timesheet_state.organization_filter_open = !this.timesheet_state.organization_filter_open;
    }

    onYearSelect(ev) {
        const year = ev.currentTarget.dataset.value;
        const previousYear = this.timesheet_state.selected_year;
        this.resetLineChartDrillContext();
        this.timesheet_state.selected_year = year;
        this.timesheet_state.year_dropdown_open = false;
        if (year !== "all" && year !== previousYear) {
            this.timesheet_state.selected_month = "all";
            this.timesheet_state.date_from = "";
            this.timesheet_state.date_to = "";
        } else if (year === "all" && previousYear !== "all") {
            this.timesheet_state.selected_month = "all";
            this.timesheet_state.date_from = "";
            this.timesheet_state.date_to = "";
        }
        this.applyFilters();
    }

    onMonthSelect(ev) {
        const month = ev.currentTarget.dataset.value;
        this.resetLineChartDrillContext();
        this.timesheet_state.selected_month = month;
        this.timesheet_state.month_dropdown_open = false;
        this.applyFilters();
    }

    onDateFromPickerChange(value) {
        this.resetLineChartDrillContext();
        this.timesheet_state.date_from = value ? value.toISODate() : "";
        this.applyFilters();
    }

    onDateToPickerChange(value) {
        this.resetLineChartDrillContext();
        this.timesheet_state.date_to = value ? value.toISODate() : "";
        this.applyFilters();
    }

    clearDateFilters() {
        this.resetLineChartDrillContext();
        this.timesheet_state.selected_year = "all";
        this.timesheet_state.selected_month = "all";
        this.timesheet_state.date_from = "";
        this.timesheet_state.date_to = "";
        this.timesheet_state.year_dropdown_open = false;
        this.timesheet_state.month_dropdown_open = false;
        this.applyFilters();
    }

    onTimesheetTableSearch(ev) {
        this.timesheet_state.timesheet_table_search = (ev.target.value || "").toLowerCase();
    }

    onTimesheetTableFilterChange(ev) {
        const stateKey = ev.currentTarget.dataset.stateKey;
        if (!stateKey || !(stateKey in this.timesheet_state)) {
            return;
        }
        this.timesheet_state[stateKey] = ev.currentTarget.value || "all";
    }

    hasTimesheetTableFilters() {
        return Boolean(
            this.timesheet_state.timesheet_table_search ||
            this.timesheet_state.timesheet_table_employee !== "all" ||
            this.timesheet_state.timesheet_table_project !== "all" ||
            this.timesheet_state.timesheet_table_organization !== "all" ||
            this.timesheet_state.timesheet_table_task !== "all"
        );
    }

    clearTimesheetTableFilters() {
        this.timesheet_state.timesheet_table_search = "";
        this.timesheet_state.timesheet_table_employee = "all";
        this.timesheet_state.timesheet_table_project = "all";
        this.timesheet_state.timesheet_table_organization = "all";
        this.timesheet_state.timesheet_table_task = "all";
    }

    clearAllFilters() {
        this.timesheet_state.selected_projects = [];
        this.timesheet_state.project_search = "";
        this.timesheet_state.selected_tasks = [];
        this.timesheet_state.task_search = "";
        this.timesheet_state.selected_employees = [];
        this.timesheet_state.employee_search = "";
        this.timesheet_state.selected_organizations = [];
        this.timesheet_state.organization_search = "";
        this.timesheet_state.selected_year = "all";
        this.timesheet_state.selected_month = "all";
        this.timesheet_state.date_from = "";
        this.timesheet_state.date_to = "";
        this.timesheet_state.timesheet_table_search = "";
        this.timesheet_state.timesheet_table_employee = "all";
        this.timesheet_state.timesheet_table_project = "all";
        this.timesheet_state.timesheet_table_organization = "all";
        this.timesheet_state.timesheet_table_task = "all";
        this.timesheet_state.project_filter_open = false;
        this.timesheet_state.task_filter_open = false;
        this.timesheet_state.employee_filter_open = false;
        this.timesheet_state.organization_filter_open = false;
        this.timesheet_state.year_dropdown_open = false;
        this.timesheet_state.month_dropdown_open = false;
        this.timesheet_state.selected_project_drill = false;
        this.timesheet_state.selected_month_drill = "";
        this.timesheet_state.selected_day_drill = "";
        this.timesheet_state.selected_organization_drill = false;
        this.timesheet_state.line_chart_previous_date_filters = false;
        this.fetchTimesheetData();
    }

    applyFilters() {
        const { year, month, dateFrom, dateTo } = this.getDateFilters();
        this.fetchTimesheetData(
            this.toPayloadIds(this.timesheet_state.selected_projects),
            this.toPayloadIds(this.timesheet_state.selected_tasks),
            this.toPayloadIds(this.timesheet_state.selected_employees),
            this.toPayloadIds(this.timesheet_state.selected_organizations),
            year,
            month,
            dateFrom,
            dateTo
        );
    }

    openExportDialog() {
        this.timesheet_state.export_type = this.timesheet_state.export_type || "raw";
        if (!Array.isArray(this.timesheet_state.pivot_presets_selected) || !this.timesheet_state.pivot_presets_selected.length) {
            this.timesheet_state.pivot_presets_selected = ["employee_project_month"];
        }
        this.timesheet_state.export_dialog_open = true;
    }

    closeExportDialog() {
        if (!this.timesheet_state.export_in_progress) {
            this.timesheet_state.export_dialog_open = false;
        }
    }

    isExportColumnSelected(columnKey) {
        return this.timesheet_state.selected_export_columns.includes(columnKey);
    }

    getExportColumnOrder(columnKey) {
        const index = this.timesheet_state.selected_export_columns.indexOf(columnKey);
        return index >= 0 ? index + 1 : "";
    }

    canMoveExportColumnUp(columnKey) {
        return this.timesheet_state.selected_export_columns.indexOf(columnKey) > 0;
    }

    canMoveExportColumnDown(columnKey) {
        const columns = this.timesheet_state.selected_export_columns;
        const index = columns.indexOf(columnKey);
        return index >= 0 && index < columns.length - 1;
    }

    onExportColumnToggle(ev) {
        const columnKey = ev.currentTarget.dataset.key;
        const isChecked = ev.currentTarget.checked;
        const columns = [...this.timesheet_state.selected_export_columns];
        const columnIndex = columns.indexOf(columnKey);

        if (isChecked && columnIndex < 0) {
            columns.push(columnKey);
            this.timesheet_state.selected_export_columns = columns;
            return;
        }

        if (!isChecked && columnIndex >= 0) {
            if (columns.length === 1) {
                ev.currentTarget.checked = true;
                this.notification.add("Select at least one column before exporting.", { type: "warning" });
                return;
            }
            columns.splice(columnIndex, 1);
            this.timesheet_state.selected_export_columns = columns;
        }
    }

    moveExportColumn(ev) {
        const columnKey = ev.currentTarget.dataset.key;
        const direction = ev.currentTarget.dataset.direction;
        const columns = [...this.timesheet_state.selected_export_columns];
        const sourceIndex = columns.indexOf(columnKey);

        if (sourceIndex < 0) {
            return;
        }

        const targetIndex = direction === "up" ? sourceIndex - 1 : sourceIndex + 1;
        if (targetIndex < 0 || targetIndex >= columns.length) {
            return;
        }

        [columns[sourceIndex], columns[targetIndex]] = [columns[targetIndex], columns[sourceIndex]];
        this.timesheet_state.selected_export_columns = columns;
    }

    getExportPayload() {
        const { year, month, dateFrom, dateTo } = this.getDateFilters();
        return {
            project_id: this.toPayloadIds(this.timesheet_state.selected_projects),
            task_id: this.toPayloadIds(this.timesheet_state.selected_tasks),
            employee_id: this.toPayloadIds(this.timesheet_state.selected_employees),
            organization_id: this.toPayloadIds(this.timesheet_state.selected_organizations),
            year: year,
            month: month,
            date_from: dateFrom,
            date_to: dateTo,
            columns: [...this.timesheet_state.selected_export_columns],
            export_type: this.timesheet_state.export_type || "raw",
            pivot_presets: [...(this.timesheet_state.pivot_presets_selected || [])],
        };
    }

    onExportTypeChange(ev) {
        this.timesheet_state.export_type = ev.currentTarget.value || "raw";
    }

    getPivotPresets() {
        return [
            {
                key: "employee_totals",
                label: "Employee Hours Summary",
                description: "Total hours per employee (SUM).",
            },
            {
                key: "project_totals",
                label: "Project Hours Summary",
                description: "Total hours per project (SUM).",
            },
            {
                key: "task_by_project",
                label: "Task Analysis (by Project)",
                description: "Total hours by project and task (SUM).",
            },
            {
                key: "task_by_employee",
                label: "Task Analysis (by Employee)",
                description: "Total hours by employee and task (SUM).",
            },
            {
                key: "monthly_summaries",
                label: "Monthly Hours Summary",
                description: "Total hours by year and month (SUM).",
            },
            {
                key: "org_insights",
                label: "Organization Monthly Insights",
                description: "Total hours by organization and month (SUM).",
            },
            {
                key: "employee_project_month",
                label: "Employee–Project Monthly Summary",
                description: "Total hours by employee, project, and month (SUM).",
            },
        ];
    }

    togglePivotPreset(ev) {
        const key = String(ev.currentTarget.dataset.key || "");
        if (!key) return;
        const checked = ev.currentTarget.checked;
        const selected = [...(this.timesheet_state.pivot_presets_selected || [])];
        const idx = selected.indexOf(key);
        if (checked && idx < 0) {
            selected.push(key);
        }
        if (!checked && idx >= 0) {
            selected.splice(idx, 1);
        }
        this.timesheet_state.pivot_presets_selected = selected;
    }

    getPivotPresetOrder(presetKey) {
        const index = (this.timesheet_state.pivot_presets_selected || []).indexOf(presetKey);
        return index >= 0 ? index + 1 : "";
    }

    canMovePivotPresetUp(presetKey) {
        return (this.timesheet_state.pivot_presets_selected || []).indexOf(presetKey) > 0;
    }

    canMovePivotPresetDown(presetKey) {
        const presets = this.timesheet_state.pivot_presets_selected || [];
        const index = presets.indexOf(presetKey);
        return index >= 0 && index < presets.length - 1;
    }

    movePivotPreset(ev) {
        const presetKey = ev.currentTarget.dataset.key;
        const direction = ev.currentTarget.dataset.direction;
        const presets = [...(this.timesheet_state.pivot_presets_selected || [])];
        const sourceIndex = presets.indexOf(presetKey);
        if (sourceIndex < 0) return;

        const targetIndex = direction === "up" ? sourceIndex - 1 : sourceIndex + 1;
        if (targetIndex < 0 || targetIndex >= presets.length) return;

        [presets[sourceIndex], presets[targetIndex]] = [presets[targetIndex], presets[sourceIndex]];
        this.timesheet_state.pivot_presets_selected = presets;
    }

    async exportTimesheets() {
        if (this.timesheet_state.export_in_progress) {
            return;
        }

        const exportType = this.timesheet_state.export_type || "raw";
        if (exportType === "pivot" && !(this.timesheet_state.pivot_presets_selected || []).length) {
            this.notification.add("Select at least one pivot preset to export.", { type: "warning" });
            return;
        }

        if (exportType === "raw" && !this.timesheet_state.selected_export_columns.length) {
            this.notification.add("Select at least one column before exporting.", { type: "warning" });
            return;
        }

        this.timesheet_state.export_in_progress = true;
        try {
            let url = "/timesheet_analytics/export/xlsx";
            if (exportType === "pivot") {
                url = "/timesheet_analytics/export/pivot/presets/xlsx";
            }
            await download({
                url,
                data: {
                    data: JSON.stringify(this.getExportPayload()),
                },
            });
            this.timesheet_state.export_dialog_open = false;
        } catch {
            this.notification.add("Unable to export timesheets. Please try again.", { type: "danger" });
        } finally {
            this.timesheet_state.export_in_progress = false;
        }
    }

    getSelectSize(listLength) {
        const maxVisible = 10;
        return Math.max(1, Math.min(listLength, maxVisible));
    }

    getDateFilters() {
        const year = this.timesheet_state.selected_year === "all" ? false : this.timesheet_state.selected_year;
        const month = this.timesheet_state.selected_month === "all" ? false : this.timesheet_state.selected_month;
        return {
            year: year,
            month: month,
            dateFrom: this.timesheet_state.date_from || false,
            dateTo: this.timesheet_state.date_to || false,
        };
    }

    toggleYearDropdown() {
        this.timesheet_state.year_dropdown_open = !this.timesheet_state.year_dropdown_open;
        if (this.timesheet_state.year_dropdown_open) {
            this.timesheet_state.month_dropdown_open = false;
        }
    }

    toggleMonthDropdown() {
        this.timesheet_state.month_dropdown_open = !this.timesheet_state.month_dropdown_open;
        if (this.timesheet_state.month_dropdown_open) {
            this.timesheet_state.year_dropdown_open = false;
        }
    }

    getYearLabel() {
        return this.timesheet_state.selected_year === "all"
            ? "All Years"
            : this.timesheet_state.selected_year;
    }

    getMonthLabel() {
        if (this.timesheet_state.selected_month === "all") {
            return "All Months";
        }
        const match = this.months.find(
            (month) => month.value === this.timesheet_state.selected_month
        );
        return match ? match.label : "All Months";
    }

    getDateTimeValue(value) {
        return value ? DateTime.fromISO(value) : false;
    }

    getMinDateTime() {
        return this.timesheet_state.available_date_min
            ? DateTime.fromISO(this.timesheet_state.available_date_min)
            : false;
    }

    getMaxDateTime() {
        return this.timesheet_state.available_date_max
            ? DateTime.fromISO(this.timesheet_state.available_date_max)
            : false;
    }

    getAvailableMonths() {
        const available = new Set(
            (this.timesheet_state.available_months || []).map((m) => String(m))
        );
        if (!available.size) {
            return this.months;
        }
        return this.months.filter((m) => available.has(m.value));
    }

    isSelected(selectedIds, id) {
        return selectedIds.includes(Number(id));
    }

    hasAppliedFilters() {
        return Boolean(
            this.timesheet_state.selected_projects.length ||
            this.timesheet_state.selected_tasks.length ||
            this.timesheet_state.selected_employees.length ||
            this.timesheet_state.selected_organizations.length ||
            this.timesheet_state.selected_year !== "all" ||
            this.timesheet_state.selected_month !== "all" ||
            this.timesheet_state.date_from ||
            this.timesheet_state.date_to
        );
    }

    getEntityFilterChips(prefix, selectedIds, records) {
        const nameById = new Map((records || []).map((record) => [Number(record.id), record.name]));
        return selectedIds.map((id) => ({
            key: `${prefix.toLowerCase()}-${id}`,
            label: `${prefix}: ${nameById.get(Number(id)) || id}`,
        }));
    }

    getAppliedFilterChips() {
        const chips = [];

        chips.push(...this.getEntityFilterChips("Organization", this.timesheet_state.selected_organizations, this.timesheet_state.organizations));
        chips.push(...this.getEntityFilterChips("Project", this.timesheet_state.selected_projects, this.timesheet_state.projects));
        chips.push(...this.getEntityFilterChips("Task", this.timesheet_state.selected_tasks, this.timesheet_state.tasks));
        chips.push(...this.getEntityFilterChips("Employee", this.timesheet_state.selected_employees, this.timesheet_state.employees));

        if (this.timesheet_state.selected_year !== "all") {
            chips.push({
                key: `year-${this.timesheet_state.selected_year}`,
                label: `Year: ${this.timesheet_state.selected_year}`,
            });
        }

        if (this.timesheet_state.selected_month !== "all") {
            chips.push({
                key: `month-${this.timesheet_state.selected_month}`,
                label: `Month: ${this.getMonthLabel()}`,
            });
        }

        if (this.timesheet_state.selected_day_drill) {
            chips.push({
                key: `day-${this.timesheet_state.selected_day_drill}`,
                label: `Day: ${this.timesheet_state.selected_day_drill}`,
            });
        }

        if (this.timesheet_state.date_from) {
            chips.push({
                key: `date-from-${this.timesheet_state.date_from}`,
                label: `From: ${this.timesheet_state.date_from}`,
            });
        }

        if (this.timesheet_state.date_to) {
            chips.push({
                key: `date-to-${this.timesheet_state.date_to}`,
                label: `To: ${this.timesheet_state.date_to}`,
            });
        }

        return chips;
    }

    setActiveNav(ev) {
        this.timesheet_state.active_nav = ev.currentTarget.dataset.nav || "hours_summary";
    }

    isActiveNav(navKey) {
        return this.timesheet_state.active_nav === navKey;
    }

    isHoursSummaryNav() {
        return this.timesheet_state.active_nav === "hours_summary";
    }

    isTimesheetsNav() {
        return this.timesheet_state.active_nav === "timesheets";
    }

    isProjectsAnalysisNav() {
        return this.timesheet_state.active_nav === "projects_analysis";
    }

    isEmployeesAnalysisNav() {
        return this.timesheet_state.active_nav === "employees_analysis";
    }

    getActiveNavLabel() {
        const current = (this.timesheet_state.nav_items || []).find(
            (item) => item.key === this.timesheet_state.active_nav
        );
        return current ? current.label : "Section";
    }

    formatHours(value) {
        return Number(value || 0).toFixed(2);
    }

    formatIntegerTick(value) {
        const numericValue = Number(value);
        if (!Number.isFinite(numericValue)) {
            return "";
        }
        const roundedValue = Math.round(numericValue);
        return Math.abs(numericValue - roundedValue) < 1e-6 ? String(roundedValue) : "";
    }

    formatDateLabel(dateValue) {
        if (!dateValue) {
            return "";
        }
        return DateTime.fromISO(dateValue).toFormat("dd LLL yyyy");
    }

    formatDayShort(dateValue) {
        if (!dateValue) {
            return "";
        }
        return DateTime.fromISO(dateValue).toFormat("dd LLL");
    }

    getMonthName(monthValue) {
        if (!monthValue) {
            return "";
        }
        const monthInt = Number(monthValue);
        if (!monthInt || monthInt < 1 || monthInt > 12) {
            return "";
        }
        return DateTime.fromObject({ year: 2000, month: monthInt, day: 1 }).toFormat("LLLL");
    }

    formatMonthLabel(monthValue) {
        if (!monthValue) {
            return "";
        }
        return DateTime.fromFormat(monthValue, "yyyy-MM").toFormat("LLLL yyyy");
    }

    formatMonthShortLabel(monthValue) {
        if (!monthValue) {
            return "";
        }
        const parsedMonth = DateTime.fromFormat(monthValue, "yyyy-MM");
        if (!parsedMonth.isValid) {
            return "";
        }
        return parsedMonth.toFormat("LLL yy");
    }

    getTimesheetRows() {
        return this.timesheet_state.timesheet_rows || [];
    }

    getProjectsOrganizationBreakdown() {
        const organizationIdByName = new Map(
            (this.getHoursPerOrganization() || []).map((row) => [
                String(row.organization_name || "").trim(),
                Number(row.organization_id || 0),
            ])
        );
        for (const organization of this.timesheet_state.organizations || []) {
            const organizationName = String(organization.name || "").trim();
            if (!organizationName || organizationIdByName.has(organizationName)) {
                continue;
            }
            organizationIdByName.set(organizationName, Number(organization.id || 0));
        }

        const projectsByOrganization = new Map();
        for (const row of this.getTimesheetRows()) {
            const organizationName = String(row.organization || "").trim();
            const projectName = String(row.project || "").trim();
            if (!organizationName || !projectName) {
                continue;
            }
            if (!projectsByOrganization.has(organizationName)) {
                projectsByOrganization.set(organizationName, new Set());
            }
            projectsByOrganization.get(organizationName).add(projectName);
        }

        const breakdown = [];
        for (const [organizationName, projects] of projectsByOrganization.entries()) {
            breakdown.push({
                organization_id: Number(organizationIdByName.get(organizationName) || 0),
                organization_name: organizationName,
                projects_count: projects.size,
            });
        }

        breakdown.sort((left, right) => {
            if (right.projects_count !== left.projects_count) {
                return right.projects_count - left.projects_count;
            }
            return left.organization_name.localeCompare(right.organization_name, undefined, { sensitivity: "base" });
        });
        return breakdown;
    }

    getProjectsOrganizationChartStageHeight(totalBars) {
        const bars = Math.max(1, Number(totalBars) || 1);
        const minHeight = 340;
        const perBar = 50;
        const base = 70;
        return `${Math.max(minHeight, (bars * perBar) + base)}px`;
    }

    getProjectsOrganizationChartRenderModel() {
        const rows = this.getProjectsOrganizationBreakdown();
        const selectedOrganizations = this.timesheet_state.selected_organizations || [];
        const selectedOrganizationId = selectedOrganizations.length === 1
            ? Number(selectedOrganizations[0] || 0)
            : 0;
        return {
            labels: rows.map((row) => row.organization_name),
            values: rows.map((row) => Number(row.projects_count || 0)),
            organizationIds: rows.map((row) => Number(row.organization_id || 0)),
            backgroundColor: rows.map((row) => {
                const baseColor = this.getSeriesColor(row.organization_id || 0);
                return selectedOrganizationId && selectedOrganizationId === Number(row.organization_id || 0)
                    ? "#1e3a8add"
                    : `${baseColor}cc`;
            }),
            borderColor: rows.map((row) => {
                const baseColor = this.getSeriesColor(row.organization_id || 0);
                return selectedOrganizationId && selectedOrganizationId === Number(row.organization_id || 0)
                    ? "#1e3a8a"
                    : baseColor;
            }),
            organizationNames: rows.map((row) => row.organization_name),
            total: rows.reduce((s, r) => s + Number(r.projects_count || 0), 0),
        };
    }

    getProjectsOrganizationChartConfig(chartModel) {
        const maxValue = Math.max(0, ...chartModel.values.map((value) => Number(value || 0)));
        const countStepSize = Math.max(1, Math.ceil(maxValue / 8));
        const selectedId = chartModel.organizationIds
            ? (this.timesheet_state.selected_organizations || []).length === 1
                ? Number(this.timesheet_state.selected_organizations[0] || 0)
                : 0
            : 0;
        const backgroundColor = (chartModel.organizationIds || []).map((id) =>
            selectedId && selectedId === id ? "rgba(16, 185, 129, 0.9)" : "rgba(16, 185, 129, 0.6)"
        );
        const borderColor = (chartModel.organizationIds || []).map((id) =>
            selectedId && selectedId === id ? "rgb(16, 185, 129)" : "rgba(16, 185, 129, 0.8)"
        );
        return {
            type: "bar",
            data: {
                labels: chartModel.labels,
                datasets: [
                    {
                        label: "#Projects",
                        data: chartModel.values,
                        backgroundColor: backgroundColor.length ? backgroundColor : chartModel.backgroundColor,
                        borderColor: borderColor.length ? borderColor : chartModel.borderColor,
                        borderWidth: 1,
                        barThickness: "flex",
                        maxBarThickness: 36,
                        hoverBackgroundColor: "rgba(16, 185, 129, 0.8)",
                        hoverBorderColor: "rgb(16, 185, 129)",
                        hoverBorderWidth: 2,
                    },
                ],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                layout: { padding: 4 },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (!canvas) {
                        return;
                    }
                    canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (_event, elements) => {
                    if (!elements.length) {
                        return;
                    }
                    const index = elements[0].index;
                    const organizationId = Number(chartModel.organizationIds[index] || 0);
                    if (organizationId) {
                        this.applyOrganizationChartFilter(organizationId);
                    }
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        displayColors: false,
                        callbacks: {
                            title: (items) => {
                                const index = items?.[0]?.dataIndex;
                                if (!Number.isInteger(index)) {
                                    return "";
                                }
                                return `${chartModel.organizationNames[index]}`;
                            },
                            label: (context) => `${Number(context.raw || 0).toFixed(0)} projects`,
                        },
                    },
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: "rgba(148, 163, 184, 0.22)",
                        },
                        ticks: {
                            color: "#64748b",
                            precision: 0,
                            maxTicksLimit: 8,
                            stepSize: countStepSize,
                            callback: (value) => this.formatIntegerTick(value),
                        },
                    },
                    y: {
                        grid: {
                            display: false,
                        },
                        ticks: {
                            color: "#334155",
                            autoSkip: false,
                            font: {
                                size: 11,
                                weight: "600",
                            },
                        },
                    },
                },
            },
        };
    }

    getProjectsOrganizationPieConfig(chartModel) {
        const orgColors = [
            "rgba(16, 185, 129, 0.8)", "rgba(239, 68, 68, 0.8)", "rgba(34, 197, 94, 0.8)",
            "rgba(245, 158, 11, 0.8)", "rgba(59, 130, 246, 0.8)", "rgba(139, 92, 246, 0.8)",
            "rgba(236, 72, 153, 0.8)", "rgba(20, 184, 166, 0.8)", "rgba(251, 146, 60, 0.8)",
        ];
        const pieSlicePlugin = getPieSliceLabelsPlugin();
        return {
            type: "pie",
            plugins: [pieSlicePlugin],
            data: {
                labels: chartModel.labels,
                datasets: [{
                    data: chartModel.values,
                    backgroundColor: orgColors.slice(0, chartModel.labels.length),
                    borderColor: "#ffffff",
                    borderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                layout: { padding: 4 },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (canvas) canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (_event, elements) => {
                    if (!elements.length) return;
                    const index = elements[0].index;
                    const organizationId = Number(chartModel.organizationIds[index] || 0);
                    if (organizationId) this.applyOrganizationChartFilter(organizationId);
                },
                plugins: {
                    legend: {
                        display: true,
                        position: "right",
                        labels: {
                            boxWidth: 10,
                            padding: 6,
                            font: { size: 9 },
                            formatter: (value, ctx) => {
                                const v = ctx.chart?.data?.datasets?.[0]?.data?.[ctx.dataIndex];
                                const summary = v != null ? formatCompactValue(v) : "";
                                return summary ? `${value} ${summary}` : value;
                            },
                        },
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const name = chartModel.organizationNames[ctx.dataIndex];
                                const total = chartModel.total || 1;
                                const val = Number(chartModel.values[ctx.dataIndex] || 0);
                                const pct = total > 0 ? ((val / total) * 100).toFixed(2) : "0";
                                return `${name || "?"}: ${val} projects (${pct}%)`;
                            },
                        },
                        backgroundColor: "rgba(30, 41, 59, 0.95)",
                    },
                },
            },
        };
    }

    getProjectsHoursPerProjectChartConfig(chartModel) {
        return {
            type: "bar",
            data: {
                labels: chartModel.labels,
                datasets: [{
                    label: "#Hours",
                    data: chartModel.values,
                    backgroundColor: "rgba(16, 185, 129, 0.6)",
                    borderColor: "rgb(16, 185, 129)",
                    borderWidth: 1,
                    barThickness: "flex",
                    maxBarThickness: 36,
                    hoverBackgroundColor: "rgba(16, 185, 129, 0.8)",
                    hoverBorderColor: "rgb(16, 185, 129)",
                    hoverBorderWidth: 2,
                }],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                layout: { padding: 4 },
                interaction: { mode: "index", axis: "y", intersect: false },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (canvas) canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (_event, elements) => {
                    if (!elements.length) return;
                    const projectId = Number(chartModel.keys[elements[0].index] || 0);
                    if (projectId) this.applyProjectChartDrill(projectId);
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        displayColors: false,
                        backgroundColor: "rgba(30, 41, 59, 0.95)",
                        callbacks: {
                            label: (ctx) => {
                                const name = chartModel.labels[ctx.dataIndex];
                                return `${name || "?"}: ${this.formatHours(ctx.raw)} hrs`;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        position: "bottom",
                        beginAtZero: true,
                        title: { display: true, text: "#Hours" },
                        grid: { color: "rgba(0,0,0,0.06)" },
                    },
                    y: {
                        position: "left",
                        display: true,
                        grid: { display: false },
                    },
                },
            },
        };
    }

    getProjectsPerEmployeeBreakdown() {
        const employeeIdByName = new Map(
            (this.getHoursPerEmployee() || []).map((row) => [
                String(row.employee_name || "").trim(),
                Number(row.employee_id || 0),
            ])
        );
        for (const employee of this.timesheet_state.employees || []) {
            const employeeName = String(employee.name || "").trim();
            if (!employeeName || employeeIdByName.has(employeeName)) {
                continue;
            }
            employeeIdByName.set(employeeName, Number(employee.id || 0));
        }

        const projectsByEmployee = new Map();
        for (const row of this.getTimesheetRows()) {
            const employeeName = String(row.employee || "").trim();
            const projectName = String(row.project || "").trim();
            if (!employeeName || !projectName) {
                continue;
            }
            if (!projectsByEmployee.has(employeeName)) {
                projectsByEmployee.set(employeeName, new Set());
            }
            projectsByEmployee.get(employeeName).add(projectName);
        }

        const breakdown = [];
        for (const [employeeName, projects] of projectsByEmployee.entries()) {
            breakdown.push({
                employee_id: Number(employeeIdByName.get(employeeName) || 0),
                employee_name: employeeName,
                projects_count: projects.size,
            });
        }

        breakdown.sort((left, right) => {
            if (right.projects_count !== left.projects_count) {
                return right.projects_count - left.projects_count;
            }
            return left.employee_name.localeCompare(right.employee_name, undefined, { sensitivity: "base" });
        });
        return breakdown;
    }

    getEmployeesProjectsChartStageHeight(totalBars) {
        const bars = Math.max(1, Number(totalBars) || 1);
        const minHeight = 340;
        const perBar = 50;
        const base = 70;
        return `${Math.max(minHeight, (bars * perBar) + base)}px`;
    }

    getEmployeesProjectsChartRenderModel() {
        const rows = this.getProjectsPerEmployeeBreakdown();
        const selectedEmployees = this.timesheet_state.selected_employees || [];
        const selectedEmployeeId = selectedEmployees.length === 1
            ? Number(selectedEmployees[0] || 0)
            : 0;
        return {
            labels: rows.map((row) => row.employee_name),
            values: rows.map((row) => Number(row.projects_count || 0)),
            employeeIds: rows.map((row) => Number(row.employee_id || 0)),
            backgroundColor: rows.map((row, index) => {
                const seed = Number(row.employee_id || (index + 1));
                const baseColor = this.getSeriesColor(seed);
                return selectedEmployeeId && selectedEmployeeId === Number(row.employee_id || 0)
                    ? "#1e3a8add"
                    : `${baseColor}cc`;
            }),
            borderColor: rows.map((row, index) => {
                const seed = Number(row.employee_id || (index + 1));
                const baseColor = this.getSeriesColor(seed);
                return selectedEmployeeId && selectedEmployeeId === Number(row.employee_id || 0)
                    ? "#1e3a8a"
                    : baseColor;
            }),
            employeeNames: rows.map((row) => row.employee_name),
        };
    }

    getEmployeesPerCompanyBreakdown() {
        return this.timesheet_state.charts.employees_per_company || [];
    }

    getEmployeesOrganizationPieRenderModel() {
        const rows = this.getEmployeesPerCompanyBreakdown();
        const total = rows.reduce((s, r) => s + Number(r.employees_count || 0), 0);
        return {
            labels: rows.map((r) => r.organization_name),
            values: rows.map((r) => Number(r.employees_count || 0)),
            organizationIds: rows.map((r) => Number(r.organization_id || 0)),
            organizationNames: rows.map((r) => r.organization_name),
            total,
        };
    }

    getEmployeesOrganizationPieConfig(chartModel) {
        const orgColors = [
            "rgba(16, 185, 129, 0.8)", "rgba(239, 68, 68, 0.8)", "rgba(34, 197, 94, 0.8)",
            "rgba(245, 158, 11, 0.8)", "rgba(59, 130, 246, 0.8)", "rgba(139, 92, 246, 0.8)",
            "rgba(236, 72, 153, 0.8)", "rgba(20, 184, 166, 0.8)", "rgba(251, 146, 60, 0.8)",
        ];
        const pieSlicePlugin = getPieSliceLabelsPlugin();
        return {
            type: "pie",
            plugins: [pieSlicePlugin],
            data: {
                labels: chartModel.labels,
                datasets: [{
                    data: chartModel.values,
                    backgroundColor: orgColors.slice(0, chartModel.labels.length),
                    borderColor: "#ffffff",
                    borderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                layout: { padding: 4 },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (canvas) canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (_event, elements) => {
                    if (!elements.length) return;
                    const index = elements[0].index;
                    const organizationId = Number(chartModel.organizationIds[index] || 0);
                    if (organizationId) this.applyOrganizationChartFilter(organizationId);
                },
                plugins: {
                    legend: {
                        display: true,
                        position: "right",
                        labels: {
                            boxWidth: 10,
                            padding: 6,
                            font: { size: 9 },
                            formatter: (value, ctx) => {
                                const v = ctx.chart?.data?.datasets?.[0]?.data?.[ctx.dataIndex];
                                const summary = v != null ? formatCompactValue(v) : "";
                                return summary ? `${value} ${summary}` : value;
                            },
                        },
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const name = chartModel.organizationNames[ctx.dataIndex];
                                const total = chartModel.total || 1;
                                const val = Number(chartModel.values[ctx.dataIndex] || 0);
                                const pct = total > 0 ? ((val / total) * 100).toFixed(2) : "0";
                                return `${name || "?"}: ${val} employees (${pct}%)`;
                            },
                        },
                        backgroundColor: "rgba(30, 41, 59, 0.95)",
                    },
                },
            },
        };
    }

    getEmployeesHoursPerEmployeeChartConfig(chartModel) {
        const selectedEmployees = this.timesheet_state.selected_employees || [];
        const selectedId = selectedEmployees.length === 1 ? Number(selectedEmployees[0] || 0) : 0;
        const backgroundColor = (chartModel.keys || []).map((id) =>
            selectedId && selectedId === id ? "rgba(79, 70, 229, 0.9)" : "rgba(99, 102, 241, 0.6)"
        );
        const borderColor = (chartModel.keys || []).map((id) =>
            selectedId && selectedId === id ? "rgb(79, 70, 229)" : "rgba(99, 102, 241, 0.8)"
        );
        return {
            type: "bar",
            data: {
                labels: chartModel.labels,
                datasets: [{
                    label: "#Hours",
                    data: chartModel.values,
                    backgroundColor: backgroundColor.length ? backgroundColor : "rgba(99, 102, 241, 0.6)",
                    borderColor: borderColor.length ? borderColor : "rgba(99, 102, 241, 0.8)",
                    borderWidth: 1,
                    barThickness: "flex",
                    maxBarThickness: 36,
                    hoverBackgroundColor: "rgba(79, 70, 229, 0.75)",
                    hoverBorderColor: "rgb(79, 70, 229)",
                    hoverBorderWidth: 2,
                }],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                layout: { padding: 4 },
                interaction: { mode: "index", axis: "y", intersect: false },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (canvas) canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (_event, elements) => {
                    if (!elements.length) return;
                    const employeeId = Number(chartModel.keys[elements[0].index] || 0);
                    if (employeeId) this.applyEmployeeChartFilter(employeeId);
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        displayColors: false,
                        backgroundColor: "rgba(30, 41, 59, 0.95)",
                        callbacks: {
                            label: (ctx) => {
                                const emp = (this.getHoursPerEmployee() || [])[ctx.dataIndex];
                                return `${emp?.employee_name || "?"}: ${this.formatHours(ctx.raw)} hrs`;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        position: "bottom",
                        beginAtZero: true,
                        title: { display: true, text: "Hours" },
                        grid: { color: "rgba(0,0,0,0.06)" },
                    },
                    y: {
                        position: "left",
                        display: true,
                        grid: { display: false },
                    },
                },
            },
        };
    }

    getEmployeesProjectsChartConfig(chartModel) {
        const maxValue = Math.max(0, ...chartModel.values.map((value) => Number(value || 0)));
        const countStepSize = Math.max(1, Math.ceil(maxValue / 8));
        const selectedId = (chartModel.employeeIds || []).length && (this.timesheet_state.selected_employees || []).length === 1
            ? Number(this.timesheet_state.selected_employees[0] || 0)
            : 0;
        const backgroundColor = (chartModel.employeeIds || []).map((id) =>
            selectedId && selectedId === id ? "rgba(16, 185, 129, 0.9)" : "rgba(16, 185, 129, 0.6)"
        );
        const borderColor = (chartModel.employeeIds || []).map((id) =>
            selectedId && selectedId === id ? "rgb(16, 185, 129)" : "rgba(16, 185, 129, 0.8)"
        );
        return {
            type: "bar",
            data: {
                labels: chartModel.labels,
                datasets: [
                    {
                        label: "#Projects",
                        data: chartModel.values,
                        backgroundColor: backgroundColor.length ? backgroundColor : chartModel.backgroundColor,
                        borderColor: borderColor.length ? borderColor : chartModel.borderColor,
                        borderWidth: 1,
                        barThickness: "flex",
                        maxBarThickness: 36,
                        hoverBackgroundColor: "rgba(16, 185, 129, 0.8)",
                        hoverBorderColor: "rgb(16, 185, 129)",
                        hoverBorderWidth: 2,
                    },
                ],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 280,
                },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (!canvas) {
                        return;
                    }
                    canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (_event, elements) => {
                    if (!elements.length) {
                        return;
                    }
                    const index = elements[0].index;
                    const employeeId = Number(chartModel.employeeIds[index] || 0);
                    if (employeeId) {
                        this.applyEmployeeChartFilter(employeeId);
                    }
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        displayColors: false,
                        callbacks: {
                            title: (items) => {
                                const index = items?.[0]?.dataIndex;
                                if (!Number.isInteger(index)) {
                                    return "";
                                }
                                return `${chartModel.employeeNames[index]}`;
                            },
                            label: (context) => `${Number(context.raw || 0).toFixed(0)} projects`,
                        },
                    },
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: "rgba(148, 163, 184, 0.22)",
                        },
                        ticks: {
                            color: "#64748b",
                            precision: 0,
                            maxTicksLimit: 8,
                            stepSize: countStepSize,
                            callback: (value) => this.formatIntegerTick(value),
                        },
                    },
                    y: {
                        grid: {
                            display: false,
                        },
                        ticks: {
                            color: "#334155",
                            autoSkip: false,
                            font: {
                                size: 11,
                                weight: "600",
                            },
                        },
                    },
                },
            },
        };
    }

    getProjectsOverTimeRows() {
        const dayBreakdown = this.timesheet_state.charts.day_breakdown || {};
        return Object.entries(dayBreakdown)
            .map(([dayKey, dayDetails]) => {
                const normalizedDayKey = String(dayKey || "");
                if (!normalizedDayKey) {
                    return false;
                }
                const projects = Array.isArray(dayDetails?.projects) ? dayDetails.projects : [];
                const uniqueProjects = new Set();
                for (const project of projects) {
                    const projectId = Number(project?.project_id || 0);
                    if (projectId > 0) {
                        uniqueProjects.add(`id:${projectId}`);
                        continue;
                    }
                    const projectName = String(project?.project_name || "").trim().toLowerCase();
                    if (projectName) {
                        uniqueProjects.add(`name:${projectName}`);
                    }
                }
                return {
                    date: normalizedDayKey,
                    projects_count: uniqueProjects.size,
                };
            })
            .filter(Boolean)
            .sort((left, right) => String(left.date || "").localeCompare(String(right.date || "")));
    }

    getProjectsOverTimeMonthlyCounts() {
        const dayBreakdown = this.timesheet_state.charts.day_breakdown || {};
        const monthlyProjects = new Map();

        for (const [dayKey, dayDetails] of Object.entries(dayBreakdown)) {
            const monthKey = String(dayKey || "").slice(0, 7);
            if (!monthKey) {
                continue;
            }

            if (!monthlyProjects.has(monthKey)) {
                monthlyProjects.set(monthKey, new Set());
            }

            const bucket = monthlyProjects.get(monthKey);
            const projects = Array.isArray(dayDetails?.projects) ? dayDetails.projects : [];
            for (const project of projects) {
                const projectId = Number(project?.project_id || 0);
                if (projectId > 0) {
                    bucket.add(`id:${projectId}`);
                    continue;
                }
                const projectName = String(project?.project_name || "").trim().toLowerCase();
                if (projectName) {
                    bucket.add(`name:${projectName}`);
                }
            }
        }

        return monthlyProjects;
    }

    getProjectsOverTimeTitle() {
        const selectedMonth = this.timesheet_state.selected_month_drill || "";
        if (!selectedMonth) {
            return "Projects Over Time";
        }
        return `Projects Over Time: ${this.formatMonthLabel(selectedMonth)}`;
    }

    getProjectsOverTimeSubtitle() {
        return "Click to filter";
    }

    getProjectsOverTimeRenderModel() {
        const rows = this.getProjectsOverTimeRows();
        const selectedMonth = this.timesheet_state.selected_month_drill || "";
        if (selectedMonth) {
            const monthRows = rows
                .filter((row) => String(row.date || "").slice(0, 7) === selectedMonth)
                .sort((a, b) => String(a.date || "").localeCompare(String(b.date || "")));
            return {
                mode: "days",
                keys: monthRows.map((row) => row.date),
                labels: monthRows.map((row) => this.formatDayShort(row.date)),
                values: monthRows.map((row) => Number(row.projects_count || 0)),
            };
        }

        const monthlyProjects = this.getProjectsOverTimeMonthlyCounts();
        const monthKeys = Array.from(monthlyProjects.keys()).sort((a, b) => a.localeCompare(b));
        return {
            mode: "months",
            keys: monthKeys,
            labels: monthKeys.map((month) => this.formatMonthShortLabel(month)),
            values: monthKeys.map((month) => {
                const projects = monthlyProjects.get(month);
                return projects ? projects.size : 0;
            }),
        };
    }

    getProjectsOverTimeChartConfig(chartModel) {
        const selectedDay = this.timesheet_state.selected_day_drill;
        const isDayMode = chartModel.mode === "days";
        const maxValue = Math.max(0, ...chartModel.values.map((value) => Number(value || 0)));
        const countStepSize = Math.max(1, Math.ceil(maxValue / 8));
        return {
            type: "line",
            data: {
                labels: chartModel.labels,
                datasets: [
                    {
                        label: "#Projects",
                        data: chartModel.values,
                        borderColor: "rgb(16, 185, 129)",
                        backgroundColor: "rgba(16, 185, 129, 0.2)",
                        fill: "start",
                        tension: 0.2,
                        borderWidth: 2,
                        pointRadius: chartModel.keys.map((key) => (isDayMode && key === selectedDay ? 5 : 3)),
                        pointHoverRadius: 5,
                        pointBackgroundColor: chartModel.keys.map((key) => (isDayMode && key === selectedDay ? "#f59e0b" : "#10b981")),
                        pointBorderColor: chartModel.keys.map((key) => (isDayMode && key === selectedDay ? "#f97316" : "#ffffff")),
                        pointBorderWidth: 2,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "nearest",
                    axis: "x",
                    intersect: false,
                },
                animation: false,
                layout: { padding: 4 },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (!canvas) {
                        return;
                    }
                    canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (event, elements, chart) => {
                    const activeElements = elements.length
                        ? elements
                        : chart.getElementsAtEventForMode(event, "nearest", { intersect: false }, true);
                    if (!activeElements.length) {
                        return;
                    }
                    const selectedKey = chartModel.keys[activeElements[0].index];
                    if (!selectedKey) {
                        return;
                    }
                    if (chartModel.mode === "months") {
                        this.applyMonthChartDrill(selectedKey);
                        return;
                    }
                    this.applyDayChartDrill(selectedKey);
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        displayColors: false,
                        callbacks: {
                            title: (items) => {
                                const index = items?.[0]?.dataIndex;
                                if (!Number.isInteger(index)) {
                                    return "";
                                }
                                return chartModel.mode === "months"
                                    ? this.formatMonthShortLabel(chartModel.keys[index])
                                    : this.formatDateLabel(chartModel.keys[index]);
                            },
                            label: (context) => `${Number(context.raw || 0).toFixed(0)} projects`,
                        },
                    },
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                        },
                        ticks: {
                            color: "#64748b",
                            autoSkip: true,
                            maxTicksLimit: 9,
                            maxRotation: 0,
                            minRotation: 0,
                        },
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: "rgba(148, 163, 184, 0.22)",
                        },
                        ticks: {
                            color: "#64748b",
                            precision: 0,
                            maxTicksLimit: 8,
                            stepSize: countStepSize,
                            callback: (value) => this.formatIntegerTick(value),
                        },
                    },
                },
            },
        };
    }

    getEmployeesOverTimeRows() {
        const dayBreakdown = this.timesheet_state.charts.day_breakdown || {};
        return Object.entries(dayBreakdown)
            .map(([dayKey, dayDetails]) => {
                const normalizedDayKey = String(dayKey || "");
                if (!normalizedDayKey) {
                    return false;
                }
                const employees = Array.isArray(dayDetails?.employees) ? dayDetails.employees : [];
                const uniqueEmployees = new Set();
                for (const employee of employees) {
                    const employeeId = Number(employee?.employee_id || 0);
                    if (employeeId > 0) {
                        uniqueEmployees.add(`id:${employeeId}`);
                        continue;
                    }
                    const employeeName = String(employee?.employee_name || "").trim().toLowerCase();
                    if (employeeName) {
                        uniqueEmployees.add(`name:${employeeName}`);
                    }
                }
                return {
                    date: normalizedDayKey,
                    employees_count: uniqueEmployees.size,
                };
            })
            .filter(Boolean)
            .sort((left, right) => String(left.date || "").localeCompare(String(right.date || "")));
    }

    getEmployeesOverTimeMonthlyCounts() {
        const dayBreakdown = this.timesheet_state.charts.day_breakdown || {};
        const monthlyEmployees = new Map();

        for (const [dayKey, dayDetails] of Object.entries(dayBreakdown)) {
            const monthKey = String(dayKey || "").slice(0, 7);
            if (!monthKey) {
                continue;
            }

            if (!monthlyEmployees.has(monthKey)) {
                monthlyEmployees.set(monthKey, new Set());
            }

            const bucket = monthlyEmployees.get(monthKey);
            const employees = Array.isArray(dayDetails?.employees) ? dayDetails.employees : [];
            for (const employee of employees) {
                const employeeId = Number(employee?.employee_id || 0);
                if (employeeId > 0) {
                    bucket.add(`id:${employeeId}`);
                    continue;
                }
                const employeeName = String(employee?.employee_name || "").trim().toLowerCase();
                if (employeeName) {
                    bucket.add(`name:${employeeName}`);
                }
            }
        }

        return monthlyEmployees;
    }

    getEmployeesOverTimeTitle() {
        const selectedMonth = this.timesheet_state.selected_month_drill || "";
        if (!selectedMonth) {
            return "Employees Over Time";
        }
        return `Employees Over Time: ${this.formatMonthLabel(selectedMonth)}`;
    }

    getEmployeesOverTimeSubtitle() {
        return "Click to filter";
    }

    getEmployeesOverTimeRenderModel() {
        const rows = this.getEmployeesOverTimeRows();
        const selectedMonth = this.timesheet_state.selected_month_drill || "";
        if (selectedMonth) {
            const monthRows = rows
                .filter((row) => String(row.date || "").slice(0, 7) === selectedMonth)
                .sort((a, b) => String(a.date || "").localeCompare(String(b.date || "")));
            return {
                mode: "days",
                keys: monthRows.map((row) => row.date),
                labels: monthRows.map((row) => this.formatDayShort(row.date)),
                values: monthRows.map((row) => Number(row.employees_count || 0)),
            };
        }

        const monthlyEmployees = this.getEmployeesOverTimeMonthlyCounts();
        const monthKeys = Array.from(monthlyEmployees.keys()).sort((a, b) => a.localeCompare(b));
        return {
            mode: "months",
            keys: monthKeys,
            labels: monthKeys.map((month) => this.formatMonthShortLabel(month)),
            values: monthKeys.map((month) => {
                const employees = monthlyEmployees.get(month);
                return employees ? employees.size : 0;
            }),
        };
    }

    getEmployeesOverTimeChartConfig(chartModel) {
        const selectedDay = this.timesheet_state.selected_day_drill;
        const isDayMode = chartModel.mode === "days";
        const maxValue = Math.max(0, ...chartModel.values.map((value) => Number(value || 0)));
        const countStepSize = Math.max(1, Math.ceil(maxValue / 8));
        return {
            type: "line",
            data: {
                labels: chartModel.labels,
                datasets: [
                    {
                        label: "#Employees",
                        data: chartModel.values,
                        borderColor: "rgb(16, 185, 129)",
                        backgroundColor: "rgba(16, 185, 129, 0.2)",
                        fill: "start",
                        tension: 0.2,
                        borderWidth: 2,
                        pointRadius: chartModel.keys.map((key) => (isDayMode && key === selectedDay ? 5 : 3)),
                        pointHoverRadius: 5,
                        pointBackgroundColor: chartModel.keys.map((key) => (isDayMode && key === selectedDay ? "#f59e0b" : "#10b981")),
                        pointBorderColor: chartModel.keys.map((key) => (isDayMode && key === selectedDay ? "#f97316" : "#ffffff")),
                        pointBorderWidth: 2,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "nearest",
                    axis: "x",
                    intersect: false,
                },
                animation: {
                    duration: 300,
                },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (!canvas) {
                        return;
                    }
                    canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (event, elements, chart) => {
                    const activeElements = elements.length
                        ? elements
                        : chart.getElementsAtEventForMode(event, "nearest", { intersect: false }, true);
                    if (!activeElements.length) {
                        return;
                    }
                    const selectedKey = chartModel.keys[activeElements[0].index];
                    if (!selectedKey) {
                        return;
                    }
                    if (chartModel.mode === "months") {
                        this.applyMonthChartDrill(selectedKey);
                        return;
                    }
                    this.applyDayChartDrill(selectedKey);
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        displayColors: false,
                        callbacks: {
                            title: (items) => {
                                const index = items?.[0]?.dataIndex;
                                if (!Number.isInteger(index)) {
                                    return "";
                                }
                                return chartModel.mode === "months"
                                    ? this.formatMonthShortLabel(chartModel.keys[index])
                                    : this.formatDateLabel(chartModel.keys[index]);
                            },
                            label: (context) => `${Number(context.raw || 0).toFixed(0)} employees`,
                        },
                    },
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                        },
                        ticks: {
                            color: "#64748b",
                            autoSkip: true,
                            maxTicksLimit: 9,
                            maxRotation: 0,
                            minRotation: 0,
                        },
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: "rgba(148, 163, 184, 0.22)",
                        },
                        ticks: {
                            color: "#64748b",
                            precision: 0,
                            maxTicksLimit: 8,
                            stepSize: countStepSize,
                            callback: (value) => this.formatIntegerTick(value),
                        },
                    },
                },
            },
        };
    }

    getTimesheetTableRows() {
        const rows = this.getTimesheetRows();
        const query = (this.timesheet_state.timesheet_table_search || "").trim().toLowerCase();
        const selectedEmployee = this.timesheet_state.timesheet_table_employee || "all";
        const selectedProject = this.timesheet_state.timesheet_table_project || "all";
        const selectedOrganization = this.timesheet_state.timesheet_table_organization || "all";
        const selectedTask = this.timesheet_state.timesheet_table_task || "all";

        return rows.filter((row) => {
            const employee = String(row.employee || "");
            const project = String(row.project || "");
            const organization = String(row.organization || "");
            const task = String(row.task || "");

            if (selectedEmployee !== "all" && employee !== selectedEmployee) {
                return false;
            }
            if (selectedProject !== "all" && project !== selectedProject) {
                return false;
            }
            if (selectedOrganization !== "all" && organization !== selectedOrganization) {
                return false;
            }
            if (selectedTask !== "all" && task !== selectedTask) {
                return false;
            }
            if (!query) {
                return true;
            }

            const searchBlob = [
                row.date,
                employee,
                organization,
                project,
                task,
                row.description,
                row.user,
                row.company,
                this.formatHours(row.hours),
            ].join(" ").toLowerCase();
            return searchBlob.includes(query);
        });
    }

    getTimesheetTableTotalHours() {
        const rows = this.getTimesheetTableRows();
        return rows.reduce((sum, row) => sum + Number(row.hours || 0), 0);
    }

    getTimesheetTableEmptyState() {
        if (!this.getTimesheetRows().length) {
            return "No timesheet entries found for the selected dashboard filters.";
        }
        return "No timesheet rows match the table filters.";
    }

    getHoursPerEmployee() {
        return this.timesheet_state.charts.hours_per_employee || [];
    }

    getHoursPerProject() {
        return this.timesheet_state.charts.hours_per_project || [];
    }

    getProjectHoursTreeRows() {
        const flat = this.timesheet_state.charts.hours_per_project_hierarchy || [];
        const expanded = this.timesheet_state.project_hours_table_expanded || {};
        if (!flat.length) return [];
        const tree = {};
        for (const row of flat) {
            const pid = row.project_id;
            const tid = row.task_id;
            const eid = row.employee_id;
            if (!tree[pid]) {
                tree[pid] = { name: row.project_name, hours: 0, tasks: {} };
            }
            tree[pid].hours += row.hours;
            if (!tid) continue;
            if (!tree[pid].tasks[tid]) {
                tree[pid].tasks[tid] = { name: row.task_name || `Task ${tid}`, hours: 0, employees: [] };
            }
            tree[pid].tasks[tid].hours += row.hours;
            if (eid) {
                tree[pid].tasks[tid].employees.push({
                    id: eid,
                    name: row.employee_name || `Employee ${eid}`,
                    hours: row.hours,
                });
            }
        }
        const rows = [];
        let grandTotal = 0;
        const projectIds = Object.keys(tree).sort((a, b) => tree[b].hours - tree[a].hours);
        for (const pid of projectIds) {
            const proj = tree[pid];
            const projKey = `project_${pid}`;
            const projExpanded = expanded[projKey] === true;
            const taskIds = Object.keys(proj.tasks).sort((a, b) => proj.tasks[b].hours - proj.tasks[a].hours);
            rows.push({
                key: projKey,
                project: proj.name,
                task: "",
                employee: "",
                hours: Math.round(proj.hours * 100) / 100,
                level: 0,
                hasChildren: taskIds.length > 0,
                expanded: projExpanded,
                rowClass: "hours-table-row-project",
                isTotal: false,
            });
            if (!projExpanded) continue;
            for (const tid of taskIds) {
                const task = proj.tasks[tid];
                const taskKey = `${projKey}_task_${tid}`;
                const taskExpanded = expanded[taskKey] === true;
                const emps = (task.employees || []).sort((a, b) => b.hours - a.hours);
                rows.push({
                    key: taskKey,
                    project: "",
                    task: task.name,
                    employee: "",
                    hours: Math.round(task.hours * 100) / 100,
                    level: 1,
                    hasChildren: emps.length > 0,
                    expanded: taskExpanded,
                    rowClass: "hours-table-row-task",
                    isTotal: false,
                });
                if (!taskExpanded) continue;
                for (const emp of emps) {
                    rows.push({
                        key: `${taskKey}_emp_${emp.id}`,
                        project: "",
                        task: "",
                        employee: emp.name,
                        hours: Math.round(emp.hours * 100) / 100,
                        level: 2,
                        hasChildren: false,
                        expanded: false,
                        rowClass: "hours-table-row-employee",
                        isTotal: false,
                    });
                }
                rows.push({
                    key: `${taskKey}_total`,
                    project: "",
                    task: "",
                    employee: "Total",
                    hours: Math.round(task.hours * 100) / 100,
                    level: 2,
                    hasChildren: false,
                    expanded: false,
                    rowClass: "hours-table-row-total",
                    isTotal: true,
                    totalCol: "employee",
                });
            }
            rows.push({
                key: `${projKey}_total`,
                project: "",
                task: "Total",
                employee: "",
                hours: Math.round(proj.hours * 100) / 100,
                level: 1,
                hasChildren: false,
                expanded: false,
                rowClass: "hours-table-row-total",
                isTotal: true,
                totalCol: "task",
            });
            grandTotal += proj.hours;
        }
        rows.push({
            key: "_grand_total",
            project: "Total",
            task: "",
            employee: "",
            hours: Math.round(grandTotal * 100) / 100,
            level: 0,
            hasChildren: false,
            expanded: false,
            rowClass: "hours-table-row-total",
            isTotal: true,
            totalCol: "project",
        });
        return rows;
    }

    getHoursPerOrganization() {
        return this.timesheet_state.charts.hours_per_organization || [];
    }

    getMaxHours(rows) {
        return Math.max(1, ...rows.map((row) => Number(row.hours || 0)));
    }

    getSeriesColor(seed) {
        return COMPANY_COLORS[Math.abs(Number(seed || 0)) % COMPANY_COLORS.length];
    }

    getEmployeeChartRows() {
        return this.getHoursPerEmployee();
    }

    getEmployeeChartTitle() {
        return "Hours Per Employee";
    }

    getEmployeeChartSubtitle() {
        return "Click a bar to filter";
    }

    getEmployeeChartEmptyState() {
        return "No employee hours for the selected filters.";
    }

    getEmployeeChartStageHeight(totalBars) {
        const bars = Math.max(1, Number(totalBars) || 1);
        const minHeight = 340;
        const perBar = 54;
        const base = 70;
        return `${Math.max(minHeight, (bars * perBar) + base)}px`;
    }

    getEmployeeChartPalette(mode, totalBars) {
        const palettes = {
            employees: ["#355070", "#3d5a80", "#2a9d8f", "#4d908e", "#577590", "#6d597a", "#457b9d", "#7a8b99"],
            tasks: ["#264653", "#2a9d8f", "#8ab17d", "#e9c46a", "#f4a261", "#e76f51", "#6c757d", "#588157"],
        };
        const palette = palettes[mode] || palettes.employees;
        const backgroundColor = [];
        const borderColor = [];

        for (let index = 0; index < totalBars; index++) {
            const color = palette[index % palette.length];
            backgroundColor.push(`${color}dd`);
            borderColor.push(color);
        }

        return { backgroundColor, borderColor };
    }

    getEmployeeChartRenderModel() {
        const employees = this.getHoursPerEmployee();
        return {
            mode: "employees",
            labels: employees.map((employee) => employee.employee_name || "Employee"),
            values: employees.map((employee) => Number(employee.hours || 0)),
            keys: employees.map((employee) => Number(employee.employee_id || 0)),
        };
    }

    getEmployeeChartConfig(chartModel) {
        const selectedEmployees = this.timesheet_state.selected_employees || [];
        const selectedId = selectedEmployees.length === 1 ? Number(selectedEmployees[0] || 0) : 0;
        const backgroundColor = chartModel.keys.map((id) =>
            selectedId && selectedId === id ? "rgba(79, 70, 229, 0.9)" : "rgba(99, 102, 241, 0.6)"
        );
        const borderColor = chartModel.keys.map((id) =>
            selectedId && selectedId === id ? "rgb(79, 70, 229)" : "rgba(99, 102, 241, 0.8)"
        );
        const borderWidth = chartModel.keys.map((id) => (selectedId && selectedId === id ? 3 : 1));
        return {
            type: "bar",
            data: {
                labels: chartModel.labels,
                datasets: [
                    {
                        label: "#Hours",
                        data: chartModel.values,
                        backgroundColor,
                        borderColor,
                        borderWidth,
                        barThickness: "flex",
                        maxBarThickness: 36,
                        hoverBackgroundColor: "rgba(79, 70, 229, 0.75)",
                        hoverBorderColor: "rgb(79, 70, 229)",
                        hoverBorderWidth: 2,
                    },
                ],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                layout: { padding: 4 },
                interaction: { mode: "index", axis: "y", intersect: false },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (canvas) canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (_event, elements) => {
                    if (!elements.length) return;
                    const employeeId = Number(chartModel.keys[elements[0].index] || 0);
                    if (employeeId) this.applyEmployeeChartFilter(employeeId);
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        displayColors: false,
                        backgroundColor: "rgba(30, 41, 59, 0.95)",
                        callbacks: {
                            label: (ctx) => {
                                const emp = (this.getHoursPerEmployee() || [])[ctx.dataIndex];
                                return `${emp?.employee_name || "Employee"}: ${this.formatHours(ctx.raw)} hrs`;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        position: "bottom",
                        beginAtZero: true,
                        title: { display: true, text: "Hours" },
                        grid: { color: "rgba(0,0,0,0.06)" },
                    },
                    y: {
                        position: "left",
                        display: true,
                        grid: { display: false },
                    },
                },
            },
        };
    }

    renderEmployeeChart() {
        const canvas = this.employeeChartCanvasRef.el;
        if (!canvas || !this.isHoursSummaryNav()) {
            this.destroyEmployeeChart();
            return;
        }

        const chartModel = this.getEmployeeChartRenderModel();
        if (!chartModel.values.length) {
            this.destroyEmployeeChart();
            return;
        }

        const fingerprint = JSON.stringify({
            mode: chartModel.mode,
            labels: chartModel.labels,
            values: chartModel.values,
        });

        if (this.employeeChart && this.employeeChartFingerprint === fingerprint) {
            this.employeeChart.resize();
            return;
        }

        if (this.employeeChart) {
            this.employeeChart.destroy();
        }
        this.employeeChart = new Chart(canvas, this.getEmployeeChartConfig(chartModel));
        this.employeeChartFingerprint = fingerprint;
    }

    destroyEmployeeChart() {
        if (this.employeeChart) {
            this.employeeChart.destroy();
            this.employeeChart = null;
        }
        this.employeeChartFingerprint = "";
    }

    renderProjectChart() {
        const canvas = this.projectChartCanvasRef.el;
        if (!canvas || !this.isHoursSummaryNav()) {
            this.destroyProjectChart();
            return;
        }

        const view = this.timesheet_state.project_chart_view || "bar";
        const fullData = this.getHoursPerProject();
        const chartModel = this.getProjectChartRenderModel();
        const hasData = view === "pie"
            ? fullData.length > 0
            : chartModel.values.length > 0;
        if (!hasData) {
            this.destroyProjectChart();
            return;
        }
        const fingerprint = JSON.stringify(
            view === "pie"
                ? { view, data: fullData.slice(0, 11).map((d) => ({ id: d.project_id, hours: d.hours })) }
                : {
                    mode: chartModel.mode,
                    labels: chartModel.labels,
                    values: chartModel.values,
                    selectedProject: this.timesheet_state.selected_project_drill || false,
                    view,
                }
        );

        if (this.projectChart && this.projectChartFingerprint === fingerprint) {
            this.projectChart.resize();
            return;
        }

        if (this.projectChart) {
            this.projectChart.destroy();
        }
        const config = view === "pie" && !this.timesheet_state.selected_project_drill
            ? this.getProjectChartPieConfig(chartModel)
            : this.getProjectChartConfig(chartModel);
        this.projectChart = new Chart(canvas, config);
        this.projectChartFingerprint = fingerprint;
    }

    destroyProjectChart() {
        if (this.projectChart) {
            this.projectChart.destroy();
            this.projectChart = null;
        }
        this.projectChartFingerprint = "";
    }

    onFullscreenChange() {
        const employeeCard = this.employeeChartCardRef.el;
        const lineCard = this.lineChartCardRef.el;
        const projectCard = this.projectChartCardRef.el;
        const organizationCard = this.organizationChartCardRef.el;
        const timesheetTableCard = this.timesheetTableCardRef.el;
        const fullscreenElement = document.fullscreenElement || document.webkitFullscreenElement || null;
        this.timesheet_state.employee_chart_fullscreen = Boolean(
            employeeCard && fullscreenElement === employeeCard
        );
        this.timesheet_state.line_chart_fullscreen = Boolean(
            lineCard && fullscreenElement === lineCard
        );
        this.timesheet_state.project_chart_fullscreen = Boolean(
            projectCard && fullscreenElement === projectCard
        );
        this.timesheet_state.organization_chart_fullscreen = Boolean(
            organizationCard && fullscreenElement === organizationCard
        );
        this.timesheet_state.timesheets_table_fullscreen = Boolean(
            timesheetTableCard && fullscreenElement === timesheetTableCard
        );
    }

    async toggleCardFullscreen(card) {
        if (!card) {
            return;
        }

        const fullscreenElement = document.fullscreenElement || document.webkitFullscreenElement || null;
        if (fullscreenElement === card) {
            if (document.exitFullscreen) {
                await document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            }
            return;
        }

        if (card.requestFullscreen) {
            await card.requestFullscreen();
        } else if (card.webkitRequestFullscreen) {
            card.webkitRequestFullscreen();
        }
    }

    async toggleEmployeeChartFullscreen() {
        const card = this.employeeChartCardRef.el;
        await this.toggleCardFullscreen(card);
    }

    async toggleLineChartFullscreen() {
        const card = this.lineChartCardRef.el;
        await this.toggleCardFullscreen(card);
    }

    async toggleProjectChartFullscreen() {
        const card = this.projectChartCardRef.el;
        await this.toggleCardFullscreen(card);
    }

    async toggleOrganizationChartFullscreen() {
        const card = this.organizationChartCardRef.el;
        await this.toggleCardFullscreen(card);
    }

    async toggleTimesheetTableFullscreen() {
        const card = this.timesheetTableCardRef.el;
        await this.toggleCardFullscreen(card);
    }

    getEmployeeHorizontalStyle(hours, maxHours, employeeId) {
        const ratio = maxHours ? Math.max(6, (Number(hours || 0) / maxHours) * 100) : 0;
        return `width:${ratio}%;background:${this.getSeriesColor(employeeId)};`;
    }

    clearProjectDrill() {
        this.timesheet_state.selected_project_drill = false;
    }

    getProjectDrillData() {
        const projectId = this.timesheet_state.selected_project_drill;
        if (!projectId) {
            return false;
        }
        return this.timesheet_state.charts.project_task_breakdown[String(projectId)] || false;
    }

    getProjectChartRows() {
        const projectDrill = this.getProjectDrillData();
        if (projectDrill) {
            return projectDrill.tasks || [];
        }
        return this.getHoursPerProject();
    }

    getProjectChartTitle() {
        const projectDrill = this.getProjectDrillData();
        if (projectDrill) {
            return `${projectDrill.project_name}: Hours Per Task`;
        }
        return "Hours Per Project";
    }

    getProjectChartSubtitle() {
        return "Click a bar to filter";
    }

    getProjectChartEmptyState() {
        if (this.getProjectDrillData()) {
            return "No task hours for the selected project with current filters.";
        }
        return "No project hours for the selected filters.";
    }

    getProjectChartStageHeight(totalBars) {
        const bars = Math.max(1, Number(totalBars) || 1);
        const minHeight = 340;
        const perBar = 54;
        const base = 70;
        return `${Math.max(minHeight, (bars * perBar) + base)}px`;
    }

    getProjectChartPalette(mode, totalBars) {
        const palettes = {
            projects: ["#335c81", "#3f7f98", "#2f6f74", "#4d7c59", "#7b8d5f", "#5f6f84", "#7f6a93", "#8f6372"],
            tasks: ["#355070", "#6d597a", "#b56576", "#e56b6f", "#587291", "#5b8f7e", "#8d6e63", "#6c757d"],
        };
        const palette = palettes[mode] || palettes.projects;
        const backgroundColor = [];
        const borderColor = [];

        for (let index = 0; index < totalBars; index++) {
            const color = palette[index % palette.length];
            backgroundColor.push(`${color}dd`);
            borderColor.push(color);
        }

        return { backgroundColor, borderColor };
    }

    getProjectChartRenderModel() {
        const projectDrill = this.getProjectDrillData();
        if (projectDrill) {
            const tasks = projectDrill.tasks || [];
            return {
                mode: "tasks",
                labels: tasks.map((task) => task.task_name || "Task"),
                values: tasks.map((task) => Number(task.hours || 0)),
                keys: tasks.map((task) => Number(task.task_id || 0)),
            };
        }

        const projects = this.getHoursPerProject();
        return {
            mode: "projects",
            labels: projects.map((project) => project.project_name || "Project"),
            values: projects.map((project) => Number(project.hours || 0)),
            keys: projects.map((project) => Number(project.project_id || 0)),
        };
    }

    getProjectChartPieConfig(chartModel) {
        const fullData = this.getHoursPerProject();
        const topN = 10;
        const top = fullData.slice(0, topN);
        const rest = fullData.slice(topN);
        const othersHours = rest.reduce((s, r) => s + (r.hours || 0), 0);
        const total = fullData.reduce((s, r) => s + (r.hours || 0), 0);
        const labels = top.map((d) => d.project_name || `Project ${d.project_id}`);
        const values = top.map((d) => d.hours);
        if (rest.length) {
            labels.push("Others");
            values.push(Math.round(othersHours * 100) / 100);
        }
        const colors = [
            "rgba(16, 185, 129, 0.8)", "rgba(245, 158, 11, 0.8)", "rgba(239, 68, 68, 0.8)",
            "rgba(59, 130, 246, 0.8)", "rgba(139, 92, 246, 0.8)", "rgba(236, 72, 153, 0.8)",
            "rgba(20, 184, 166, 0.8)", "rgba(251, 146, 60, 0.8)", "rgba(99, 102, 241, 0.8)",
            "rgba(34, 197, 94, 0.8)", "rgba(100, 116, 139, 0.8)",
        ];
        const pieData = top.map((d, i) => ({ ...d, index: i })).concat(
            rest.length ? [{ project_name: "Others", hours: othersHours }] : []
        );
        const pieSlicePlugin = getPieSliceLabelsPlugin();
        return {
            type: "pie",
            plugins: [pieSlicePlugin],
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.slice(0, labels.length),
                    borderColor: "#ffffff",
                    borderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                layout: { padding: 4 },
                plugins: {
                    legend: {
                        display: true,
                        position: "right",
                        labels: {
                            boxWidth: 10,
                            padding: 6,
                            font: { size: 9 },
                            formatter: (value, ctx) => {
                                const v = ctx.chart?.data?.datasets?.[0]?.data?.[ctx.dataIndex];
                                const summary = v != null ? formatCompactValue(v) : "";
                                return summary ? `${value} ${summary}` : value;
                            },
                        },
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const d = pieData[ctx.dataIndex];
                                const pct = total > 0 ? ((d.hours / total) * 100).toFixed(2) : "0";
                                return `${d?.project_name || "?"}: ${this.formatHours(d?.hours)} hrs (${pct}%)`;
                            },
                        },
                        backgroundColor: "rgba(30, 41, 59, 0.95)",
                    },
                },
            },
        };
    }

    getProjectChartConfig(chartModel) {
        return {
            type: "bar",
            data: {
                labels: chartModel.labels,
                datasets: [
                    {
                        label: "#Hours",
                        data: chartModel.values,
                        backgroundColor: "rgba(16, 185, 129, 0.6)",
                        borderColor: "rgb(16, 185, 129)",
                        borderWidth: 1,
                        barThickness: "flex",
                        maxBarThickness: 36,
                        hoverBackgroundColor: "rgba(16, 185, 129, 0.8)",
                        hoverBorderColor: "rgb(16, 185, 129)",
                        hoverBorderWidth: 2,
                    },
                ],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                layout: { padding: 4 },
                interaction: { mode: "index", axis: "y", intersect: false },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (canvas) canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (_event, elements) => {
                    if (!elements.length) return;
                    const activeIndex = elements[0].index;
                    if (chartModel.mode === "projects") {
                        const projectId = Number(chartModel.keys[activeIndex] || 0);
                        if (projectId) this.applyProjectChartDrill(projectId);
                        return;
                    }
                    const taskId = Number(chartModel.keys[activeIndex] || 0);
                    if (taskId) this.applyProjectTaskChartFilter(taskId);
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        displayColors: false,
                        backgroundColor: "rgba(30, 41, 59, 0.95)",
                        callbacks: {
                            label: (ctx) => {
                                const name = chartModel.labels[ctx.dataIndex] || "?";
                                return `${name}: ${this.formatHours(ctx.raw)} hrs`;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        position: "bottom",
                        beginAtZero: true,
                        title: { display: true, text: "#Hours" },
                        grid: { color: "rgba(0,0,0,0.06)" },
                    },
                    y: {
                        position: "left",
                        display: true,
                        grid: { display: false },
                    },
                },
            },
        };
    }

    getHoursOverTime() {
        return this.timesheet_state.charts.hours_over_time || [];
    }

    resetLineChartDrillContext() {
        this.timesheet_state.selected_month_drill = "";
        this.timesheet_state.selected_day_drill = "";
        this.timesheet_state.line_chart_previous_date_filters = false;
    }

    getLineChartTitle() {
        const selectedMonth = this.timesheet_state.selected_month_drill || "";
        if (!selectedMonth) {
            return "Hours Over Time";
        }
        return `Hours Over Time: ${this.formatMonthLabel(selectedMonth)}`;
    }

    getLineChartSubtitle() {
        return "Click to filter";
    }

    applyMonthChartDrill(monthKey) {
        const parsedMonth = DateTime.fromFormat(monthKey, "yyyy-MM");
        if (!parsedMonth.isValid) {
            return;
        }
        if (!this.timesheet_state.selected_month_drill) {
            this.timesheet_state.line_chart_previous_date_filters = {
                selected_year: this.timesheet_state.selected_year,
                selected_month: this.timesheet_state.selected_month,
                date_from: this.timesheet_state.date_from,
                date_to: this.timesheet_state.date_to,
            };
        }
        this.timesheet_state.selected_month_drill = monthKey;
        this.timesheet_state.selected_day_drill = "";
        this.timesheet_state.selected_year = parsedMonth.toFormat("yyyy");
        this.timesheet_state.selected_month = parsedMonth.toFormat("M");
        this.timesheet_state.date_from = parsedMonth.startOf("month").toISODate();
        this.timesheet_state.date_to = parsedMonth.endOf("month").toISODate();
        this.applyFilters();
    }

    applyDayChartDrill(dayKey) {
        const parsedDay = DateTime.fromISO(dayKey);
        if (!parsedDay.isValid) {
            return;
        }
        const isoDay = parsedDay.toISODate();
        if (!isoDay) {
            return;
        }
        this.timesheet_state.selected_day_drill = isoDay;
        this.timesheet_state.selected_year = parsedDay.toFormat("yyyy");
        this.timesheet_state.selected_month = parsedDay.toFormat("M");
        this.timesheet_state.date_from = isoDay;
        this.timesheet_state.date_to = isoDay;
        this.applyFilters();
    }

    clearMonthDrill() {
        const previousFilters = this.timesheet_state.line_chart_previous_date_filters;
        this.timesheet_state.selected_month_drill = "";
        this.timesheet_state.selected_day_drill = "";
        if (previousFilters) {
            this.timesheet_state.selected_year = previousFilters.selected_year || "all";
            this.timesheet_state.selected_month = previousFilters.selected_month || "all";
            this.timesheet_state.date_from = previousFilters.date_from || "";
            this.timesheet_state.date_to = previousFilters.date_to || "";
        } else {
            this.timesheet_state.date_from = "";
            this.timesheet_state.date_to = "";
        }
        this.timesheet_state.line_chart_previous_date_filters = false;
        this.applyFilters();
    }

    getLineChartRenderModel() {
        const rows = this.getHoursOverTime();
        const selectedMonth = this.timesheet_state.selected_month_drill || "";
        if (selectedMonth) {
            const monthRows = rows
                .filter((row) => String(row.date || "").slice(0, 7) === selectedMonth)
                .sort((a, b) => String(a.date || "").localeCompare(String(b.date || "")));
            return {
                mode: "days",
                keys: monthRows.map((row) => row.date),
                labels: monthRows.map((row) => this.formatDayShort(row.date)),
                values: monthRows.map((row) => Number(row.hours || 0)),
            };
        }

        const monthlyTotals = new Map();
        for (const row of rows) {
            const monthKey = String(row.date || "").slice(0, 7);
            if (!monthKey) {
                continue;
            }
            const currentTotal = Number(monthlyTotals.get(monthKey) || 0);
            monthlyTotals.set(monthKey, currentTotal + Number(row.hours || 0));
        }
        const monthKeys = Array.from(monthlyTotals.keys()).sort((a, b) => a.localeCompare(b));
        return {
            mode: "months",
            keys: monthKeys,
            labels: monthKeys.map((month) => this.formatMonthShortLabel(month)),
            values: monthKeys.map((month) => Number(monthlyTotals.get(month) || 0)),
        };
    }

    getLineChartConfig(chartModel) {
        const selectedDay = this.timesheet_state.selected_day_drill;
        const isDayMode = chartModel.mode === "days";
        return {
            type: "line",
            data: {
                labels: chartModel.labels,
                datasets: [
                    {
                        label: "#Hours",
                        data: chartModel.values,
                        borderColor: "rgb(16, 185, 129)",
                        backgroundColor: "rgba(16, 185, 129, 0.2)",
                        fill: "start",
                        tension: 0.2,
                        borderWidth: 2,
                        pointRadius: chartModel.keys.map((key) => (isDayMode && key === selectedDay ? 5 : 3)),
                        pointHoverRadius: 5,
                        pointBackgroundColor: chartModel.keys.map((key) => (isDayMode && key === selectedDay ? "#f59e0b" : "#10b981")),
                        pointBorderColor: chartModel.keys.map((key) => (isDayMode && key === selectedDay ? "#f97316" : "#ffffff")),
                        pointBorderWidth: 2,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                layout: { padding: 4 },
                interaction: { mode: "index", intersect: false },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (canvas) canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (event, elements, chart) => {
                    const activeElements = elements.length
                        ? elements
                        : chart.getElementsAtEventForMode(event, "index", { intersect: false }, true);
                    if (!activeElements.length) return;
                    const selectedKey = chartModel.keys[activeElements[0].index];
                    if (!selectedKey) return;
                    if (chartModel.mode === "months") {
                        this.applyMonthChartDrill(selectedKey);
                        return;
                    }
                    this.applyDayChartDrill(selectedKey);
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        displayColors: false,
                        backgroundColor: "rgba(30, 41, 59, 0.95)",
                        callbacks: {
                            title: (items) => {
                                const index = items?.[0]?.dataIndex;
                                if (!Number.isInteger(index)) return "";
                                return chartModel.mode === "months"
                                    ? this.formatMonthShortLabel(chartModel.keys[index])
                                    : this.formatDateLabel(chartModel.keys[index]);
                            },
                            label: (context) => `${this.formatHours(context.raw)} hrs`,
                        },
                    },
                },
                scales: {
                    x: {
                        position: "bottom",
                        title: { display: true, text: "Period" },
                        grid: { color: "rgba(0,0,0,0.06)" },
                    },
                    y: {
                        position: "left",
                        beginAtZero: true,
                        title: { display: true, text: "#Hours" },
                        grid: { color: "rgba(0,0,0,0.06)" },
                    },
                },
            },
        };
    }

    renderLineChart() {
        const canvas = this.lineChartCanvasRef.el;
        if (!canvas || !this.isHoursSummaryNav()) {
            this.destroyLineChart();
            return;
        }

        const chartModel = this.getLineChartRenderModel();
        if (!chartModel.values.length) {
            this.destroyLineChart();
            return;
        }

        const fingerprint = JSON.stringify({
            mode: chartModel.mode,
            keys: chartModel.keys,
            values: chartModel.values,
            selectedMonth: this.timesheet_state.selected_month_drill || "",
            selectedDay: this.timesheet_state.selected_day_drill || "",
        });

        if (this.lineChart && this.lineChartFingerprint === fingerprint) {
            this.lineChart.resize();
            return;
        }

        if (this.lineChart) {
            this.lineChart.destroy();
        }
        this.lineChart = new Chart(canvas, this.getLineChartConfig(chartModel));
        this.lineChartFingerprint = fingerprint;
    }

    destroyLineChart() {
        if (this.lineChart) {
            this.lineChart.destroy();
            this.lineChart = null;
        }
        this.lineChartFingerprint = "";
    }

    renderOrganizationChart() {
        const canvas = this.organizationChartCanvasRef.el;
        if (!canvas || !this.isHoursSummaryNav()) {
            this.destroyOrganizationChart();
            return;
        }

        const chartModel = this.getOrganizationChartModel();
        if (!chartModel.values.length) {
            this.destroyOrganizationChart();
            return;
        }

        const fingerprint = JSON.stringify({
            values: chartModel.values,
            ids: chartModel.ids,
            selectedOrganizations: this.timesheet_state.selected_organizations || [],
            selectedOrganization: this.timesheet_state.selected_organization_drill || false,
        });

        if (this.organizationChart && this.organizationChartFingerprint === fingerprint) {
            this.organizationChart.resize();
            return;
        }

        if (this.organizationChart) {
            this.organizationChart.destroy();
        }
        this.organizationChart = new Chart(canvas, this.getOrganizationChartConfig(chartModel));
        this.organizationChartFingerprint = fingerprint;
    }

    destroyOrganizationChart() {
        if (this.organizationChart) {
            this.organizationChart.destroy();
            this.organizationChart = null;
        }
        this.organizationChartFingerprint = "";
    }

    renderProjectsOrganizationChart() {
        const canvas = this.projectsOrganizationChartCanvasRef.el;
        if (!canvas || !this.isProjectsAnalysisNav()) {
            this.destroyProjectsOrganizationChart();
            return;
        }

        const chartModel = this.getProjectsOrganizationChartRenderModel();
        if (!chartModel.values.length) {
            this.destroyProjectsOrganizationChart();
            return;
        }

        const fingerprint = JSON.stringify({
            labels: chartModel.labels,
            values: chartModel.values,
            organizationIds: chartModel.organizationIds,
            selectedOrganizations: this.timesheet_state.selected_organizations || [],
        });

        if (this.projectsOrganizationChart && this.projectsOrganizationChartFingerprint === fingerprint) {
            this.projectsOrganizationChart.resize();
            return;
        }

        if (this.projectsOrganizationChart) {
            this.projectsOrganizationChart.destroy();
        }
        this.projectsOrganizationChart = new Chart(canvas, this.getProjectsOrganizationChartConfig(chartModel));
        this.projectsOrganizationChartFingerprint = fingerprint;
    }

    destroyProjectsOrganizationChart() {
        if (this.projectsOrganizationChart) {
            this.projectsOrganizationChart.destroy();
            this.projectsOrganizationChart = null;
        }
        this.projectsOrganizationChartFingerprint = "";
    }

    renderProjectsOrganizationPieChart() {
        const canvas = this.projectsOrganizationPieChartCanvasRef.el;
        if (!canvas || !this.isProjectsAnalysisNav()) {
            this.destroyProjectsOrganizationPieChart();
            return;
        }
        const chartModel = this.getProjectsOrganizationChartRenderModel();
        if (!chartModel.values.length) {
            this.destroyProjectsOrganizationPieChart();
            return;
        }
        const fingerprint = JSON.stringify({
            labels: chartModel.labels,
            values: chartModel.values,
        });
        if (this.projectsOrganizationPieChart && this.projectsOrganizationPieChartFingerprint === fingerprint) {
            this.projectsOrganizationPieChart.resize();
            return;
        }
        if (this.projectsOrganizationPieChart) {
            this.projectsOrganizationPieChart.destroy();
        }
        this.projectsOrganizationPieChart = new Chart(canvas, this.getProjectsOrganizationPieConfig(chartModel));
        this.projectsOrganizationPieChartFingerprint = fingerprint;
    }

    destroyProjectsOrganizationPieChart() {
        if (this.projectsOrganizationPieChart) {
            this.projectsOrganizationPieChart.destroy();
            this.projectsOrganizationPieChart = null;
        }
        this.projectsOrganizationPieChartFingerprint = "";
    }

    renderProjectsHoursPerProjectChart() {
        const canvas = this.projectsHoursPerProjectChartCanvasRef.el;
        if (!canvas || !this.isProjectsAnalysisNav()) {
            this.destroyProjectsHoursPerProjectChart();
            return;
        }
        const fullData = this.getHoursPerProject();
        if (!fullData.length) {
            this.destroyProjectsHoursPerProjectChart();
            return;
        }
        const chartModel = {
            labels: fullData.map((d) => d.project_name || `Project ${d.project_id}`),
            values: fullData.map((d) => Number(d.hours || 0)),
            keys: fullData.map((d) => Number(d.project_id || 0)),
        };
        const fingerprint = JSON.stringify({
            labels: chartModel.labels,
            values: chartModel.values,
        });
        if (this.projectsHoursPerProjectChart && this.projectsHoursPerProjectChartFingerprint === fingerprint) {
            this.projectsHoursPerProjectChart.resize();
            return;
        }
        if (this.projectsHoursPerProjectChart) {
            this.projectsHoursPerProjectChart.destroy();
        }
        this.projectsHoursPerProjectChart = new Chart(canvas, this.getProjectsHoursPerProjectChartConfig(chartModel));
        this.projectsHoursPerProjectChartFingerprint = fingerprint;
    }

    destroyProjectsHoursPerProjectChart() {
        if (this.projectsHoursPerProjectChart) {
            this.projectsHoursPerProjectChart.destroy();
            this.projectsHoursPerProjectChart = null;
        }
        this.projectsHoursPerProjectChartFingerprint = "";
    }

    renderProjectsOverTimeChart() {
        const canvas = this.projectsOverTimeChartCanvasRef.el;
        if (!canvas || !this.isProjectsAnalysisNav()) {
            this.destroyProjectsOverTimeChart();
            return;
        }

        const chartModel = this.getProjectsOverTimeRenderModel();
        if (!chartModel.values.length) {
            this.destroyProjectsOverTimeChart();
            return;
        }

        const fingerprint = JSON.stringify({
            mode: chartModel.mode,
            keys: chartModel.keys,
            values: chartModel.values,
            selectedMonth: this.timesheet_state.selected_month_drill || "",
            selectedDay: this.timesheet_state.selected_day_drill || "",
        });

        if (this.projectsOverTimeChart && this.projectsOverTimeChartFingerprint === fingerprint) {
            this.projectsOverTimeChart.resize();
            return;
        }

        if (this.projectsOverTimeChart) {
            this.projectsOverTimeChart.destroy();
        }
        this.projectsOverTimeChart = new Chart(canvas, this.getProjectsOverTimeChartConfig(chartModel));
        this.projectsOverTimeChartFingerprint = fingerprint;
    }

    destroyProjectsOverTimeChart() {
        if (this.projectsOverTimeChart) {
            this.projectsOverTimeChart.destroy();
            this.projectsOverTimeChart = null;
        }
        this.projectsOverTimeChartFingerprint = "";
    }

    renderEmployeesProjectsChart() {
        const canvas = this.employeesProjectsChartCanvasRef.el;
        if (!canvas || !this.isEmployeesAnalysisNav()) {
            this.destroyEmployeesProjectsChart();
            return;
        }

        const chartModel = this.getEmployeesProjectsChartRenderModel();
        if (!chartModel.values.length) {
            this.destroyEmployeesProjectsChart();
            return;
        }

        const fingerprint = JSON.stringify({
            labels: chartModel.labels,
            values: chartModel.values,
            employeeIds: chartModel.employeeIds,
            selectedEmployees: this.timesheet_state.selected_employees || [],
        });

        if (this.employeesProjectsChart && this.employeesProjectsChartFingerprint === fingerprint) {
            this.employeesProjectsChart.resize();
            return;
        }

        if (this.employeesProjectsChart) {
            this.employeesProjectsChart.destroy();
        }
        this.employeesProjectsChart = new Chart(canvas, this.getEmployeesProjectsChartConfig(chartModel));
        this.employeesProjectsChartFingerprint = fingerprint;
    }

    destroyEmployeesProjectsChart() {
        if (this.employeesProjectsChart) {
            this.employeesProjectsChart.destroy();
            this.employeesProjectsChart = null;
        }
        this.employeesProjectsChartFingerprint = "";
    }

    renderEmployeesHoursPerEmployeeChart() {
        const canvas = this.employeesHoursPerEmployeeChartCanvasRef.el;
        const view = this.timesheet_state.employee_hours_per_employee_view || "bar";
        if (!canvas || !this.isEmployeesAnalysisNav() || view !== "bar") {
            this.destroyEmployeesHoursPerEmployeeChart();
            return;
        }

        const chartModel = this.getEmployeeChartRenderModel();
        if (!chartModel.values.length) {
            this.destroyEmployeesHoursPerEmployeeChart();
            return;
        }

        const fingerprint = JSON.stringify({
            labels: chartModel.labels,
            values: chartModel.values,
            keys: chartModel.keys,
            selectedEmployees: this.timesheet_state.selected_employees || [],
        });

        if (this.employeesHoursPerEmployeeChart && this.employeesHoursPerEmployeeChartFingerprint === fingerprint) {
            this.employeesHoursPerEmployeeChart.resize();
            return;
        }

        if (this.employeesHoursPerEmployeeChart) {
            this.employeesHoursPerEmployeeChart.destroy();
        }
        this.employeesHoursPerEmployeeChart = new Chart(canvas, this.getEmployeesHoursPerEmployeeChartConfig(chartModel));
        this.employeesHoursPerEmployeeChartFingerprint = fingerprint;
    }

    destroyEmployeesHoursPerEmployeeChart() {
        if (this.employeesHoursPerEmployeeChart) {
            this.employeesHoursPerEmployeeChart.destroy();
            this.employeesHoursPerEmployeeChart = null;
        }
        this.employeesHoursPerEmployeeChartFingerprint = "";
    }

    renderEmployeesOrganizationPieChart() {
        const canvas = this.employeesOrganizationPieChartCanvasRef.el;
        if (!canvas || !this.isEmployeesAnalysisNav()) {
            this.destroyEmployeesOrganizationPieChart();
            return;
        }

        const chartModel = this.getEmployeesOrganizationPieRenderModel();
        if (!chartModel.values.length) {
            this.destroyEmployeesOrganizationPieChart();
            return;
        }

        const fingerprint = JSON.stringify({
            labels: chartModel.labels,
            values: chartModel.values,
            organizationIds: chartModel.organizationIds,
        });

        if (this.employeesOrganizationPieChart && this.employeesOrganizationPieChartFingerprint === fingerprint) {
            this.employeesOrganizationPieChart.resize();
            return;
        }

        if (this.employeesOrganizationPieChart) {
            this.employeesOrganizationPieChart.destroy();
        }
        this.employeesOrganizationPieChart = new Chart(canvas, this.getEmployeesOrganizationPieConfig(chartModel));
        this.employeesOrganizationPieChartFingerprint = fingerprint;
    }

    destroyEmployeesOrganizationPieChart() {
        if (this.employeesOrganizationPieChart) {
            this.employeesOrganizationPieChart.destroy();
            this.employeesOrganizationPieChart = null;
        }
        this.employeesOrganizationPieChartFingerprint = "";
    }

    renderEmployeesOverTimeChart() {
        const canvas = this.employeesOverTimeChartCanvasRef.el;
        if (!canvas || !this.isEmployeesAnalysisNav()) {
            this.destroyEmployeesOverTimeChart();
            return;
        }

        const chartModel = this.getEmployeesOverTimeRenderModel();
        if (!chartModel.values.length) {
            this.destroyEmployeesOverTimeChart();
            return;
        }

        const fingerprint = JSON.stringify({
            mode: chartModel.mode,
            keys: chartModel.keys,
            values: chartModel.values,
            selectedMonth: this.timesheet_state.selected_month_drill || "",
            selectedDay: this.timesheet_state.selected_day_drill || "",
        });

        if (this.employeesOverTimeChart && this.employeesOverTimeChartFingerprint === fingerprint) {
            this.employeesOverTimeChart.resize();
            return;
        }

        if (this.employeesOverTimeChart) {
            this.employeesOverTimeChart.destroy();
        }
        this.employeesOverTimeChart = new Chart(canvas, this.getEmployeesOverTimeChartConfig(chartModel));
        this.employeesOverTimeChartFingerprint = fingerprint;
    }

    destroyEmployeesOverTimeChart() {
        if (this.employeesOverTimeChart) {
            this.employeesOverTimeChart.destroy();
            this.employeesOverTimeChart = null;
        }
        this.employeesOverTimeChartFingerprint = "";
    }

    clearDayDrill() {
        const selectedMonth = this.timesheet_state.selected_month_drill || "";
        if (selectedMonth) {
            const parsedMonth = DateTime.fromFormat(selectedMonth, "yyyy-MM");
            if (parsedMonth.isValid) {
                this.timesheet_state.selected_day_drill = "";
                this.timesheet_state.selected_year = parsedMonth.toFormat("yyyy");
                this.timesheet_state.selected_month = parsedMonth.toFormat("M");
                this.timesheet_state.date_from = parsedMonth.startOf("month").toISODate();
                this.timesheet_state.date_to = parsedMonth.endOf("month").toISODate();
                this.applyFilters();
                return;
            }
        }
        this.timesheet_state.selected_day_drill = "";
    }

    getDayDrillData() {
        const day = this.timesheet_state.selected_day_drill;
        if (!day) {
            return false;
        }
        return this.timesheet_state.charts.day_breakdown[String(day)] || false;
    }

    getOrganizationChartRows() {
        return this.getHoursPerOrganization();
    }

    getOrganizationChartPalette(totalRows) {
        const palette = [
            "#10b981", "#ef4444", "#22c55e", "#f59e0b", "#3b82f6", "#8b5cf6",
            "#ec4899", "#14b8a6", "#fb923c", "#64748b",
        ];
        const backgroundColor = [];
        const borderColor = [];

        for (let index = 0; index < totalRows; index++) {
            const hex = palette[index % palette.length];
            backgroundColor.push(`${hex}dd`);
            borderColor.push(hex);
        }

        return { backgroundColor, borderColor };
    }

    getOrganizationChartModel() {
        const rows = this.getOrganizationChartRows();
        const total = rows.reduce((sum, row) => sum + Number(row.hours || 0), 0);
        if (!total) {
            return {
                rows: [],
                ids: [],
                labels: [],
                values: [],
                backgroundColor: [],
                borderColor: [],
                total: 0,
            };
        }

        const ids = rows.map((row) => Number(row.organization_id || 0));
        const labels = rows.map((row) => row.organization_name || "Organization");
        const values = rows.map((row) => Number(row.hours || 0));
        const palette = this.getOrganizationChartPalette(rows.length);
        const selectedOrganizations = this.timesheet_state.selected_organizations || [];
        const selectedId = selectedOrganizations.length === 1
            ? Number(selectedOrganizations[0] || 0)
            : Number(this.timesheet_state.selected_organization_drill || 0);

        const legendRows = rows.map((row, index) => {
            const organizationId = Number(row.organization_id || 0);
            return {
                organization_id: organizationId,
                organization_name: row.organization_name || "Organization",
                hours: Number(row.hours || 0),
                percentage: (Number(row.hours || 0) / total) * 100,
                color: palette.borderColor[index],
                active: selectedId === organizationId,
            };
        });

        return {
            rows: legendRows,
            ids,
            labels,
            values,
            backgroundColor: palette.backgroundColor,
            borderColor: palette.borderColor,
            total,
        };
    }

    getOrganizationChartTotalHours() {
        return this.getOrganizationChartModel().total;
    }

    getOrganizationPieDepthColor(color) {
        const rawColor = String(color || "").trim().replace("#", "");
        const hex = rawColor.length >= 6 ? rawColor.slice(0, 6) : "6b7280";
        const red = Number.parseInt(hex.slice(0, 2), 16);
        const green = Number.parseInt(hex.slice(2, 4), 16);
        const blue = Number.parseInt(hex.slice(4, 6), 16);
        if (!Number.isFinite(red) || !Number.isFinite(green) || !Number.isFinite(blue)) {
            return "rgba(75, 85, 99, 0.9)";
        }
        return `rgba(${Math.round(red * 0.62)}, ${Math.round(green * 0.62)}, ${Math.round(blue * 0.62)}, 0.9)`;
    }

    getOrganizationPie3DPlugin(depth = 14) {
        return {
            id: "organizationPie3D",
            beforeDatasetDraw: (chart, args) => {
                if (args.index !== 0) {
                    return;
                }
                const dataset = chart.data.datasets?.[0];
                const meta = chart.getDatasetMeta(0);
                if (!dataset || !meta?.data?.length) {
                    return;
                }
                const borderColors = Array.isArray(dataset.borderColor) ? dataset.borderColor : [];
                const { ctx } = chart;
                ctx.save();
                for (let layer = depth; layer >= 1; layer--) {
                    for (let index = 0; index < meta.data.length; index++) {
                        const arc = meta.data[index];
                        const { x, y, startAngle, endAngle, outerRadius } = arc.getProps(
                            ["x", "y", "startAngle", "endAngle", "outerRadius"],
                            true
                        );
                        ctx.beginPath();
                        ctx.moveTo(x, y + layer);
                        ctx.arc(x, y + layer, outerRadius, startAngle, endAngle);
                        ctx.closePath();
                        const baseColor = borderColors[index] || "#6b7280";
                        ctx.fillStyle = this.getOrganizationPieDepthColor(baseColor);
                        ctx.fill();
                    }
                }
                ctx.restore();
            },
        };
    }

    getOrganizationChartConfig(chartModel) {
        const orgColors = [
            "rgba(16, 185, 129, 0.8)", "rgba(239, 68, 68, 0.8)", "rgba(34, 197, 94, 0.8)",
            "rgba(245, 158, 11, 0.8)", "rgba(59, 130, 246, 0.8)", "rgba(139, 92, 246, 0.8)",
            "rgba(236, 72, 153, 0.8)", "rgba(20, 184, 166, 0.8)", "rgba(251, 146, 60, 0.8)",
        ];
        const data = this.getHoursPerOrganization();
        const pieSlicePlugin = getPieSliceLabelsPlugin();
        return {
            type: "pie",
            plugins: [pieSlicePlugin],
            data: {
                labels: chartModel.labels,
                datasets: [{
                    data: chartModel.values,
                    backgroundColor: orgColors.slice(0, chartModel.labels.length),
                    borderColor: "#ffffff",
                    borderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                layout: { padding: 4 },
                onHover: (event, elements) => {
                    const canvas = event?.native?.target;
                    if (canvas) canvas.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (_event, elements) => {
                    if (!elements.length) return;
                    const index = elements[0].index;
                    const organizationId = Number(chartModel.ids[index] || 0);
                    if (organizationId) this.applyOrganizationChartFilter(organizationId);
                },
                plugins: {
                    legend: {
                        display: true,
                        position: "right",
                        labels: {
                            boxWidth: 10,
                            padding: 6,
                            font: { size: 9 },
                            formatter: (value, ctx) => {
                                const v = ctx.chart?.data?.datasets?.[0]?.data?.[ctx.dataIndex];
                                const summary = v != null ? formatCompactValue(v) : "";
                                return summary ? `${value} ${summary}` : value;
                            },
                        },
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const d = data[ctx.dataIndex];
                                const total = chartModel.total || 1;
                                const pct = total > 0 ? ((Number(d?.hours || 0) / total) * 100).toFixed(2) : "0";
                                return `${d?.organization_name || "?"}: ${this.formatHours(d?.hours)} hrs (${pct}%)`;
                            },
                        },
                        backgroundColor: "rgba(30, 41, 59, 0.95)",
                    },
                },
            },
        };
    }

    isOrganizationFocused(organizationId) {
        const selectedOrganizations = this.timesheet_state.selected_organizations || [];
        if (selectedOrganizations.length === 1) {
            return Number(selectedOrganizations[0] || 0) === Number(organizationId || 0);
        }
        return Number(this.timesheet_state.selected_organization_drill || 0) === Number(organizationId || 0);
    }

    toggleOrganizationDrill(organizationId) {
        this.applyOrganizationChartFilter(organizationId);
    }

    getOrganizationDrillData() {
        const selectedOrganizations = this.timesheet_state.selected_organizations || [];
        const focusId = selectedOrganizations.length === 1
            ? Number(selectedOrganizations[0] || 0)
            : Number(this.timesheet_state.selected_organization_drill || 0);
        if (!focusId) {
            return false;
        }
        const rows = this.getHoursPerOrganization();
        const total = rows.reduce((sum, row) => sum + Number(row.hours || 0), 0);
        const selected = rows.find((row) => Number(row.organization_id) === focusId);
        if (!selected || !total) {
            return false;
        }
        return {
            organization_id: selected.organization_id,
            organization_name: selected.organization_name,
            hours: Number(selected.hours || 0),
            percentage: (Number(selected.hours || 0) / total) * 100,
        };
    }

    onOrganizationSliceClick(ev) {
        const organizationId = Number(ev.currentTarget.dataset.organizationId || 0);
        if (organizationId) {
            this.applyOrganizationChartFilter(organizationId);
        }
    }

    clearOrganizationDrill() {
        const hasSelectedOrganizations = Boolean((this.timesheet_state.selected_organizations || []).length);
        this.timesheet_state.selected_organization_drill = false;
        if (hasSelectedOrganizations) {
            this.timesheet_state.selected_organizations = [];
            this.applyFilters();
        }
    }
}

TimesheetDashboard.template = "TimesheetDashBoardMain";

registry.category("actions").add(
    "timesheet_dashboard_main",
    TimesheetDashboard
);
