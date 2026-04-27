from facts_publish.src.repositories.ebsi_base import EBSIClient


class IssuerRepository(EBSIClient):

    def __init__(self):
        super().__init__(root_path="issuer-mock")

    def request_vc(self, data: dict):
        response = self.post("request_vc",
                             data={
                                 "subject_did": data["subject_did"],
                                 "credential_type": data["credential_type"],
                                 "credential_subject": data["credential_subject"]
                             })
        return response
