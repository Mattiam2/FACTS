async function getCurrentTab() {
    let queryOptions = {active: true, lastFocusedWindow: true};

    let [tab] = await chrome.tabs.query(queryOptions);
    return tab;
}

function extractSubjectCredential(vc) {
    const vcData = JSON.parse(atob(vc.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))).vc

    if (!vcData.type.includes('VerifiableCredential') || !vcData.type.includes('FACTSFactCheckerCredential') && !vcData.type.includes('FACTSPublisherCredential')) {
        //this.addToastMessage('Invalid Verifiable Presentation type', 'error')
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

function getManipulationDescription(average) {
  switch (average) {
    case 1: {
      return 'Totally Manipulated'
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


getCurrentTab().then(async tab => {
    console.log("Current URL:", tab.url);

    try {
        const articleUrl = encodeURI(tab.url)
        console.log(articleUrl)

        const responseArticle = await fetch(`http://localhost:8001/articles/by-url?url=${articleUrl}`);
        const responseAssessments = await fetch(`http://localhost:8001/assessments/?article_url=${articleUrl}`);

        if (responseArticle.ok) {
            const data = await responseArticle.json();

            const publisherVC = data.metadata.publisher_vc
            const publisherCredential = extractSubjectCredential(publisherVC)
            const publisherDID = publisherCredential.id
            const publisherCompanyName = publisherCredential.company_name
            const publisherCompanyWebsite = publisherCredential.company_website

            publisherDidElement.innerHTML = publisherDID
            publisherCompanyElement.innerHTML = publisherCompanyName
            publisherWebsiteElement.innerHTML = publisherCompanyWebsite

            // Renderizziamo i dati (HTML iniettato)
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
            let credibilityScoreCount = 1
            let manipulationScoreAvg = 0
            let manipulationScoreSum = 0
            let manipulationScoreCount = 1
            for (let assessment of assessments) {
                credibilityScoreSum += assessment.credibility_score
                manipulationScoreSum += assessment.manipulation_score
            }

            assessmentsNumberElement.innerHTML = assessments.length

            credibilityScoreAvg = credibilityScoreSum / credibilityScoreCount
            manipulationScoreAvg = manipulationScoreSum / manipulationScoreCount

            credibilityGaugeElement.style.strokeDashoffset = 100 - (credibilityScoreAvg / 5) * 100
            manipulationGaugeElement.style.strokeDashoffset = 100 - (manipulationScoreAvg / 5) * 100

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

        articleTitle.innerHTML = `
      <div class="error">
        <strong>Errore di connessione:</strong><br>
        ${error.message}
      </div>
    `;
    }
});

detailsButton.addEventListener('click', () => {
    if (articleHash) {
        window.open(`http://localhost:3000/articles/${articleHash}`, '_blank');
    }
})

dashboardButton.addEventListener('click', () => {
    window.open('http://localhost:3000/', '_blank');
})