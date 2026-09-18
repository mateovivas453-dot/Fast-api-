import fastapi
import sqlmodel

# 1. MODELOS
class Usuario(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    nombre: str

class Libro(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    titulo: str
    usuario_id: int = sqlmodel.Field(foreign_key="usuario.id")

# 2. BASE DE DATOS
motor_db = sqlmodel.create_engine("sqlite:///database.db")

def obtener_sesion():
    with sqlmodel.Session(motor_db) as sesion:
        yield sesion

app = fastapi.FastAPI()

@app.on_event("startup")
def al_iniciar():
    sqlmodel.SQLModel.metadata.create_all(motor_db)

# 3. ENDPOINTS DE USUARIOS
@app.get("/usuarios/", response_model=list[Usuario])
def listar_usuarios(sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    return sesion.exec(sqlmodel.select(Usuario)).all()

@app.post("/usuarios/", response_model=Usuario)
def crear_usuario(usuario: Usuario, sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    sesion.add(usuario)
    sesion.commit()
    sesion.refresh(usuario)
    return usuario

@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    usuario = sesion.get(Usuario, usuario_id)
    if not usuario:
        raise fastapi.HTTPException(status_code=404, detail="Usuario no encontrado")
    sesion.delete(usuario)
    sesion.commit()
    return {"mensaje": "Usuario eliminado correctamente"}

# 4. ENDPOINTS DE LIBROS
@app.get("/libros/", response_model=list[Libro])
def listar_libros(sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    return sesion.exec(sqlmodel.select(Libro)).all()

@app.post("/libros/", response_model=Libro)
def crear_libro(libro: Libro, sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    if not sesion.get(Usuario, libro.usuario_id):
        raise fastapi.HTTPException(status_code=400, detail="Usuario no existe")
    sesion.add(libro)
    sesion.commit()
    sesion.refresh(libro)
    return libro

@app.delete("/libros/{libro_id}")
def eliminar_libro(libro_id: int, sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    libro = sesion.get(Libro, libro_id)
    if not libro:
        raise fastapi.HTTPException(status_code=404, detail="Libro no encontrado")
    sesion.delete(libro)
    sesion.commit()
    return {"mensaje": "Libro eliminado correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
