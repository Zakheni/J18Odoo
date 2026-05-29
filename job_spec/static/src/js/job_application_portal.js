/** @odoo-module */

import publicWidget from 'web.public.widget';
import ajax from 'web.ajax';

publicWidget.registry.JobApplicationPortal = publicWidget.Widget.extend({
    selector: '#jobs_section',
    events: {
        'change #criminal_record': '_onChangeCriminalRec',
        'change #citizenship': '_onChangeCitizenship',
        'change #id_number': '_onChangeIdNumber',
        'change #disability': '_onChangeDisability',
        'click .s_website_create_resume': '_onClickCreateResume',
    },

    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
        $('#id_number_field').show();
        $('#passport_field').hide();
        return def;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onChangeCriminalRec: function (ev) {
        ev.preventDefault();
        var criminalRecordValue = $("select[name='criminal_record']").val();
        if (criminalRecordValue === 'Y') {
            $('#crime_info_div').show();
        } else {
            $('#crime_info_div').hide();
        }
    },

    _onChangeCitizenship: function (ev) {
        ev.preventDefault();
        var citizenshipVal = $("select[name='citizenship']").val();
        if (citizenshipVal === 'SA') {
            $('#id_number_field').show();
            $('#passport_field').hide();
        } else {
            $('#id_number_field').hide();
            $('#passport_field').show();
        }
    },

    _onChangeIdNumber: function (ev) {
        ev.preventDefault();
        var id_number = $("input[name='id_no']").val();
        ajax.jsonRpc('/validate/nationalityId', 'call', {'id_number': id_number})
        .then(function (result) {
            if (result == false){
                alert("Invalid Nationality ID");
            }
        })
    },

     _onChangeDisability: function (ev) {
        ev.preventDefault();
        var disabilityVal = $("select[name='disability']").val();
        if (disabilityVal === 'Y') {
            $('#disability_details_field').show();
        } else {
            $('#disability_details_field').hide();
        }
    },

    _onClickCreateResume: function (ev) {
        ev.preventDefault();
        $('#is_create_resume').prop('checked', true);
        $('#hr_recruitment_form').submit();
    },
});

publicWidget.registry.JobCreateResume = publicWidget.Widget.extend({
    selector: '#resume_container',
    events: {
        'click #addLine': '_onClickAddLine',
        'click #deleteLine': '_onClickDeleteLine',
        'click #addCourseLine': '_onClickAddCourseLine',
        'click #deleteCourseLine': '_onClickDeleteCourseLine',
        'click #addSkillLine': '_onClickAddSkillLine',
        'click #deleteSkillLine': '_onClickDeleteSkillLine',
        'click #addRefLine': '_onClickAddRefLine',
        'click #deleteRefLine': '_onClickDeleteRefLine',
        'click #addEmpHistoryLine': '_onClickAddEmpLine',
        'click #deleteEmpHistoryLine': '_onClickDeleteEmpLine'
    },

    start: function () {
        var def = this._super.apply(this, arguments);
        this.row = $('#qualTableBody tr').length;
        this.course_row = $('#coursesTableBody tr').length;
        this.skill_row = $('#skillsTableBody tr').length;
        this.ref_row = $('#refTableBody tr').length;
        this.emp_history_row = $('#employmentTableBody').length;
        return def;
    },
    _onClickAddLine: function (ev) {
         var new_row = '<tr id="row' + this.row + '"><td><input name="qualification' + this.row + '" type="text" class="form-control" /></td><td><input name="institute' + this.row + '" type="text" class="form-control" /></td><td><input name="year' + this.row + '" type="text" class="form-control" /></td><td><button type="button" class="btn addBtn" id="addLine"><i class="fa fa-plus-circle" aria-hidden="true"></i></button><button type="button" class="btn deleteBtn" id="deleteLine"><i class="fa fa-trash" aria-hidden="true"></i></button></td></tr>';
         $('#qualTableBody').append(new_row);
         this.row++;
         return false;
    },

    _onClickDeleteLine: function (ev) {
        if(this.row>1) {
            $(ev.target).closest('tr').remove();
            this.row--;
        }
        return false;
    },
    _onClickAddCourseLine: function (ev) {
         var new_row = '<tr id="row' + this.course_row + '"><td><input name="course' + this.course_row + '" type="text" class="form-control" /></td><td><input name="course_institute' + this.course_row + '" type="text" class="form-control" /></td><td><button type="button" class="btn addBtn" id="addCourseLine"><i class="fa fa-plus-circle" aria-hidden="true"></i></button><button type="button" class="btn deleteBtn" id="deleteCourseLine"><i class="fa fa-trash" aria-hidden="true"></i></button></td></tr>';
         $('#coursesTableBody').append(new_row);
         this.course_row++;
         return false;
    },

    _onClickDeleteCourseLine: function (ev) {
        if(this.course_row>1) {
            $(ev.target).closest('tr').remove();
            this.course_row--;
        }
        return false;
    },
    _onClickAddSkillLine: function (ev) {
         var new_row = '<tr id="row' + this.skill_row + '"><td><input name="skill' + this.skill_row + '" type="text" class="form-control" /></td><td><input name="skill_experience' + this.skill_row + '" type="text" class="form-control" /></td><td><select name="skill_level' + this.skill_row + '" class="form-control s_website_form_input" id="skill_level' + this.skill_row + '"><option value="1">1</option><option value="2">2</option><option value="3">3</option></select></td><td><button type="button" class="btn addBtn" id="addSkillLine"><i class="fa fa-plus-circle" aria-hidden="true"></i></button><button type="button" class="btn deleteBtn" id="deleteSkillLine"><i class="fa fa-trash" aria-hidden="true"></i></button></td></tr>';
         $('#skillsTableBody').append(new_row);
         this.skill_row++;
         return false;
    },

    _onClickDeleteSkillLine: function (ev) {
        if(this.skill_row>1) {
            $(ev.target).closest('tr').remove();
            this.skill_row--;
        }
        return false;
    },
    _onClickAddRefLine: function (ev) {
         var new_row = '<tr id="row' + this.ref_row + '"><td><input name="ref_company' + this.ref_row + '" type="text" class="form-control" /></td><td><input name="ref_person' + this.ref_row + '" type="text" class="form-control" /></td><td><input name="ref_person_contact_details' + this.ref_row + '" type="text" class="form-control" /></td><td><button type="button" class="btn addBtn" id="addRefLine"><i class="fa fa-plus-circle" aria-hidden="true"></i></button><button type="button" class="btn addBtn" id="deleteRefLine"><i class="fa fa-trash" aria-hidden="true"></i></button></td></tr>';
         $('#refTableBody').append(new_row);
         this.ref_row++;
         return false;
    },

    _onClickDeleteRefLine: function (ev) {
        if(this.ref_row>1) {
            $(ev.target).closest('tr').remove();
            this.ref_row--;
        }
        return false;
    },

    _onClickAddEmpLine: function (ev) {
        var employmentTableHTML = '<table class="main-table employmentHistoryTable">'
                        + '<tbody id="employmentTableBody">'
                        +   '<tr id="row' + this.emp_history_row + '">'
                        +       '<th scope="col" class="fixed-side">Company Name</th>'
                        +        '<td colspan="8"><input name="emp_company_name' + this.emp_history_row + '" type="text" class="form-control"/></td>'
                        +        '<td rowspan="4">'
                        +            '<button type="button" class="btn addBtn" id="addEmpHistoryLine">'
                        +                '<i class="fa fa-plus-circle" aria-hidden="true"></i>'
                        +            '</button>'
                        +            '<button type="button" class="btn deleteBtn" id="deleteEmpHistoryLine">'
                        +                '<i class="fa fa-trash" aria-hidden="true"></i>'
                        +            '</button>'
                        +        '</td>'
                        +    '</tr>'
                        +    '<tr>'
                        +        '<th class="fixed-side">Dates Employed</th>'
                        +        '<td colspan="8"><input name="emp_date_employed' + this.emp_history_row + '" type="text" class="form-control"/></td>'
                        +    '</tr>'
                        +    '<tr>'
                        +        '<th class="fixed-side">Position</th>'
                        +        '<td colspan="8"><input name="emp_position' + this.emp_history_row + '" type="text" class="form-control"/></td>'
                        +    '</tr>'
                        +    '<tr>'
                        +        '<td colspan="8">'
                        +            '<textarea style="width:100%;" placeholder="Duties:" rows="2" name="emp_duties' + this.emp_history_row + '"></textarea>'
                        +        '</td>'
                        +    '</tr>'
                        +'</tbody>'
                    +'</table>';
         $('.employment_div').append(employmentTableHTML);
         this.emp_history_row++;
         return false;
    },

    _onClickDeleteEmpLine: function (ev) {
        if(this.emp_history_row>1) {
            $(ev.target).closest('tbody').remove();
            this.emp_history_row--;
        }
        return false;
    },
});
