from django.http import HttpResponse


def http_response(request):
    return HttpResponse('''
    <a href="accounts/login">Login</a>
    <br>
    <a href="accounts/logout">Logout</a>
    <br>
    <a href="admin">Admin</a>
    ''''')
