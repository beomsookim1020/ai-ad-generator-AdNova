from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud.history import delete_history, get_history_by_id, list_histories_by_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.history import HistoryResponse


router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[HistoryResponse])
def read_histories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[HistoryResponse]:
    return list_histories_by_user(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
    )


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    history = get_history_by_id(db, history_id)
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="history를 찾을 수 없습니다.",
        )

    if history.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인 history만 삭제할 수 있습니다.",
        )

    delete_history(db, history)
