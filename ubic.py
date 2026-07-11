class Ubic:
    def __init__(self,id):
        id_sep = [id[:4],id[4:6],id[6:8],id[8:10]]
        self.id = id
        self.depo = id_sep[0]
        self.pasillo = id_sep[1]
        self.columna = id_sep[2]
        self.nivel = id_sep[3]
        self.ubic = "DPA"