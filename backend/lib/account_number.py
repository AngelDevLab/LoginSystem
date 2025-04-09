from pydantic import BaseModel, EmailStr
import bcrypt
import random

class UserBasicInfo:
    def __init__(self, data):
        if isinstance(data, dict):
            self.id = data.get('id')
            self.email = data.get('email')
            self.level = data.get('level')
            self.authenticate_status = data.get('authenticate_status')
            self.today_api_use = data.get('today_api_use')
            self.created_at = data.get('created_at')
            self.updated_at = data.get('updated_at')
        elif isinstance(data, tuple):
            self.id = data[0]
            self.email = data[1]
            self.level = data[3]
            self.authenticate_status = data[5]
            self.today_api_use = data[6]
            self.created_at = data[7]
            self.updated_at = data[8]
        else:
            raise TypeError("Expected data to be a dictionary or tuple")

class UserInfo(UserBasicInfo):
    def __init__(self, data):
        super().__init__(data)

        if isinstance(data, dict):
            self.hashed_password = data.get('hashed_password')
            self.hashed_authenticate_code = data.get('hashed_authenticate_code')
        elif isinstance(data, tuple):
            self.hashed_password = data[2]
            self.hashed_authenticate_code = data[4]
        else:
            raise TypeError("Expected data to be a dictionary or tuple")
        
    def to_basic_info(self):
        basic_info_data = {
            'id': self.id,
            'email': self.email,
            'level': self.level,
            'authenticate_status': self.authenticate_status,
            'today_api_use': self.today_api_use,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        return UserBasicInfo(basic_info_data)

class AccountNumberCreate(BaseModel):
    email: EmailStr
    password: str

class AccountNumberAuthenticate(BaseModel):
    email: EmailStr
    authenticate_code: str

class Password:
    @staticmethod
    def hash(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
class AccountNumber(Password):
    @staticmethod
    def authenticate(db, email: str, password: str):

        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM user_info WHERE email = %s", (email,))
        result = cursor.fetchone()

        if not result:
            return False
        
        user = UserInfo(result)

        if not AccountNumber.verify(password, user.hashed_password):
            return False
        
        if not user.authenticate_status:
            return False

        return user
    
class AuthenticateCode(Password):
    @staticmethod
    def generate_digit_code(size: int) -> str:
        return ''.join([str(random.randint(0, 9)) for _ in range(size)])
    