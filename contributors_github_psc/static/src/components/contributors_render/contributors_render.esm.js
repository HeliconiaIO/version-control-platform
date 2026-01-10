import {AutoComplete} from "@web/core/autocomplete/autocomplete";
import {ContributorsRender} from "@contributors_github/components/contributors_render/contributors_render.esm";
import {_t} from "@web/core/l10n/translation";
import {onMounted} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(ContributorsRender, {
    components: {
        ...ContributorsRender.components,
        AutoComplete,
    },
});
patch(ContributorsRender.prototype, {
    setup() {
        super.setup();
        this.state.psc = "";
        this.state.pscs = [];
        this.state.pscId = null;
        this.orm = useService("orm");
        this.selectPsc = _t("Select PSC");
        onMounted(this.fetchPscs.bind(this));
    },
    async fetchPscs() {
        const pscs = await this.orm.searchRead(
            "contributors.organization.psc",
            [["organization_id", "=", this.props.organization]],
            ["id", "name", "member_ids"]
        );
        this.state.rawPscs = Object.fromEntries(pscs.map((psc) => [psc.id, psc]));
        this.state.pscs = pscs.map((psc) => {
            return {
                label: psc.name,
                value: psc.id,
            };
        });
    },
    get pscSources() {
        const pscs = this.state.pscs;
        return [
            {
                async options(query) {
                    return pscs.filter((psc) =>
                        psc.label.toLowerCase().includes(query.toLowerCase())
                    );
                },
            },
        ];
    },
    onSelectPsc(option) {
        this.state.pscId = option.value;
        this.state.psc = this.state.rawPscs[option.value].name;
        this.fetchData();
    },
    getParameters() {
        const params = super.getParameters();
        if (this.state.pscId) {
            params.psc_id = this.state.pscId;
        }
        return params;
    },
});
