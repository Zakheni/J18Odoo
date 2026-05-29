/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from "@web/core/network/rpc_service";
import Dialog from "@web/legacy/js/core/dialog";
import publicWidget from "@web/legacy/js/public/public_widget";

let token = null;

publicWidget.registry.FavoriteItem = publicWidget.Widget.extend({
    selector: ".new_timesheet",
    start: function () {
        this.$taskSelect = this.$("#ts_task_id");
        this.$project = "";
        this.$employee = this.el.querySelector("#employee_id");
        this.$currentSelectedIndex = this.$employee ? this.$employee.selectedIndex : null;
        return this._super.apply(this, arguments);
    },
    events: {
        'change select[name="project"]': "_onChangeProject",
        'change select[name="employee_id"]': "_onChangeEmployee",
        'click button[id="savetimesheet"]': "_onClickSavetimesheet",
    },

    _onClickSavetimesheet: function (ev) {
        const duration = Number.parseFloat($('input[name="duration"]').val() || 0);
        if (duration === 0.0) {
            alert(_t("Timesheet hours should be greater than 0.0"));
            ev.preventDefault();
            return;
        }
        const taskId = this.$taskSelect.val();
        if (!taskId) {
            alert(_t("Please select a task for the chosen project."));
            ev.preventDefault();
        }
    },

    _onChangeEmployee: function (ev) {
        ev.preventDefault();
        if (this.$employee && this.$currentSelectedIndex !== null) {
            this.$employee.selectedIndex = this.$currentSelectedIndex;
        }
    },

    _onChangeProject: function (ev) {
        this.$project = $(ev.currentTarget).val();
        const $task = this.$taskSelect;
        $task.empty();
        if (!this.$project) {
            $task.append(
                $("<option>", { value: "", text: _t("Select a project first") }),
            );
            return;
        }
        $task.append($("<option>", { value: "", text: _t("Choose a task") }));
        jsonrpc("/timesheet/form/project", {
            project_id: this.$project,
        }).then((data) => {
            if (data) {
                $("#ts_company_id").val(data.ts_company_id || "");
            }
        });
        jsonrpc("/timesheet/form/tasks", {
            project_id: parseInt(this.$project, 10),
        }).then((data) => {
            const tasks = (data && data.tasks) || [];
            tasks.forEach((t) => {
                $task.append($("<option>", { value: t.id, text: t.name }));
            });
        });
    },
});

publicWidget.registry.TimesheetTopScroll = publicWidget.Widget.extend({
    selector: ".o_portal_my_doc_table",
    start: function () {
        this.$scrollHost = this.$el.closest(".table-responsive");
        this.$timesheetBody = this.$el.find("tbody.tmk_timesheet_table");
        if (!this.$scrollHost.length || !this.$timesheetBody.length) {
            return this._super.apply(this, arguments);
        }

        this.$topScrollbar = this.$scrollHost.prev(".wt-top-scrollbar");
        if (!this.$topScrollbar.length) {
            this.$topScrollbar = $("<div/>", {
                class: "wt-top-scrollbar",
            }).append($("<div/>", {
                class: "wt-top-scrollbar-inner",
            }));
            this.$scrollHost.before(this.$topScrollbar);
        }

        this.$topScrollbarInner = this.$topScrollbar.find(".wt-top-scrollbar-inner");

        this._onTopScroll = this._syncFromTop.bind(this);
        this._onHostScroll = this._syncFromTable.bind(this);
        this.$topScrollbar.on("scroll", this._onTopScroll);
        this.$scrollHost.on("scroll", this._onHostScroll);

        this._resizeEventName = `resize.web_timesheet_top_scroll_${this.cid}`;
        this._updateTopScrollbar = this._updateTopScrollbar.bind(this);
        $(window).on(this._resizeEventName, this._updateTopScrollbar);
        setTimeout(this._updateTopScrollbar, 0);

        return this._super.apply(this, arguments);
    },

    _syncFromTop: function () {
        this.$scrollHost.scrollLeft(this.$topScrollbar.scrollLeft());
    },

    _syncFromTable: function () {
        this.$topScrollbar.scrollLeft(this.$scrollHost.scrollLeft());
    },

    _updateTopScrollbar: function () {
        const tableWidth = this.el.scrollWidth || 0;
        const container = this.$scrollHost.get(0);
        const containerWidth = container ? container.clientWidth : 0;

        this.$topScrollbarInner.width(tableWidth);
        this.$topScrollbar.toggleClass("d-none", tableWidth <= containerWidth + 1);
        this.$topScrollbar.scrollLeft(this.$scrollHost.scrollLeft());
    },

    destroy: function () {
        if (this.$topScrollbar && this._onTopScroll) {
            this.$topScrollbar.off("scroll", this._onTopScroll);
        }
        if (this.$scrollHost && this._onHostScroll) {
            this.$scrollHost.off("scroll", this._onHostScroll);
        }
        if (this._resizeEventName) {
            $(window).off(this._resizeEventName);
        }
        return this._super.apply(this, arguments);
    },
});

$(document).on("click", ".sheet_select #date_id", function () {
    $("#contact").trigger("click");
});

$(document).on("click", ".tmk_timesheet_table #delete_timesheet", function (event) {
    const $row = $(event.currentTarget).closest("tr");
    const timesheetId = $row.find('input[name="timesheet_id"]').val();
    new Dialog(this, {
        size: "medium",
        classes: "text-center",
        title: _t("Delete Timesheet"),
        $content: $(`<div><p>${_t("Do you really want to remove this timesheet?")}</p></div>`),
        technical: false,
        buttons: [
            {
                text: _t("No"),
                classes: "btn-danger",
                close: true,
            },
            {
                text: _t("Yes"),
                classes: "btn-primary",
                click: function () {
                    jsonrpc("/my/delete_timesheet", {
                        timesheet_id: timesheetId,
                    }).then(function () {
                        window.location.href = "/my/timesheets";
                    });
                },
                close: true,
            },
        ],
    }).open();
});

$(document).on("click", ".tmk_timesheet_table #edit_timesheet", function (event) {
    const $row = $(event.currentTarget).closest("tr");
    if (token === null || token === 0) {
        token = 1;
        $row.addClass("bg-light");
        $row.find("#ts_date, #ts_desc, #ts_duration").attr("contenteditable", "true");
        $row.find("#ts_desc").trigger("focus");
        $row.find("#edit_timesheet").addClass("d-none");
        $row.find("#save_timesheet").removeClass("d-none");
        $row.find(".default_display_project").addClass("d-none");
        $row.find(".edit_project").removeClass("d-none");
        $row.find(".default_display_task").addClass("d-none");
        $row.find(".edit_task").removeClass("d-none");
        $row.find(".edit-expenditure").removeClass("d-none");
        $row.find(".saved_exp").addClass("d-none");
        return;
    }

    new Dialog(this, {
        size: "medium",
        title: _t("Error"),
        $content: $(`<div><p>${_t("You can not edit multiple timesheets at once.")}</p></div>`),
        technical: false,
        buttons: [{
            text: _t("Ok"),
            classes: "btn-danger",
            close: true,
        }],
    }).open();
});

$(document).on("click", ".tmk_timesheet_table #save_timesheet", function (event) {
    const $row = $(event.currentTarget).closest("tr");
    const taskId = $row.find(".taskIdInput").val();
    const taskName = $row.find(".edit_task").val();
    const timesheetId = $row.find('input[name="timesheet_id"]').val();
    jsonrpc("/my/edit_timesheet", {
        id: timesheetId,
        date: $row.find("#ts_date").text(),
        duration: $row.find("#ts_duration").text(),
        description: $row.find("#ts_desc").text(),
        project_id: $row.find("#project").val(),
        task_id: taskId,
        task_name: taskName,
        ts_company_id: $row.find(".ts_company_id_cell").text().trim(),
        expenditure_type: $row.find(".expenditure_type_input").val(),
    }).then(function () {
        token = 0;
        window.location.href = "/my/timesheets";
    });
});

$(document).on("change", ".tmk_timesheet_table input[name='task_name']", function (event) {
    const $row = $(event.currentTarget).closest("tr");
    $row.find(".taskIdInput").val($(event.currentTarget).val());
});

$(document).on("change", ".tmk_timesheet_table select[name='project']", function (event) {
    const $row = $(event.currentTarget).closest("tr");
    $row.find(".taskIdInput").val("");
    $row.find(".edit_task").val("");
});

$(document).on("keyup", ".o_portal_my_doc_table .edit_task", function (event) {
    const $taskInput = $(event.currentTarget);
    const $row = $taskInput.closest("tr");
    const projectId = $row.find(".edit_project").val();

    if (!$taskInput.autocomplete) {
        return;
    }

    $taskInput.autocomplete({
        source: function (_request, response) {
            $.ajax({
                url: "/get_task_data",
                type: "post",
                dataType: "json",
                data: { search: `${event.target.value}-${projectId}` },
                success: function (data) {
                    response($.map(data, function (el) {
                        return {
                            value: el.value,
                            id: el.id,
                        };
                    }));
                },
            });
        },
        select: function (_event, ui) {
            $row.find(".taskIdInput").val(ui.item.id);
        },
    }).autocomplete("instance")._renderMenu = function (ul, items) {
        this.widget().menu("option", "items", "> :not(.ui-autocomplete-category)");
        const that = this;
        $.each(items, function (_index, item) {
            that._renderItemData(ul, item);
        });
    };
});
