from fastapi import APIRouter

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/create_vc")
def get_vc(did):
    # TODO: Build a VC, and return it signed by a DID signer trusting the client whatever.
    # This is necessary in order to make the simulator testable
    # Otherwise I would need to build TAO API which is out of the scope
    pass
