from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import ConnexionForm, InscriptionForm, ProfilForm


class ConnexionView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = ConnexionForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.request.GET.get('next', '/dashboard/')


class DeconnexionView(LogoutView):
    next_page = '/'


def inscription(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès !')
            return redirect('accounts:dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    """Tableau de bord principal — redirige selon le rôle."""
    user = request.user
    context = {'user': user}

    if user.is_superuser or user.role == 'admin_univ':
        return render(request, 'accounts/dashboard_admin.html', context)
    elif user.role == 'enseignant':
        return render(request, 'accounts/dashboard_enseignant.html', context)
    elif user.role == 'bde':
        return render(request, 'accounts/dashboard_bde.html', context)
    elif user.role == 'association':
        return render(request, 'accounts/dashboard_association.html', context)
    else:
        return render(request, 'accounts/dashboard_etudiant.html', context)


@login_required
def profil(request):
    if request.method == 'POST':
        form = ProfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour.')
            return redirect('accounts:profil')
    else:
        form = ProfilForm(instance=request.user)
    return render(request, 'accounts/profil.html', {'form': form})
