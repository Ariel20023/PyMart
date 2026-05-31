from fastapi import APIRouter, HTTPException, Header #קורה מיידע מ heder כמו Authorization
from passlib.context import CryptContext
from uuid import uuid4

from app.database.database import SessionLocal #חיבור ל sqllite 
from app.schemas.schemas import User, UserLogin, UserRegister

TOKENS = {}

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")#מגדיר סוג הצפנה 


@router.post("/register")
def register(user_data: UserRegister):
    db = SessionLocal() #פותח חיבור למסד נתונים

    existing_user = db.query(User).filter(User.email == user_data.email).first() #Checks if a user exists

    if existing_user:
        db.close()
        raise HTTPException(status_code=400, detail="Email already exists")

    password_hash = pwd_context.hash(user_data.password)

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        shipping_address=user_data.shipping_address,
        role="user"
    )

    db.add(user)
    db.commit()
    db.close()

    return {"message": "User created successfully"}


@router.post("/login")
def login(user_data: UserLogin):
    db = SessionLocal()

    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(user_data.password, user.password_hash):#בודק סיסמה מול סיסמה מוצפנת 
        db.close()
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = str(uuid4())

    TOKENS[token] = {
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

    db.close()

    return {
        "message": "Login successful",
        "username": user.username,
        "role": user.role,
        "token": token
    }


def get_user_from_authorization(authorization: str | None): #מקבל משתמש מיתוך token 
    if not authorization:
        raise HTTPException(status_code=401, detail="NO token")

    token = authorization.replace("Bearer ", "")
    user = TOKENS.get(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user #return user 


@router.get("/validate-token") #מאפשר לשרתים אחרים לבדוק אם תוקן תקין
def validate_token(authorization: str = Header(None)):
    user = get_user_from_authorization(authorization)
    return user


@router.get("/validate-admin") #בודק אם משתמש זה admin
def validate_admin(authorization: str = Header(None)):
    user = get_user_from_authorization(authorization)

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="only admin")

    return user
