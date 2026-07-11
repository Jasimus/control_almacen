from ast import List
import os
import pandas as pd
import sys
from ubic import Ubic
from rel_ubic import ProdUbic
from openpyxl import load_workbook
import colors

def main():
    file = 'deposito.xlsx'
    user = None

    try:
        user = sys.argv[1]
    except Exception:
        if user is None:
            print("No ingreso un usuario válido.")
            return
    
    os.system("clear")

    try:
        book = load_workbook(file)

    except FileNotFoundError:
        print(f"{colors.YELLOW}El archivo {file} no existe. Se creará uno nuevo.{colors.WHITE}")
        df_ubic = pd.DataFrame(columns=['id', 'depo', 'pasillo', 'columna', 'nivel', 'ubic'])
        df_articulos = pd.DataFrame(columns=['id_usuario', 'id_ubicacion', 'id_lote'])

        with pd.ExcelWriter(file, engine='openpyxl') as writer:
            df_ubic.to_excel(writer, sheet_name='ubicacion', index=False)
            df_articulos.to_excel(writer, sheet_name='articulos', index=False)


    while True:
        ubicacion_input = input("Escanee o ingrese la ubicación.\nSi ya no desea escanear más ubicaciones, ingrese 0.\n(INPUT): ")
        ##ubicacion_input = "DEP1A14702"
        if ubicacion_input == "0":
            print(f"MUCHAS GRACIAS {user}. CHAU.")
            break
        if len(ubicacion_input) != 10:
            print(f"{colors.YELLOW}EL FORMATO NO COINCIDE CON EL DE LA UBICACIÓN. REINTENTE{colors.WHITE}")
            continue
        
        ubicacion = Ubic(ubicacion_input)
        df_ubicacion = pd.DataFrame([ubicacion.__dict__])
        
        with pd.ExcelWriter(file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:

            ubic_sheet = 'ubicacion'

            df_ubicacion.to_excel(
                writer,
                sheet_name=ubic_sheet,
                startrow=writer.sheets[ubic_sheet].max_row,
                index=False,
                header=False
            )

        articulos:List[ProdUbic] = []
        os.system("clear")
        
        while True:
            articulo_input = input(f"Ingrese/Escanee el código del articulo. UBIC: {ubicacion.id}\n0. Ver artículos\n(INPUT): ")
            siguiente = False

            if articulo_input == "0":
                os.system("clear")
                print("ARTICULOS CARGADOS:")
                for a in articulos:
                    print("-------")
                    print(a)
                    print("-------\n")
                print(f"CANTIDAD: {len(articulos)}")
                respuesta = input("0. Confirmar\n1. Agregar más artículos\n> RESPUESTA: ")
                os.system("clear")
                if respuesta == "0":
                    break
                elif respuesta == "1":
                    continue

            elif len(articulo_input) != 7:
                os.system("clear")
                print(f"{colors.YELLOW}EL ARTICULO NO CUMPLE CON EL FORMATO. REINTENTE.{colors.WHITE}")

                siguiente=True
            
            for a in articulos:
                if a.id_lote == articulo_input:
                    os.system("clear")
                    print(f"{colors.RED}NO PUEDE INGRESAR EL MISMO ARTICULO. REINTENTE.{colors.WHITE}")
                    siguiente=True
            
            if siguiente:
                continue
            
            os.system("clear")
            articulo = ProdUbic(user,ubicacion.id,articulo_input)
            
            articulos.append(articulo)
            print(f"{colors.GREEN}ARTICULO INGRESADO EXITOSAMENTE.{colors.WHITE}")
        

        df_articulos = pd.DataFrame([a.__dict__ for a in articulos])

        print(df_articulos)
        print("-" * 35)
        print("\n")

        with pd.ExcelWriter(file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            art_sheet = 'articulos'

            df_articulos.to_excel(
                writer,
                sheet_name=art_sheet,
                startrow=writer.sheets[art_sheet].max_row,
                index=False,
                header=False
            )




main()
