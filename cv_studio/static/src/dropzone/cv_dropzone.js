/** @odoo-module **/
import { Component, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class CvDropzone extends Component {
    static template = "cv_studio.CvDropzone";
    static props = { ...standardFieldProps };

    setup() {
        this.state = useState({ dragging: false });
        this.fileInput = useRef("fileInput");
    }

    get filenameField() {
        return (this.props.options && this.props.options.filename_field) || false;
    }

    get currentName() {
        if (this.filenameField) {
            return this.props.record.data[this.filenameField] || "";
        }
        return this.props.value ? "pack uploaded" : "";
    }

    get disabled() {
        return !!this.props.readonly;
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
        const b64 = await this._toBase64(file);
        const changes = { [this.props.name]: b64 };
        if (this.filenameField) {
            changes[this.filenameField] = file.name;
        }
        await this.props.record.update(changes);
    }

    _toBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const res = reader.result || "";
                const comma = res.indexOf(",");
                resolve(comma >= 0 ? res.slice(comma + 1) : res);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
}

registry.category("fields").add("cv_dropzone", {
    component: CvDropzone,
    supportedTypes: ["binary"],
    extractProps: ({ options }) => ({ options }),
});
