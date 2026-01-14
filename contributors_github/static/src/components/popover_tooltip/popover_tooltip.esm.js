import {Component} from "@odoo/owl";

export class PopoverTooltip extends Component {
    static template = "contributors_github.PopoverTooltip";
    static props = {
        content: String,
    };
}
