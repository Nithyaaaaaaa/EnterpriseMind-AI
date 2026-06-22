from fastapi import Depends, HTTPException

from dependencies.auth import get_current_user
from models.user import User


def require_role(required_role: str):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):

        if current_user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return current_user

    return role_checker