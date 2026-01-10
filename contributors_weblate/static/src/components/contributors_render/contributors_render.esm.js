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
        this.state.rawLangs = [];
        this.state.lang = "";
        this.state.langs = [];
        this.state.langId = null;
        this.state.translations = [];
        this.state.sort.translations = "translations";
        this.selectLanguage = _t("Select Language");
        this.orm = useService("orm");
        onMounted(this.fetchLangs.bind(this));
    },
    async fetchData() {
        const data = await super.fetchData();
        if (this.state.kind === "translations") {
            this.state.translations = data.data;
        }
        return data;
    },
    async fetchLangs() {
        const langs = await this.orm.searchRead(
            "res.lang",
            [["active", "in", [true, false]]],
            ["id", "name"]
        );
        this.state.rawLangs = Object.fromEntries(langs.map((lang) => [lang.id, lang]));
        this.state.langs = langs.map((lang) => {
            return {
                label: lang.name,
                value: lang.id,
            };
        });
    },
    getRowData(row_id) {
        if (this.state.kind === "translations") {
            return this.state.translations[row_id];
        }
        return super.getRowData(row_id);
    },
    get rowIds() {
        if (this.state.kind === "translations") {
            return Object.keys(this.state.translations).sort(
                (a, b) =>
                    this.state.translations[b][this.state.sort.translations] -
                    this.state.translations[a][this.state.sort.translations]
            );
        }
        return super.rowIds;
    },
    get langSources() {
        const langs = this.state.langs;
        return [
            {
                async options(query) {
                    return langs.filter((lang) =>
                        lang.label.toLowerCase().includes(query.toLowerCase())
                    );
                },
            },
        ];
    },
    onChangeLang(event) {
        if (event.inputValue === "") {
            this.state.langId = null;
            this.state.lang = "";
            this.fetchData();
        }
    },
    onSelectLang(option) {
        this.state.langId = option.value;
        this.state.lang = this.state.rawLangs[option.value].name;
        this.fetchData();
    },
    getParameters() {
        const params = super.getParameters();
        if (this.state.langId) {
            params.lang_id = this.state.langId;
        }
        return params;
    },
});
