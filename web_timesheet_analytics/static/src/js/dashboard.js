/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";
import { loadBundle } from "@web/core/assets";
import publicWidget from "@web/legacy/js/public/public_widget";

const MONTHS = [
    { value: 1, label: "January" },
    { value: 2, label: "February" },
    { value: 3, label: "March" },
    { value: 4, label: "April" },
    { value: 5, label: "May" },
    { value: 6, label: "June" },
    { value: 7, label: "July" },
    { value: 8, label: "August" },
    { value: 9, label: "September" },
    { value: 10, label: "October" },
    { value: 11, label: "November" },
    { value: 12, label: "December" },
];

function escapeHtml(value) {
    return $("<div/>").text(value || "").html();
}

publicWidget.registry.WebTimesheetAnalyticsDashboard = publicWidget.Widget.extend({
    selector: ".o_wta_dashboard",
    events: {
        "click #wta_apply_filters": "_onApplyFilters",
        "click #wta_clear_filters": "_onClearFilters",
    },

    async start() {
        this.charts = {};
        const hasEmployee = Number(this.el.dataset.hasEmployee || 0) === 1;
        if (!hasEmployee) {
            return this._super(...arguments);
        }
        await loadBundle("web.chartjs_lib");
        await this._fetchAndRender();
        return this._super(...arguments);
    },

    async _onApplyFilters(ev) {
        ev.preventDefault();
        await this._fetchAndRender();
    },

    async _onClearFilters(ev) {
        ev.preventDefault();
        this.$("#wta_project_filter").val("all");
        this.$("#wta_task_filter").val("all");
        this.$("#wta_organization_filter").val("all");
        this.$("#wta_year_filter").val("all");
        this.$("#wta_month_filter").val("all");
        this.$("#wta_date_from").val("");
        this.$("#wta_date_to").val("");
        await this._fetchAndRender();
    },

    _getPayload() {
        const valOrFalse = (selector) => {
            const value = this.$(selector).val();
            return value && value !== "all" ? value : false;
        };

        return {
            project_id: valOrFalse("#wta_project_filter"),
            task_id: valOrFalse("#wta_task_filter"),
            organization_id: valOrFalse("#wta_organization_filter"),
            year: valOrFalse("#wta_year_filter"),
            month: valOrFalse("#wta_month_filter"),
            date_from: this.$("#wta_date_from").val() || false,
            date_to: this.$("#wta_date_to").val() || false,
        };
    },

    async _fetchAndRender() {
        const data = await jsonrpc("/my/timesheet-analytics/data", this._getPayload());
        this._renderKpis(data);
        this._renderFilters(data);
        this._renderTable(data.timesheet_rows || []);
        this._renderCharts(data.charts || {});
    },

    _fillSelect(selector, items, currentValue, allLabel) {
        const $select = this.$(selector);
        const selectedValue = currentValue || $select.val() || "all";
        $select.empty();
        $select.append(`<option value="all">${allLabel}</option>`);
        (items || []).forEach((item) => {
            const id = String(item.id);
            const name = item.name || "";
            $select.append(`<option value="${id}">${escapeHtml(name)}</option>`);
        });
        $select.val(selectedValue);
        if (!$select.val()) {
            $select.val("all");
        }
    },

    _renderFilters(data) {
        this._fillSelect("#wta_project_filter", data.projects, this.$("#wta_project_filter").val(), "All Projects");
        this._fillSelect("#wta_task_filter", data.tasks, this.$("#wta_task_filter").val(), "All Tasks");
        this._fillSelect("#wta_organization_filter", data.organizations, this.$("#wta_organization_filter").val(), "All Organizations");

        const $year = this.$("#wta_year_filter");
        const selectedYear = $year.val() || "all";
        $year.empty().append('<option value="all">All Years</option>');
        (data.available_years || []).forEach((year) => $year.append(`<option value="${year}">${year}</option>`));
        $year.val(selectedYear);
        if (!$year.val()) {
            $year.val("all");
        }

        const $month = this.$("#wta_month_filter");
        const selectedMonth = $month.val() || "all";
        const monthsSet = new Set((data.available_months || []).map((m) => Number(m)));
        $month.empty().append('<option value="all">All Months</option>');
        MONTHS.filter((m) => !monthsSet.size || monthsSet.has(m.value)).forEach((month) => {
            $month.append(`<option value="${month.value}">${month.label}</option>`);
        });
        $month.val(selectedMonth);
        if (!$month.val()) {
            $month.val("all");
        }

        this.$("#wta_date_from").attr("min", data.available_date_min || null).attr("max", data.available_date_max || null);
        this.$("#wta_date_to").attr("min", data.available_date_min || null).attr("max", data.available_date_max || null);
    },

    _renderKpis(data) {
        this.$("#wta_projects_count").text(data.projects_count || 0);
        this.$("#wta_tasks_count").text(data.tasks_count || 0);
        this.$("#wta_timesheets_count").text(data.timesheets_count || 0);
        this.$("#wta_total_hours").text(Number(data.total_hours || 0).toFixed(2));
    },

    _renderTable(rows) {
        const $body = this.$("#wta_table tbody");
        $body.empty();

        if (!rows.length) {
            $body.append('<tr><td colspan="7" class="text-center text-muted py-3">No timesheet entries found.</td></tr>');
            return;
        }

        rows.forEach((row) => {
            $body.append(`
                <tr>
                    <td>${escapeHtml(row.date || "")}</td>
                    <td>${escapeHtml(row.employee || "")}</td>
                    <td>${escapeHtml(row.organization || "")}</td>
                    <td>${escapeHtml(row.project || "")}</td>
                    <td>${escapeHtml(row.task || "")}</td>
                    <td>${escapeHtml(row.description || "")}</td>
                    <td class="text-end">${Number(row.hours || 0).toFixed(2)}</td>
                </tr>
            `);
        });
    },

    _destroyChart(key) {
        if (this.charts[key]) {
            this.charts[key].destroy();
            this.charts[key] = null;
        }
    },

    _renderCharts(charts) {
        const projectRows = charts.hours_per_project || [];
        const orgRows = charts.hours_per_organization || [];
        const timeRows = charts.hours_over_time || [];

        this._destroyChart("project");
        this._destroyChart("organization");
        this._destroyChart("time");

        const projectCtx = this.el.querySelector("#wta_project_chart");
        const orgCtx = this.el.querySelector("#wta_org_chart");
        const timeCtx = this.el.querySelector("#wta_time_chart");

        this.charts.project = new Chart(projectCtx, {
            type: "bar",
            data: {
                labels: projectRows.map((item) => item.project_name),
                datasets: [{
                    label: "Hours",
                    data: projectRows.map((item) => Number(item.hours || 0)),
                    backgroundColor: "#3b82f6",
                }],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });

        this.charts.organization = new Chart(orgCtx, {
            type: "doughnut",
            data: {
                labels: orgRows.map((item) => item.organization_name),
                datasets: [{
                    data: orgRows.map((item) => Number(item.hours || 0)),
                    backgroundColor: ["#2563eb", "#0891b2", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"],
                }],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });

        this.charts.time = new Chart(timeCtx, {
            type: "line",
            data: {
                labels: timeRows.map((item) => item.date),
                datasets: [{
                    label: "Hours",
                    data: timeRows.map((item) => Number(item.hours || 0)),
                    borderColor: "#0f766e",
                    backgroundColor: "rgba(15,118,110,0.15)",
                    fill: true,
                    tension: 0.3,
                }],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });
    },

    destroy() {
        this._destroyChart("project");
        this._destroyChart("organization");
        this._destroyChart("time");
        return this._super(...arguments);
    },
});
