odoo.define('web_timesheet.custom', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    var token = null;


    publicWidget.registry.FavoriteItem = publicWidget.Widget.extend({
        selector: '.new_timesheet',
        start: function () {
            this.$taskInput = this.$('.taskInput');
            this.$taskInput.autocomplete({ source: [] });
            this.$project = ''
            this.$employee = document.getElementById('employee_id');
            this.$currentSelectedIndex = this.$employee.selectedIndex;
            return this._super.apply(this, arguments);
        },
        events: {
            'change select[name="project"]': '_onChangeProject',
//            'change select[name="tasks"]': '_onChangeTask',
            'change select[name="employee_id"]': '_onChangeEmployee',
            'click button[id="savetimesheet"]': '_onClickSavetimesheet',
            'keyup .taskInput': '_onKeyUpTask',

        },


        _onClickSavetimesheet: function(ev) {
            if (parseFloat($('input[name="duration"]').val()) === 0.0){
                alert("Timesheet hours should be greater than 0.0")
                ev.preventDefault();
            }

        },

         _onChangeEmployee: function(ev) {
            ev.preventDefault();
            this.$employee.selectedIndex = this.$currentSelectedIndex;

        },

        _onChangeProject: function(ev) {
            this.$project = $(ev.currentTarget).val();
            this.$taskInput.val('')
            ajax.jsonRpc("/timesheet/form/project", 'call', {
                project_id: this.$project,
            }).then(function(data) {
                if (data) {
                    $('#ts_company_id').val(data.ts_company_id);
                }
            });
        },
        _onChangeTask: function(ev) {
            var task = $(ev.currentTarget).val();
            $('input[name="ts_task_id"]').val(task);

        },

        _onKeyUpTask: async function(evt){
            this.$taskInput.focus();
            var self = this;
                this.$taskInput.autocomplete({
                source: function (request, response) {
                    $.ajax({
                        url: "/get_task_data",
                        type: "post",
                        dataType: "json",
                        async: false,
//                        data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'search': evt.target.value, 'project': this.$project}}),
                        data: { search: evt.target.value + '-' + self.$project},
                        success: function (data) {
                            response($.map(data, function (el) {
                                return {
                                    value: el.value,
                                    id: el.id,
                                }
                            }))
                        }
                    });
                },
              select: function( event, ui ) {
                  var str = ui.item.id;
                  self.$('.taskIdInput').val(str)
              }
          }).autocomplete( "instance" )._renderMenu = function (ul, items) {
                this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
                var that = this;
                $.each(items, function (index, item) {
                    var li = that._renderItemData( ul, item );
                });
            }

          },

    });

    $('.sheet_select').on('click', '#date_id', function(event) {
        $('#contact').click();
    });

    $('.tmk_timesheet_table').on("click", "#delete_timesheet", function(event) {
        var timesheet_id = $(this).parents("tr").find('input[name="timesheet_id"]').val();
        var dialog = new Dialog(this, {
            size: 'medium',
            classes: 'text-center',
            title: _t('Delete Timesheet '),
            $content: _t("<div><p>Do you really want to remove this timesheet?</p></div>"),
            technical: false,
            buttons: [{
                    text: "No",
                    classes: 'btn-danger',
                    click: function() {},
                    close: true
                },
                {
                    text: "Yes",
                    classes: 'btn-primary',
                    click: function() {
                        $(this).parents("tr").remove();
                        ajax.jsonRpc('/my/delete_timesheet', 'call', {
                            'timesheet_id': timesheet_id,
                        }).then(function(data) {
                            window.location.href = "/my/timesheets";
                        });
                    },
                    close: true
                }
            ],
        }).open();
    });


    $('.tmk_timesheet_table').on("click", "#edit_timesheet", function(event) {
        if (token == null || token == 0) {
            token = 1;
            var timesheet = $(this).parents("tr").find('input[name="timesheet_id"]').val();
            $(this).parents("tr").addClass('bg-light');
            $(this).parents("tr").find('#ts_date').attr("contenteditable", "true");
            $(this).parents("tr").find('#ts_desc').attr("contenteditable", "true");
            $(this).parents("tr").find('#ts_desc').focus();
            $(this).parents("tr").find('#ts_duration').attr("contenteditable", "true");
            $(this).parents("tr").find('#edit_timesheet').addClass('d-none');
            $(this).parents("tr").find('#save_timesheet').removeClass('d-none');
            $(this).parents("tr").find('.default_display_project').addClass('d-none');
            $(this).parents("tr").find('.edit_project').removeClass('d-none');
            $(this).parents("tr").find('.default_display_task').addClass('d-none');
            $(this).parents("tr").find('.edit_task').removeClass('d-none');
            $(this).parents("tr").find('.edit-expenditure').removeClass('d-none');
            $(this).parents("tr").find('.saved_exp').addClass('d-none');

//            $(this).parents("tr").find('.default_display_task').addClass('d-none');
             $(this).parents("tr").find('.edit_task').removeClass('d-none');
            var curr_project = $(this).parents("tr").find('.edit_task').removeClass('d-none');
            var project_id = $(this).parents("tr").find('#project').val();
            var task_id = $(this).parents("tr").find('#tasks').val();
//            ajax.jsonRpc('/timesheet/form/project', 'call', {
//                project_id: project_id,
//                task_id: task_id
//            }).then(function(data) {
//                if (data) {
//                    curr_project.replaceWith(data.datas1);
//                }
//            });

            $('.tmk_timesheet_table tr').on('click', '#save_timesheet', function(event) {
                var task_id = $(event.currentTarget).closest("tr").find('.taskIdInput').val();
                var task_name = $(event.currentTarget).closest("tr").find('.edit_task').val();
//                if (!task_id) {
//                    var task_id = task_sec.find('.default_display_task').attr('data-project_task_id');
//
//                }

                ajax.jsonRpc('/my/edit_timesheet', 'call', {
                    'id': timesheet,
                    'date': $(this).parents("tr").find('#ts_date').text(),
                    'duration': $(this).parents("tr").find('#ts_duration').text(),
                    'description': $(this).parents("tr").find('#ts_desc').text(),
                    'project_id': $(this).parents("tr").find('#project').val(),
                    'task_id': task_id,
                    'task_name': task_name,
                    'ts_company_id': $(this).parents("tr").find('#ts_company_id').val(),
                    'expenditure_type': $(this).parents("tr").find('#expenditure_type').val(),
                }).then(function(data) {
                    token = 0;
                    window.location.href = "/my/timesheets";
                });
            });
            $('.tmk_timesheet_table tr').on('change', 'input[name="task_name"]', function(event) {
                var task = $(event.currentTarget).val();
                $(event.currentTarget).closest("tr").find('.taskIdInput').val(task);

            });
            $('.tmk_timesheet_table tr').on('change', 'select[name="project"]', function(event) {
                $(event.currentTarget).closest("tr").find('.taskIdInput').val('');
                $(event.currentTarget).closest("tr").find('.edit_task').val('');

            });

        } else {
            var dialog = new Dialog(this, {
                size: 'medium',
                title: _t('Error'),
                $content: _t("<div><p>You can not edit the multiple timesheet at once.</p></div>"),
                technical: false,
                buttons: [{
                    text: "ok",
                    classes: 'btn-danger',
                    click: function() {},
                    close: true
                }],
            }).open();
        }

    });


    $('.o_portal_my_doc_table').on("keyup", ".edit_task", function(event) {
        var $taskInput = $(this).closest('.tmk_timesheet_table').find('.edit_task');
        var $projectId = $(this).parents("tr").find('.edit_project').val();
//        var $projectId = $(this).parents("tr").find('.projectId').val();
        $taskInput.focus();
        var self = $(this).closest('.tmk_timesheet_table');

        $taskInput.autocomplete({
            source: function(request, response) {
                $.ajax({
                    url: "/get_task_data",
                    type: "post",
                    dataType: "json",
                    data: { search: event.target.value + '-' + $projectId },
                    success: function(data) {
                        response($.map(data, function(el) {
                            return {
                                value: el.value,
                                id: el.id
                            };
                        }));
                    }
                });
            },
            select: function(event, ui) {
                var str = ui.item.id;
                self.find('.taskIdInput').val(str);
            }
        }).autocomplete("instance")._renderMenu = function(ul, items) {
            this.widget().menu("option", "items", "> :not(.ui-autocomplete-category)");
            var that = this;
            $.each(items, function(index, item) {
                var li = that._renderItemData(ul, item);
            });
        };
    });

    });