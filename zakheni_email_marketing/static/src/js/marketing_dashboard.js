odoo.define('zakheni_email_marketing.marketing_dashboard', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var qweb = core.qweb;

    var MarketingDashboard = AbstractAction.extend({
        template: 'zakheni_email_marketing.Dashboard',
        events: {},

        init: function (parent, context) {
            this._super.apply(this, arguments);
        },

        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self._loadData();
            });
        },

        _loadData: function () {
            var self = this;
            return this._rpc({
                model: 'marketing.campaign',
                method: 'search_read',
                fields: ['name', 'state', 'sent_count', 'open_rate', 'click_rate', 'mailing_count'],
                domain: [],
            }).then(function (campaigns) {
                self.campaigns = campaigns;
            });
        },
    });

    core.action_registry.add('marketing_dashboard', MarketingDashboard);
    return MarketingDashboard;
});
