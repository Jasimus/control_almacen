from datetime import datetime


class ProdUbic:
    def __init__(self, id_usuario, id_ubic, id_lote):
        self.id_usuario = id_usuario
        self.id_ubic = id_ubic
        self.id_lote = id_lote
        self.fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    def load(self):
        # Load data from a database or other source
        pass
    def __str__(self):
        return f"USUARIO: {self.id_usuario}\nUBICACION: {self.id_ubic}\nLOTE: {self.id_lote}\nFECHA/HORA: {self.fecha_hora}"