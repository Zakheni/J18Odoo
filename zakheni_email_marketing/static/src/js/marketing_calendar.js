odoo.define('zakheni_email_marketing.marketing_calendar', function (require) {
    'use strict';

    var CalendarView = require('web.CalendarView');
    var CalendarRenderer = require('web.CalendarRenderer');

    CalendarRenderer.include({
        _getColorForRecord: function (record) {
            var color = record.data.color || 0;
            var colors = ['#875A7B', '#E67E22', '#2ECC71', '#3498DB', '#E74C3C',
                         '#9B59B6', '#1ABC9C', '#F39C12', '#34495E', '#7F8C8D'];
            return colors[color % colors.length];
        },
    });
});
