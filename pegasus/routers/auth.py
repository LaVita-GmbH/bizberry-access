from fastapi import APIRouter

router = APIRouter()

@router.get('/login')
def login():
    raise NotImplementedError
