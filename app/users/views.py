from django.shortcuts import render, redirect
from .models import Code
from .forms import CodeForm
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib import admin, messages

User = get_user_model()

def verify_view(request):
    form = CodeForm(request.POST or None)
    
    if request.method == 'POST':
        user_id = request.session.get('_auth_user_id')
        
        if user_id:
            user = User.objects.get(pk=user_id)
            code = user.su_auth_code
            code_user = f"{user.email}: {user.su_auth_code}"
            
            if form.is_valid():
                num = form.cleaned_data.get('number')
                if str(code) == num:
                    # Set authenticated to True
                    code.authenticated = True
                    code.save()
                    
                    messages.success(request, "You have been successfully logged in.")
                    return redirect("/admin")
                else:
                    messages.error(request, "Sorry! verification cade did not match please try again.")
                    return redirect("/verification")
    
    return render(request, 'verify.html', {'form': form})
