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
        {
            content: "Check Etobella",
            trigger: 'a[href*="https://github.com/etobella"]:first',
        },
        {
            content: "Check LuisDixmit",
            trigger: 'a[href*="https://github.com/luisDixmit"]:first',
        },
        {
            content: "Check JordiBForgeFlow",
            trigger: 'a[href*="https://github.com/JordiBForgeFlow"]:first',
        },
        {
            content: "Check Etobella Value",
            trigger:
                'tr:has(a[href*="https://github.com/etobella"]) td:nth-child(2):contains("4.00"):first',
        },
        {
            content: "Check LuisDixmit Value",
            trigger:
                'tr:has(a[href*="https://github.com/luisDixmit"]) td:nth-child(2):contains("1.00"):first',
        },
        {
            content: "Check JordiBForgeFlow Value",
            trigger:
                'tr:has(a[href*="https://github.com/JordiBForgeFlow"]) td:nth-child(2):contains("1.00"):first',
        },
        {
            content: "Change to Repositories",
            trigger: ".o_contributors_repositories button",
            run: "click",
        },
        {
            content: "Check Repository",
            trigger: 'a[href*="https://github.com/oca/contributors-module"]:first',
        },
        {
            content: "Check Created Pull Requests Value",
            trigger:
                'tr:has(a[href*="https://github.com/oca/contributors-module"]) td:nth-child(3):contains("3"):first',
        },
        {
            content: "Check Merged Pull Requests Value",
            trigger:
                'tr:has(a[href*="https://github.com/oca/contributors-module"]) td:nth-child(4):contains("1"):first',
        },
        {
            content: "Change to Organizations",
            trigger: ".o_contributors_organizations button",
            run: "click",
        },
        {
            content: "Check Dixmit",
            trigger: 'tr:has(a[href*="https://github.com/dixmit"]):first',
        },
        {
            content: "Check ForgeFlow",
            trigger: 'tr:has(a[href*="https://github.com/ForgeFlow"]):first',
        },
        {
            content: "Check Dixmit Created Pull Requests Value",
            trigger:
                'tr:has(a[href*="https://github.com/dixmit"]) td:nth-child(2):contains("2"):first',
        },
        {
            content: "Check ForgeFlow Created Pull Requests Value",
            trigger:
                'tr:has(a[href*="https://github.com/ForgeFlow"]) td:nth-child(2):contains("1"):first',
        },
        {
            content: "Check Dixmit Merged Pull Requests Value",
            trigger:
                'tr:has(a[href*="https://github.com/dixmit"]) td:nth-child(3):contains("1"):first',
        },
        {
            content: "Check ForgeFlow Merged Pull Requests Value",
            trigger:
                'tr:has(a[href*="https://github.com/ForgeFlow"]) td:nth-child(3):contains("0"):first',
        },
    ],
});
