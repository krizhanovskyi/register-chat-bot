
from pydantic import BaseModel, EmailStr, constr

class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    tg_user_name: str
    tg_id: int
    tg_first_name: str
    tg_last_name: str
    password: constr(min_length=8, max_length=128)

    def serialize(self):
        return self.json()
