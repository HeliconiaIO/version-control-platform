import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("portal_load_contributors_github", {
    url: "/my",
    steps: () => [
        {
            content: "Check portal is loaded and Find Contributors menu",
            trigger: 'a[href*="/contributors"]:contains("Contributors"):first',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Check Contributors Page",
            trigger: 'a[href*="/contributors/oca"]:contains("OCA"):first',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Check Contributors Page",
            trigger: "owl-component",
        },
    ],
});
