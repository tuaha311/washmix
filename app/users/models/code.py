from django.conf import settings
from django.db import models
import random
from core.common_models import Common

def code_string():
        number_list = [x for x in range(10)] 
        code_items = []
        for i in range(5):
            num = random.choice(number_list) 
            code_items.append(num)
            
        code_string = "".join(str(item) for item in code_items) 
        
        return code_string 
    
class Code(Common):
    number = models.CharField(max_length=5, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="su_auth_code",
    )
    authenticated = models.BooleanField(
        default=False
    )
    
    def __str__(self):
        return str(self.number) 

    def save(self, *args, **kwargs):
        if not self.number:
            code = code_string()
            self.number = code
        super().save(*args, **kwargs)
