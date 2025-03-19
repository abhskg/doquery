from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, status

router = APIRouter()


@router.get("/", response_model=List[object])
async def get_guidelines():
    return [
        {
            "id": 1,
            "title": "Usage Guideline 1",
            "description": "This is a description for usage guideline 1.",
        },
        {
            "id": 2,
            "title": "Usage Guideline 2",
            "description": "This is a description for usage guideline 2.",
        },
        {
            "id": 3,
            "title": "Usage Guideline 3",
            "description": "This is a description for usage guideline 3.",
        },
    ]
