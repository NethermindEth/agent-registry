/**
 * Cookie.Fun Agent Scraper
 * Author: Deeptanshu Sankhwar (GitHub: @Deeptanshu-sankhwar)
 * Date: 2025-02-19
 * Description: Scrapes data and meta data around 1400+ AI agents with their twitter impressions/engagements
 */

const axios = require("axios");
const fs = require("fs");

const API_URL =
    "https://www.cookie.fun/api/trpc/agents.getAgentsTableDetails?batch=1&input=";
const PAGE_LIMIT = 15;

async function fetchData(page) {
    const queryParams = {
        0: {
            json: {
                page: page,
                limit: PAGE_LIMIT,
                orderColumn: "TwitterMindshare",
                orderByAscending: false,
                orderDataPoint: "_7DaysAgo",
                tags: [],
                projectsFilter: {
                    blockchainFilter: { chains: [] },
                    categoriesFilter: { values: [] },
                    creationDateFilter: null,
                    frameworkFilter: { values: [] },
                    metricFilters: [],
                    projectTypeFilter: { values: [] },
                    searchFilter: "",
                    tagsFilter: { values: [] },
                },
                isWatchlist: false,
            },
        },
    };

    const encodedParams = encodeURIComponent(JSON.stringify(queryParams));
    console.log(`${API_URL}${encodedParams}`)
    const response = await axios.get(`${API_URL}${encodedParams}`, {
        headers: {
            'User-Agent': 'PostmanRuntime/7.43.0', // Mimic postman
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache'
        }
    });
    return response.data[0].result.data.json;
}

async function scrapeData() {
    let page = 1;
    let allData = [];
    let hasMoreData = true;

    while (hasMoreData) {
        try {
            console.log(`Fetching page ${page}...`);
            const results = await fetchData(page);

            if (results.projects && results.projects.length > 0) {
                allData.push(...results.projects);
                page++;
            } else {
                hasMoreData = false;
            }
        } catch (error) {
            console.error(`Error fetching page ${page}:`, error.message);
            hasMoreData = false;
        }
    }

    // Save data to a JSON file
    fs.writeFileSync("scraped_data.json", JSON.stringify(allData, null, 2));
    console.log("Data scraping complete. Saved to scraped_data.json");
}

scrapeData();
