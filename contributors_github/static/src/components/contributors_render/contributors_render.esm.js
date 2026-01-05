import {Component, onMounted, useState} from "@odoo/owl";

import {Dropdown} from "@web/core/dropdown/dropdown";
import {DropdownItem} from "@web/core/dropdown/dropdown_item";
import {formatFloat} from "@web/core/utils/numbers";
import {registry} from "@web/core/registry";
import {rpc} from "@web/core/network/rpc";

/**
 * This Component is a signature request form. It uses
 * @see NameAndSignature for the input fields, adds a submit
 * button, and handles the RPC to save the result.
 */
export class ContributorsRender extends Component {
    static template = "cotributors_github.ContributorsRender";
    setup() {
        const year = new Date().getFullYear();
        const month = new Date().getMonth() + 1;
        this.state = useState({
            sort: {
                contributors: "index",
                organizations: "merged_pull_requests",
                repositories: "merged_pull_requests",
            },
            period: "YTD",
            contributors: [],
            organizations: [],
            repositories: [],
            year: month === 1 ? year - 1 : year,
            month: (month === 1 ? 12 : month - 1).toString(),
            kind: "contributors",
        });
        onMounted(this.fetchData.bind(this));
    }
    selectPeriod(period) {
        this.state.period = period;
        this.fetchData();
    }
    async fetchData() {
        if (this.state.kind === "contributors") {
            this.state.contributors = await rpc(
                "/contributors/fetch",
                this.getParameters()
            );
        } else if (this.state.kind === "organizations") {
            this.state.organizations = await rpc(
                "/contributors/fetch",
                this.getParameters()
            );
        } else if (this.state.kind === "repositories") {
            this.state.repositories = await rpc(
                "/contributors/fetch",
                this.getParameters()
            );
        }
    }
    getParameters() {
        return {
            year: parseInt(this.state.year, 10),
            month: parseInt(this.state.month, 10),
            organization_id: this.props.organization,
            kind: this.state.kind,
            period: this.state.period,
        };
    }
    get rowIds() {
        if (this.state.kind === "contributors") {
            return Object.keys(this.state.contributors).sort(
                (a, b) =>
                    this.state.contributors[b][this.state.sort.contributors] -
                    this.state.contributors[a][this.state.sort.contributors]
            );
        } else if (this.state.kind === "organizations") {
            return Object.keys(this.state.organizations).sort(
                (a, b) =>
                    this.state.organizations[b][this.state.sort.organizations] -
                    this.state.organizations[a][this.state.sort.organizations]
            );
        } else if (this.state.kind === "repositories") {
            return Object.keys(this.state.repositories).sort(
                (a, b) =>
                    this.state.repositories[b][this.state.sort.repositories] -
                    this.state.repositories[a][this.state.sort.repositories]
            );
        }
        return [];
    }
    getRowData(row_id) {
        if (this.state.kind === "organizations") {
            return this.state.organizations[row_id];
        }
        if (this.state.kind === "repositories") {
            return this.state.repositories[row_id];
        }
        if (this.state.kind === "contributors") {
            return this.state.contributors[row_id];
        }
        return {};
    }
    formatFloat(value, digits) {
        return formatFloat(value, {digits: [digits, digits]});
    }
    setKind(kind) {
        this.state.kind = kind;
        this.fetchData();
    }
    sortBy(field) {
        this.state.sort[this.state.kind] = field;
    }
}

ContributorsRender.props = {
    organization: Number,
};
ContributorsRender.components = {
    Dropdown,
    DropdownItem,
};
registry
    .category("public_components")
    .add("contributors_github.ContributorsRender", ContributorsRender);
