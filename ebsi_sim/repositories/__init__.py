from datetime import datetime
from sqlmodel import SQLModel, Session, select
from ebsi_sim.core.db import engine
from ebsi_sim.models.didr import Identifier, VerificationMethod, VerificationRelationship, IdentifierController


def create_db_and_tables():
    """
    Creates the database and all associated tables.

    :return: None
    """
    SQLModel.metadata.create_all(engine)


def create_default_data():
    with Session(engine) as session:
        identifiers = session.exec(select(Identifier)).all()
        if not identifiers:
            did_authority = Identifier(did="did:ebsi:zE971oT9esuKdcHspKdfAXg",
                                       context="{\"@context\": [\"https://www.w3.org/ns/did/v1\", \"https://w3id.org/security/suites/jws-2020/v1\"]}",
                                       tir_authorised=True,
                                       tnt_authorised=True)
            did_authority_controller = IdentifierController(identifier_did="did:ebsi:zE971oT9esuKdcHspKdfAXg", did_controller="did:ebsi:zE971oT9esuKdcHspKdfAXg")
            vmethod1 = VerificationMethod(
                id="did:ebsi:zE971oT9esuKdcHspKdfAXg#NigSloq5YZrtXc2A40SO0VkKsEP3Nlqim2V6w4voNKM",
                type="JsonWebKey2020",
                did_controller="did:ebsi:zE971oT9esuKdcHspKdfAXg",
                public_key="0x04364c7a761f55a0dfb9aaa2ed5154c19731615499a41673d36d48c64a91424cf3c82fcf553b8e958a84a823686ef501c7d54897592485af380aff752ab6b0a976",
                issecp256k1=True,
                notafter=datetime.fromtimestamp(2090330373))
            vmethod2 = VerificationMethod(
                id="did:ebsi:zE971oT9esuKdcHspKdfAXg#pjyiTxPXALmmH4/ZBxgoUSibpzzKCntMXlzyPGYzupI",
                type="JsonWebKey2020",
                did_controller="did:ebsi:zE971oT9esuKdcHspKdfAXg",
                public_key="0x7b0a202022637276223a2022502d323536222c0a202022657874223a20747275652c0a2020226b65795f6f7073223a205b0a2020202022766572696679220a20205d2c0a2020226b7479223a20224543222c0a20202278223a20227267753666564c7a5a386c45786171586349655a2d5943794c3150327046676a56335034744f69374f6555222c0a20202279223a20227a646951634667383336474d765944326b49566e393957636d435330775952566533683169436e334e7a77222c0a2020226b6964223a2022706a796954785058414c6d6d48342f5a4278676f55536962707a7a4b436e744d586c7a795047597a7570493d220a7d",
                issecp256k1=False,
                notafter=datetime.fromtimestamp(2090330373)
            )
            vrelationship1 = VerificationRelationship(
                identifier_did="did:ebsi:zE971oT9esuKdcHspKdfAXg",
                name="authentication",
                vmethodid="did:ebsi:zE971oT9esuKdcHspKdfAXg#NigSloq5YZrtXc2A40SO0VkKsEP3Nlqim2V6w4voNKM",
                notbefore=datetime.now(),
                notafter=datetime.fromtimestamp(2090330373)
            )
            vrelationship2 = VerificationRelationship(
                identifier_did="did:ebsi:zE971oT9esuKdcHspKdfAXg",
                name="assertionMethod",
                vmethodid="did:ebsi:zE971oT9esuKdcHspKdfAXg#pjyiTxPXALmmH4/ZBxgoUSibpzzKCntMXlzyPGYzupI",
                notbefore=datetime.now(),
                notafter=datetime.fromtimestamp(2090330373)
            )
            vrelationship3 = VerificationRelationship(
                identifier_did="did:ebsi:zE971oT9esuKdcHspKdfAXg",
                name="capabilityInvocation",
                vmethodid="did:ebsi:zE971oT9esuKdcHspKdfAXg#NigSloq5YZrtXc2A40SO0VkKsEP3Nlqim2V6w4voNKM",
                notbefore=datetime.now(),
                notafter=datetime.fromtimestamp(2090330373)
            )
            session.add(did_authority)
            session.add(did_authority_controller)
            session.add(vmethod1)
            session.add(vmethod2)
            session.add(vrelationship1)
            session.add(vrelationship2)
            session.add(vrelationship3)
            session.commit()
