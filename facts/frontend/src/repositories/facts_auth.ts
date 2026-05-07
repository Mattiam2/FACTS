import type {ArticleInfo} from "@/types";
import factsClient from '@/repositories/facts_base.ts'

export default {

    async authenticate(vpToken: string, scope: string) {
        return await factsClient.post('/auth/token', {
            "vp_token": vpToken,
            scope,
        })
    },

    async create_article_transaction(accessToken: string, ethAddress: string, articleInfo: ArticleInfo) {
        return await factsClient.post('/articles', {
            from_eth_address: ethAddress,
            article_info: articleInfo
        },
        {
            headers: {
                "Content-type": "application/json",
                "Authorization": `Bearer ${accessToken}`,
            }
        }
    )
    }

}