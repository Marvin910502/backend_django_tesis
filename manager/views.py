from django.shortcuts import render

# Create your views here.


def home(request):

    context = {
        'users_amount': 45,
        'diagnostics_amount': 150,
        'files_amount': 4,
        'storage_space': 500,
        'storage_used': 45,
    }
    return render(request, 'home.html', context)
