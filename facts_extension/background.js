const FACTS_API_URL = 'http://localhost:8001'

/**
 * Listens for changes in the active tab and checks if the article is present in FACTS.
 */
chrome.tabs.onActivated.addListener((activeInfo) => {
    console.log("Tab switched! Active Tab ID:", activeInfo.tabId);
    console.log("Window ID:", activeInfo.windowId);
    setNotFoundIcon(activeInfo.tabId)

    chrome.tabs.get(activeInfo.tabId, (tab) => {
        if (chrome.runtime.lastError) {
            console.error(chrome.runtime.lastError.message);
            return;
        }
        console.log("New tab details:", tab);
        if (tab.url && tab.url.startsWith('http')) {
            checkArticlePresence(tab.url, activeInfo.tabId);
        }
    });
});

/**
 * Listens for changes in the URL of the active tab and checks if the article is present in FACTS.
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    setNotFoundIcon(tabId)
    if (tab.url && tab.url.startsWith('http')) {
        checkArticlePresence(tab.url, tabId);
    }
});

/**
 * Checks the presence of an article and its assessments using the provided URL and updates the browser tab icon accordingly.
 *
 * @param {string} url - The URL of the article to be checked.
 * @param {number} tabId - The ID of the browser tab where the icon needs to be updated.
 * @return {Promise<void>} - A promise that resolves when the process of checking the article and setting the icon is complete.
 */
async function checkArticlePresence(url, tabId) {
    try {
        const articleUrl = encodeURIComponent(url)
        const responseArticle = await fetch(`${FACTS_API_URL}/articles/by-url?url=${articleUrl}`, {method: 'HEAD'});
        const responseAssessments = await fetch(`${FACTS_API_URL}/assessments/?article_url=${articleUrl}`, {method: 'HEAD'});

        let assessments = []
        if (responseAssessments.ok) {
            const assessmentsList = await fetch(`${FACTS_API_URL}/assessments/?article_url=${articleUrl}`);
            if(assessmentsList.ok)
                assessments = await assessmentsList.json();
        }

        if (!responseArticle.ok && !responseAssessments.ok) {
            setNotFoundIcon(tabId);
        } else {
            if (assessments.length > 0) {
                let credibilityScoreAvg = 0
                let credibilityScoreSum = 0
                let credibilityScoreCount = undefined
                let manipulationScoreAvg = 0
                let manipulationScoreSum = 0
                let manipulationScoreCount = undefined
                for (let assessment of assessments) {
                    if(assessment.credibility_score > 0) {
                        credibilityScoreCount = (credibilityScoreCount ?? 0) + 1
                        credibilityScoreSum += assessment.credibility_score
                    }
                    if(assessment.manipulation_score > 0) {
                        manipulationScoreCount = (manipulationScoreCount ?? 0) + 1
                        manipulationScoreSum += assessment.manipulation_score
                    }
                }

                credibilityScoreAvg = credibilityScoreSum / (credibilityScoreCount ?? 1)
                manipulationScoreAvg = manipulationScoreSum / (manipulationScoreCount ?? 1)

                if (Math.min(credibilityScoreAvg, manipulationScoreAvg) < 3) {
                    setDangerousIcon(tabId)
                } else if (Math.min(credibilityScoreAvg, manipulationScoreAvg) < 4) {
                    setWarningIcon(tabId)
                } else {
                    setSafeIcon(tabId)
                }
            }else{
                setSafeIcon(tabId)
            }
        }

    } catch (error) {
        console.error("Error checking article in FACTS:", error);
        // In case of error set the icon as not found
        setNotFoundIcon(tabId);
    }
}

/**
 * Sets the icon of the browser tab to indicate that the article is not found.
 * @param tabId - The ID of the browser tab.
 */
function setNotFoundIcon(tabId) {
    chrome.action.setIcon({
        tabId: tabId,
        "path": {
            "16": "icons/favicon-16x16-notfound.png",
            "32": "icons/favicon-32x32-notfound.png",
            "180": "icons/favicon-180x180-notfound.png",
        }
    })
}

/**
 * Sets the icon of the browser tab to indicate that the article has been found and has warning score
 * @param tabId - The ID of the browser tab.
 */
function setWarningIcon(tabId) {
    chrome.action.setIcon({
        tabId: tabId,
        "path": {
            "16": "icons/favicon-16x16-warning.png",
            "32": "icons/favicon-32x32-warning.png",
            "180": "icons/favicon-180x180-warning.png",
        }
    })
}

/**
 * Sets the icon of the browser tab to indicate that the article has been found and has dangerous score
 * @param tabId - The ID of the browser tab.
 */
function setDangerousIcon(tabId) {
    chrome.action.setIcon({
        tabId: tabId,
        "path": {
            "16": "icons/favicon-16x16-dangerous.png",
            "32": "icons/favicon-32x32-dangerous.png",
            "180": "icons/favicon-180x180-dangerous.png",
        }
    })
}

/**
 * Sets the icon of the browser tab to indicate that the article has been found and has safe score
 * @param tabId - The ID of the browser tab.
 */
function setSafeIcon(tabId) {
    chrome.action.setIcon({
        tabId: tabId,
        "path": {
            "16": "icons/favicon-16x16.png",
            "32": "icons/favicon-32x32.png",
            "180": "icons/favicon-180x180.png",
        }
    })
}