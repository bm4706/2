import string
import secrets

class SendEmailHelper:
    @staticmethod  # 정적 메서드로 선언 (객체를 만들 필요 없이 직접 호출 가능능)
    
    def make_random_code_for_register():
        digit_and_alpha = string.ascii_letters + string.digits # 영문 대소문자 + 숫자자
        return "".join(secrets.choice(digit_and_alpha) for _ in range(6)) # 6자리 랜덤 코드 발송송
        
sendEmailHelper = SendEmailHelper()