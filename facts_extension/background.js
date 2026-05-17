chrome.tabs.onActivated.addListener((activeInfo) => {
    console.log("Tab switched! Active Tab ID:", activeInfo.tabId);
    console.log("Window ID:", activeInfo.windowId);
    setNotFoundIcon(activeInfo.tabId)
    // Esegui il controllo solo quando la pagina ha finito di caricare completamente ed è un URL web
    chrome.tabs.get(activeInfo.tabId, (tab) => {
        if (chrome.runtime.lastError) {
            console.error(chrome.runtime.lastError.message);
            return;
        }
        // Note: tab.url and tab.title will be undefined unless you have the "tabs" permission
        console.log("New tab details:", tab);
        if (tab.url && tab.url.startsWith('http')) {
            //setNotFoundIcon(activeInfo.tabId)
            checkArticlePresence(tab.url, activeInfo.tabId);
        }
    });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Controlliamo 'complete' per assicurarci che la pagina sia pronta,
    // oppure 'loading' se vogliamo che l'icona cambi immediatamente
    setNotFoundIcon(tabId)
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        checkArticlePresence(tab.url, tabId);
    }
});

async function checkArticlePresence(url, tabId) {
    try {
        const articleUrl = encodeURIComponent(url)
        // 1. Invia l'URL grezzo al tuo endpoint di controllo (es. /api/v1/articles/check)
        // Il backend si occuperà di fare la get_canonical_url() prima del check nel DB
        const responseArticle = await fetch(`http://localhost:8001/articles/by-url?url=${articleUrl}`);
        const responseAssessments = await fetch(`http://localhost:8001/assessments/?article_url=${articleUrl}`);

        let assessments = []
        if (responseAssessments.ok) {
            assessments = await responseAssessments.json();
        }

        if (!responseArticle.ok && assessments.length === 0) {
            setNotFoundIcon(tabId);
        } else {
            if (assessments.length > 0) {
                let credibilityScoreAvg = 0
                let credibilityScoreSum = 0
                let credibilityScoreCount = 1
                let manipulationScoreAvg = 0
                let manipulationScoreSum = 0
                let manipulationScoreCount = 1
                for (let assessment of assessments) {
                    credibilityScoreSum += assessment.credibility_score
                    manipulationScoreSum += assessment.manipulation_score
                }

                credibilityScoreAvg = credibilityScoreSum / credibilityScoreCount
                manipulationScoreAvg = manipulationScoreSum / manipulationScoreCount

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
        // In caso di errore del server, mantieni o resetta l'icona di default
        setNotFoundIcon(tabId);
    }
}

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