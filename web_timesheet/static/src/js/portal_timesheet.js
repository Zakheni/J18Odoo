/** @odoo-module **/

import { PortalHomeCounters } from '@portal/js/portal';

PortalHomeCounters.include({
    /**
     * @override
     * Keep the Timesheets card visible for portal users even when the count is zero
     * (counts load asynchronously; portal domain may include linked-employee lines).
     */
    _getCountersAlwaysDisplayed() {
        return this._super(...arguments).concat(['timesheet_count']);
    },
});
