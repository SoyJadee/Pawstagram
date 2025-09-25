from functools import wraps
from django.shortcuts import redirect

def user_not_authenticated(view_func):
	"""
	Decorador para vistas que solo deben ser accesibles por usuarios NO autenticados.
	Si el usuario está autenticado, lo redirige a 'principal'.
	"""
	@wraps(view_func)
	def _wrapped_view(request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('principal')
		return view_func(request, *args, **kwargs)
	return _wrapped_view