const FACTS_API_URL = 'http://localhost:8001'
const FACTS_WEB_URL = 'http://localhost:8080'

/**
 * Retrieves the currently active tab in the last focused browser window.
 *
 * @return A promise that resolves to the active tab object, which contains details about the tab such as its ID, URL, and title.
 */
async function getCurrentTab() {
    let queryOptions = {active: true, lastFocusedWindow: true};

    let [tab] = await chrome.tabs.query(queryOptions);
    return tab;
}

/**
 * Extracts the credential subject from a Verifiable Credential (VC) and determines its role in the context of specific credential types.
 *
 * @param vc - A JWT-encoded Verifiable Credential string.
 * @return The credential subject object with an additional `role` property if the VC is valid and matches the expected types; otherwise, returns `undefined`.
 */
function extractSubjectCredential(vc) {
    const vcData = JSON.parse(atob(vc.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))).vc

    if (!vcData.type.includes('VerifiableCredential') || !vcData.type.includes('FACTSFactCheckerCredential') && !vcData.type.includes('FACTSPublisherCredential')) {
        return undefined
    }
    const credentialSubject = vcData?.credentialSubject
    if (credentialSubject) {
        if (vcData.type.includes('FACTSPublisherCredential')) {
            credentialSubject.role = "PUBLISHER"
        } else if (vcData.type.includes('FACTSFactCheckerCredential')) {
            credentialSubject.role = "FACT CHECKER"
        }
    }
    return credentialSubject
}

/**
 * Returns a descriptive label based on the provided credibility average.
 *
 * @param average - The average credibility score, ranging from 1 to 5.
 * @return A description corresponding to the given credibility average.
 */
function getCredibilityDescription(average) {
    switch (average) {
        case 1: {
            return 'False'
        }
        case 2: {
            return 'Partially False'
        }
        case 3: {
            return 'Missing Context'
        }
        case 4: {
            return 'Subjective'
        }
        case 5: {
            return 'True'
        }
    }
    return ''
}

/**
 * Provides a description of the manipulation level based on the given average value.
 *
 * @param average - The average value representing the level of manipulation.
 *                           Valid values are 1 through 5.
 * @return A string describing the level of manipulation.
 *                  Returns an empty string if the input is not within the valid range.
 */
function getManipulationDescription(average) {
    switch (average) {
        case 1: {
            return 'Completely Manipulated'
        }
        case 2: {
            return 'Heavily Manipulated'
        }
        case 3: {
            return 'Partially Manipulated'
        }
        case 4: {
            return 'Minor Edits'
        }
        case 5: {
            return 'Authentic'
        }
    }
    return ''
}

const detailsButton = document.getElementById('view-details');
const dashboardButton = document.getElementById('view-facts');
const articleTitle = document.getElementById('article-title');
const loadingView = document.getElementById('loading-view');
const articleView = document.getElementById('article-view');
const assessmentsView = document.getElementById('assessments-view');
const assessmentsNumberElement = document.getElementById('assessments-number')
const assessmentsNotFoundView = document.getElementById('assessments-not-found-view');
const credibilityScoreAvgElement = document.getElementById('credibility-avg-score')
const manipulationScoreAvgElement = document.getElementById('manipulation-avg-score')
const credibilityGaugeElement = document.getElementById('credibility-gauge')
const manipulationGaugeElement = document.getElementById('manipulation-gauge')
const publisherView = document.getElementById('publisher-view')
const publisherDidElement = document.getElementById('publisher-did')
const publisherCompanyElement = document.getElementById('publisher-company')
const publisherWebsiteElement = document.getElementById('publisher-website')
const credibilityDescriptionElement = document.getElementById('credibility-description')
const manipulationDescriptionElement = document.getElementById('manipulation-description')


let articleHash = "";

/**
 * Retrieves the current tab's URL and fetches the article data and assessments from the FACTS API.
 */
getCurrentTab().then(async tab => {
    console.log("Current URL:", tab.url);

    try {
        const articleUrl = encodeURIComponent(tab.url)
        console.log(articleUrl)

        const responseArticle = await fetch(`${FACTS_API_URL}/articles/by-url?url=${articleUrl}`);
        const responseAssessments = await fetch(`${FACTS_API_URL}/assessments/?article_url=${articleUrl}`);

        if (responseArticle.ok) {
            const data = await responseArticle.json();

            const publisherVC = data.metadata.publisher_vc
            const publisherCredential = extractSubjectCredential(publisherVC)
            const publisherDID = publisherCredential?.id
            const publisherCompanyName = publisherCredential?.company_name
            const publisherCompanyWebsite = publisherCredential?.company_website

            publisherDidElement.innerHTML = publisherDID
            publisherCompanyElement.innerHTML = publisherCompanyName
            publisherWebsiteElement.innerHTML = publisherCompanyWebsite

            // SHow article data
            articleHash = data.hash
            articleTitle.innerHTML = data.metadata.article_info.title;
            loadingView.style.display = 'none';
            articleView.style.display = 'block';
            publisherView.style.display = 'block';
            detailsButton.style.display = 'block';
        } else {
            loadingView.style.display = 'none';
            articleView.style.display = 'block';
        }

        if (responseAssessments.ok) {
            const assessments = await responseAssessments.json();
            if (assessments.length === 0) {
                assessmentsView.style.display = 'none';
                assessmentsNotFoundView.style.display = 'block';
                return
            }
            if (assessments[0].article_hash) {
                articleHash = assessments[0].article_hash
            }
            assessmentsView.style.display = 'block';

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

            assessmentsNumberElement.innerHTML = assessments.length

            credibilityGaugeElement.style.strokeDasharray = `${(credibilityScoreAvg / 5) * 126} 126`
            credibilityGaugeElement.style.stroke = credibilityScoreAvg > 3 ? 'var(--teal-accent)' : credibilityScoreAvg > 2 ? '#ffb300' : '#ff5252'

            manipulationGaugeElement.style.strokeDasharray = `${(manipulationScoreAvg / 5) * 126} 126`
            manipulationGaugeElement.style.stroke = manipulationScoreAvg > 3 ? 'var(--teal-accent)' : manipulationScoreAvg > 2 ? '#ffb300' : '#ff5252'


            credibilityScoreAvgElement.innerHTML = credibilityScoreAvg.toFixed(1)
            manipulationScoreAvgElement.innerHTML = manipulationScoreAvg.toFixed(1)

            credibilityDescriptionElement.innerHTML = "Probably " + getCredibilityDescription(Math.floor(credibilityScoreAvg))
            manipulationDescriptionElement.innerHTML = "Probably " + getManipulationDescription(Math.floor(manipulationScoreAvg))

            detailsButton.style.display = 'block';
        } else {
            assessmentsView.style.display = 'none';
            assessmentsNotFoundView.style.display = 'block';
        }

    } catch (error) {

        loadingView.innerHTML = `
      <div class="error">
        <strong>Connection error:</strong><br>
        ${error.message}
      </div>
    `;
    }
});

/**
 * Opens the article details page in a new tab.
 */
detailsButton.addEventListener('click', () => {
    if (articleHash) {
        window.open(`${FACTS_WEB_URL}/articles/${articleHash}`, '_blank');
    }
})

/**
 * Opens the FACTS dashboard in a new tab.
 */
dashboardButton.addEventListener('click', () => {
    window.open(`${FACTS_WEB_URL}`, '_blank');
})