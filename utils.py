from database import obtener_conexion
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime


def generar_tiket():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM caja")
    registros = cursor.fetchall()

    total = 0
    categorias_totales = {}
    for reg in registros:
        tipo, descripcion, categoria, monto = reg[1], reg[2], reg[3], reg[4]
        total += monto
        if categoria in categorias_totales:
            categorias_totales[categoria] += monto
        else:
            categorias_totales[categoria] = monto


    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Archivos de texto", "*.txt")],
        title="Guardar Ticket"
    )


    if not file_path:
        return

    
    with open(file_path, "w", encoding='utf-8') as f:
        f.write("Tiket de Caja\n")
        f.write(f"Fecha y Hora: {fecha_hora_actual}\n") 
        f.write("====================\n")
        for reg in registros:
            f.write(f"Tipo: {reg[1]}, Descripción: {reg[2]}, Categoría: {reg[3]}, Monto: {reg[4]}\n")
        f.write("====================\n")
        f.write(f"Total General: {total}\n")
        for cat, monto in categorias_totales.items():
            f.write(f"Total {cat}: {monto}\n")

   
    cursor.execute("DELETE FROM caja")
    conn.commit()
    conn.close()
