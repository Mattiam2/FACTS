export interface FactsSubjectCredential {
    id: string
    company_name: string
    company_address: string
    company_vat: string
    company_website: string
    company_email: string
    company_country: string
    authorized_hosts: string[]
    role?: string
}

export interface ArticleInfo {
    url?: string,
    title?: string,
    author?: string,
    description?: string,
    publication_date?: string,
    language?: string,
    sources: string[]
}

export enum CredibilityScore {
    FALSE = 1,
    PARTIALLY_FALSE = 2,
    MISSING_CONTEXT = 3,
    SUBJECTIVE = 4,
    TRUE = 5,
}

export interface CredibilityEvaluation {
    note?: string,
    score?: CredibilityScore
}

export enum ManipulationScore {
    TOTALLY_MANIPULATED = 1,  // Exactly 100% of content is artificially produced
    HEAVILY_MANIPULATED = 2,  // More than 75% of content is artificially produced
    PARTIALLY_MANIPULATED = 3,  // 25% to 75% of content is artificially produced
    MINOR_EDITS = 4,  // Less than 25% of content is artificially produced
    AUTHENTIC = 5,  // Exactly 0% of content is artificially produced
}

export interface ManipulationEvaluation {
    note?: string,
    score?: ManipulationScore
}

export interface AssessedArticleInfo {
    title?: string
    author?: string
    description?: string
    publication_date?: string
    language?: string
    sources: string[]
}

export interface AssessmentInfo {
    article_url?: string,
    assessment_date?: string,
    credibility_evaluation: CredibilityEvaluation,
    manipulation_evaluation: ManipulationEvaluation,
    evidences: string[]
}

export interface EbsiArticleDocument {
    hash: string;
    metadata: ArticleMetadata;
    timestamp: Timestamp;
    creator: string;
}

export interface EbsiAssessmentDocument {
    article_hash: string;
    hash: string;
    metadata: AssessmentMetadata;
    timestamp: Timestamp;
    creator: string;
}

export interface ArticleMetadata {
    version: string;
    type: "FACTS_ARTICLE" | string;
    article_info: ArticleInfo;
    eth_address: string;
    publisher_vc: string;
}

export interface AssessmentMetadata {
    version: string;
    type: "FACTS_ASSESSMENT" | string;
    assessed_article: AssessedArticleInfo;
    assessment_info: AssessmentInfo;
    eth_address: string;
    fact_checker_vc: string;
}

export interface Timestamp {
    datetime: string;         // ISO 8601
    source: "block" | "ntp" | "manual" | string;
    proof: string | null;
}

export interface IndexedAssessment {
    article_hash: string;    // keccak256 hex, 0x-prefixed
    creator: string;         // DID
    manipulation_score: number;
    data_hash: string;       // hex, no 0x prefix
    confirmed: boolean;
    hash: string;            // keccak256 hex, 0x-prefixed
    article_url: string;
    credibility_score: number;
    tx_hash: string;         // Ethereum tx hash, 0x-prefixed
    timestamp: string;       // ISO 8601
    subjectCredential?: FactsSubjectCredential;
    assessmentInfo?: AssessmentInfo;
}

export interface IndexedArticle {
    hash: string;
    url: string;
    creator: string;
    tx_hash: string;
    timestamp: string;
    data_hash: string;
    eth_address: string;
}

export interface VerifiablePresentation {
    '@context': string[];
    id: string;
    type: string[];
    holder: string;
    verifiableCredential: string[];
}

export interface VPPayload {
    iss: string;
    aud: string;
    sub: string;
    iat: number;
    nbf: number;
    exp: number;
    nonce: string;
    jti: string;
    vp: VerifiablePresentation;
}

export interface SourceNode {
    article_hash: string;
    source_value: string;
    source_hash: string;
    avg_credibility_score: number | null;
    avg_manipulation_score: number | null;
    depth: number;
}