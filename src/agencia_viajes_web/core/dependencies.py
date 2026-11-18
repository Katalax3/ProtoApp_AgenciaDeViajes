from fastapi import Request

class NoAutenticadoVista(Exception):
  pass

def require_role(rol_permitido: str):
  def verificador(request: Request):
    usuario = request.session.get("usuario")

    if not usuario or usuario.get("tipo_usuario", "") != rol_permitido:
      raise NoAutenticadoVista()
    return usuario

  return verificador
