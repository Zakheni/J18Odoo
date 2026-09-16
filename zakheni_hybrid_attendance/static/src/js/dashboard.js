/** @odoo-module **/

import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";

const TYPE_LABELS = {
    office: "Office",
    home: "Home",
    client: "Client Site",
    other: "Other",
    no_location: "No Location",
};

const TYPE_COLORS = {
    office: "text-success",
    home: "text-info",
    client: "text-warning",
    other: "text-secondary",
    no_location: "text-muted",
};

const DAY_TYPE_LABELS = {
    present: "Present",
    absent: "Absent",
    leave: "On Leave",
    day_off: "Day Off",
    unscheduled: "Unscheduled",
};

export class ZakheniAttendanceDashboard extends Component {
    static template = "zakheni_attendance.Dashboard";
    static props = {
        action: { type: Object, optional: true },
    };

    setup() {
        this.http = useService("http");
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        this.state = useState({
            data: null,
            loading: true,
            refreshing: false,
            locations: [],
            selected_location: 0,
        });

        this._pollInterval = null;

        onWillStart(async () => {
            await this.refresh();
            await this.loadLocations();
        });

        onWillUnmount(() => {
            if (this._pollInterval) {
                browser.clearTimeout(this._pollInterval);
            }
        });
    }

    get typeLabels() {
        return TYPE_LABELS;
    }

    get typeColors() {
        return TYPE_COLORS;
    }

    get dayTypeLabels() {
        return DAY_TYPE_LABELS;
    }

    async refresh() {
        this.state.loading = true;
        try {
            this.state.data = await this.http.post("/zakheni_attendance/live", {});
        } catch (err) {
            this.notification.add(err.message, { type: "danger" });
        } finally {
            this.state.loading = false;
            this.state.refreshing = false;
        }
        this._scheduleRefresh();
    }

    _scheduleRefresh() {
        if (this._pollInterval) {
            browser.clearTimeout(this._pollInterval);
        }
        this._pollInterval = browser.setTimeout(() => {
            this.state.refreshing = true;
            this.refresh();
        }, 30000);
    }

    async loadLocations() {
        const locs = await this.orm.call("zakheni.work.location", "search_read", [[], ["id", "name", "location_type"]], {});
        this.state.locations = locs;
    }

    get locationChoices() {
        return [
            { id: 0, name: "Auto (GPS)" },
            ...this.state.locations.map((l) => ({
                id: l.id,
                name: `${l.name} (${TYPE_LABELS[l.location_type] || l.location_type})`,
            })),
        ];
    }

    async onCheckInOut() {
        const self = this;
        const usePosition = (coords) => {
            self._doCheckInOut(coords);
        };
        const onError = (err) => {
            self._doCheckInOut(null);
        };
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(usePosition, onError, {
                enableHighAccuracy: true,
                timeout: 8000,
                maximumAge: 0,
            });
        } else {
            this._doCheckInOut(null);
        }
    }

    async _doCheckInOut(coords) {
        const params = { capture_method: coords ? "gps" : "ip" };
        if (coords) {
            params.latitude = coords.latitude;
            params.longitude = coords.longitude;
            params.accuracy = coords.accuracy;
        }
        if (this.state.selected_location) {
            params.work_location_id = this.state.selected_location;
        }
        this.state.loading = true;
        try {
            const result = await this.http.post("/zakheni_attendance/check", params);
            if (result) {
                this.notification.add(
                    result.checked_in
                        ? `Checked in${result.work_location_id ? ` at ${result.work_location_type || "location"}` : ""}.`
                        : "Checked out.",
                    { type: "success" }
                );
            }
        } catch (err) {
            this.notification.add(err.message, { type: "danger" });
        } finally {
            this.state.loading = false;
        }
        await this.refresh();
    }

    openDailyRecords() {
        this.action.doAction("zakheni_hybrid_attendance.zakheni_attendance_day_action");
    }

    openOwnAttendance() {
        this.action.doAction("hr_attendance.hr_attendance_action");
    }

    async downloadRegister() {
        const now = new Date();
        const month = now.getMonth() + 1;
        const year = now.getFullYear();
        const url = `/zakheni_attendance/register_export?month=${month}&year=${year}`;
        window.location.href = url;
    }
}

registry.category("actions").add("zakheni_attendance_dashboard", ZakheniAttendanceDashboard);