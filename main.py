import fastapi
import sqlmodel

class Usuario(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    nombre: str

class Libro(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    titulo: str
    usuario_id: int = sqlmodel.Field(foreign_key="usuario.id")

motor_db = sqlmodel.create_engine("sqlite:///database.db")

def obtener_sesion():
    with sqlmodel.Session(motor_db) as sesion:
        yield sesion

app = fastapi.FastAPI()

@app.on_event("startup")
def al_iniciar():
    sqlmodel.SQLModel.metadata.create_all(motor_db)

@app.get("/usuarios/", response_model=list[Usuario])
def listar_usuarios(sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    return sesion.exec(sqlmodel.select(Usuario)).all()

@app.post("/usuarios/", response_model=Usuario)
def crear_usuario(usuario: Usuario, sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    sesion.add(usuario)
    sesion.commit()
    sesion.refresh(usuario)
    return usuario

@app.put("/usuarios/{usuario_id}", response_model=Usuario)
def actualizar_usuario(usuario_id: int, usuario_actualizado: Usuario, sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    usuario_db = sesion.get(Usuario, usuario_id)
    if not usuario_db:
        raise fastapi.HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_db.nombre = usuario_actualizado.nombre
    
    sesion.add(usuario_db)
    sesion.commit()
    sesion.refresh(usuario_db)
    return usuario_db

@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    usuario = sesion.get(Usuario, usuario_id)
    if not usuario:
        raise fastapi.HTTPException(status_code=404, detail="Usuario no encontrado")
    sesion.delete(usuario)
    sesion.commit()
    return {"mensaje": "Usuario eliminado correctamente"}

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

@app.put("/libros/{libro_id}", response_model=Libro)
def actualizar_libro(libro_id: int, libro_actualizado: Libro, sesion: sqlmodel.Session = fastapi.Depends(obtener_sesion)):
    libro_db = sesion.get(Libro, libro_id)
    if not libro_db:
        raise fastapi.HTTPException(status_code=404, detail="Libro no encontrado")

    if not sesion.get(Usuario, libro_actualizado.usuario_id):
        raise fastapi.HTTPException(status_code=400, detail="El nuevo usuario asignado no existe")
        
    libro_db.titulo = libro_actualizado.titulo
    libro_db.usuario_id = libro_actualizado.usuario_id
    
    sesion.add(libro_db)
    sesion.commit()
    sesion.refresh(libro_db)
    return libro_db

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
