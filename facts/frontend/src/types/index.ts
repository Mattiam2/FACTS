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
    "url": string,
    "title": string,
    "author": string,
    "description": string,
    "publication_date": string,
    "language": string,
    "sources": string[]
}
