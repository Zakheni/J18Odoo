/** @odoo-module **/
import { Component, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class CvDropzone extends Component {
    static template = "cv_studio.CvDropzone";
    static props = { ...standardFieldProps };

    setup() {
        this.state = useState({ dragging: false, uploading: false });
        this.fileInput = useRef("fileInput");
        this.notification = useService("notification");
    }

    get filenameField() {
        return (this.props.options && this.props.options.filename_field) || false;
    }

    get tokenField() {
        return (this.props.options && this.props.options.token_field) || false;
    }

    get currentName() {
        if (this.filenameField) {
            return this.props.record.data[this.filenameField] || "";
        }
        return this.props.value ? "pack uploaded" : "";
    }

    get disabled() {
        return !!this.props.readonly || this.state.uploading;
    }

    onDragOver(ev) {
        if (this.disabled) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        this.state.dragging = true;
    }

    onDragLeave(ev) {
        ev.preventDefault();
        this.state.dragging = false;
    }

    async onDrop(ev) {
        if (this.disabled) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        this.state.dragging = false;
        const file = ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files[0];
        if (file) {
            await this._store(file);
        }
    }

    onClick() {
        if (!this.disabled && this.fileInput.el) {
            this.fileInput.el.click();
        }
    }

    async onChange(ev) {
        const file = ev.target.files && ev.target.files[0];
        if (file) {
            await this._store(file);
        }
        ev.target.value = "";
    }

    async _store(file) {
        this.state.uploading = true;
        try {
            const form = new FormData();
            form.append("ufile", file, file.name);
            let resp;
            try {
                resp = await fetch("/cv_studio/upload_pack", {
                    method: "POST",
                    body: form,
                });
            } catch (err) {
                this.notification.add(
                    "Could not reach the server while uploading the pack.",
                    { type: "danger" });
                return;
            }
            if (!resp.ok) {
                let msg = "Upload failed (HTTP " + resp.status + ").";
                try {
                    const j = await resp.json();
                    if (j && j.error) {
                        msg = j.error;
                    }
                } catch (err) {
                    // non-JSON error body; keep the generic message
                }
                if (resp.status === 413) {
                    msg = "The pack is too large for this server. "
                        + "Raise the server upload limit, or use a Server Folder.";
                }
                this.notification.add(msg, { type: "danger" });
                return;
            }
            const data = await resp.json();
            const changes = {};
            if (this.tokenField) {
                changes[this.tokenField] = data.token;
            }
            if (this.filenameField) {
                changes[this.filenameField] = data.name;
            }
            await this.props.record.update(changes);
        } finally {
            this.state.uploading = false;
        }
    }
}

registry.category("fields").add("cv_dropzone", {
    component: CvDropzone,
    supportedTypes: ["binary"],
    extractProps: ({ options }) => ({ options }),
});
