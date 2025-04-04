import tkinter as tk
from tkinter import ttk, messagebox
from database import obtener_conexion
from utils import generar_tiket

class CajaFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.categorias = ["Producto", "Deuda", "Impuesto", "Servicio", "Varios", "Sueldo", "Descuento"]
        self.create_widgets()
        self.ventanas_abiertas = {}

    def create_widgets(self):

        form_frame = ttk.LabelFrame(self, text="Registro de Caja")
        form_frame.pack(fill='x', padx=10, pady=10)


        ttk.Label(form_frame, text="Tipo:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.tipo_var = tk.StringVar()
        self.tipo_combo = ttk.Combobox(form_frame, textvariable=self.tipo_var, values=["Ingreso", "Egreso"], state='readonly')
        self.tipo_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')


        ttk.Label(form_frame, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.descripcion_var = tk.StringVar()
        self.descripcion_entry = ttk.Entry(form_frame, textvariable=self.descripcion_var)
        self.descripcion_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')


        ttk.Label(form_frame, text="Categoría:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.categoria_var = tk.StringVar()
        self.categoria_combo = ttk.Combobox(form_frame, textvariable=self.categoria_var, values=self.categorias, state='readonly')
        self.categoria_combo.grid(row=2, column=1, padx=5, pady=5, sticky='w')


        ttk.Label(form_frame, text="Monto:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.monto_var = tk.StringVar()  # Cambiado a StringVar para validar manualmente
        self.monto_entry = ttk.Entry(form_frame, textvariable=self.monto_var)
        self.monto_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')


        self.agregar_btn = ttk.Button(form_frame, text="Agregar", command=self.agregar_caja)
        self.agregar_btn.grid(row=4, column=1, padx=5, pady=10, sticky='e')


        self.refrescar_btn = ttk.Button(form_frame, text="Refrescar", command=self.refrescar)
        self.refrescar_btn.grid(row=4, column=0, padx=5, pady=10, sticky='w')


        list_frame = ttk.LabelFrame(self, text="Historial de Caja")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)


        scrolled_frame = ttk.Frame(canvas)


        canvas.create_window((0, 0), window=scrolled_frame, anchor="nw")
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        

        columns = ('ID', 'Tipo', 'Descripción', 'Categoría', 'Monto')
        self.tree = ttk.Treeview(scrolled_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center')
        self.tree.pack(fill='both', expand=True)

        self.tree.bind('<Double-1>', self.on_item_double_click)


        self.generar_tiket_btn = ttk.Button(self, text="Generar Tiket", command=self.generar_tiket)
        self.generar_tiket_btn.pack(pady=5)

        self.actualizar_lista()

    def refrescar(self):
        """Método para refrescar la lista de registros en la interfaz."""
        self.actualizar_lista()
        messagebox.showinfo("Refrescar", "Datos de caja actualizados.")

    def agregar_caja(self):
        tipo = self.tipo_var.get()
        descripcion = self.descripcion_var.get()
        categoria = self.categoria_var.get()
        monto = self.monto_var.get()

        if not all([tipo, descripcion, categoria, monto]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return


        try:
            monto = float(monto) 
            if tipo == "Ingreso" and monto <= 0:
                raise ValueError("El monto para un ingreso debe ser mayor a 0.")
            elif tipo == "Egreso" and monto >= 0:
                raise ValueError("El monto para un egreso debe ser menor a 0.")
        except ValueError:
            messagebox.showerror("Error", "El campo 'Monto' debe contener un valor numérico válido.")
            return
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO caja (tipo, descripcion, categoria, monto) VALUES (?, ?, ?, ?)''',
                    (tipo, descripcion, categoria, monto))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Registro añadido a la caja.")
        self.actualizar_lista()
        self.limpiar_formulario()

    def limpiar_formulario(self):
        self.tipo_var.set('')
        self.descripcion_var.set('')
        self.categoria_var.set('')
        self.monto_var.set(0.0)

    def actualizar_lista(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM caja")
        for row in cursor.fetchall():
            self.tree.insert('', tk.END, values=row)
        conn.close()

    def on_item_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = selected_item[0]
        registro_id = self.tree.item(item, "values")[0]

        if registro_id in self.ventanas_abiertas:
            try:
                self.ventanas_abiertas[registro_id].focus() 
                return
            except tk.TclError:
                del self.ventanas_abiertas[registro_id]

        top = tk.Toplevel(self)
        top.title(f"Eliminar Registro ID: {registro_id}")
        self.ventanas_abiertas[registro_id] = top  
        
        def on_close():
            del self.ventanas_abiertas[registro_id]
            top.destroy()



        ttk.Label(top, text=f"¿Estás seguro de eliminar el registro ID: {registro_id}?").pack(padx=10, pady=10)
        ttk.Button(top, text="Sí, Eliminar", command=lambda: self.eliminar_registro(registro_id, top)).pack(padx=10, pady=5)
        ttk.Button(top, text="Cancelar", command=top.destroy).pack(padx=10, pady=5)

    def eliminar_registro(self, registro_id, window):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM caja WHERE id = ?", (registro_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
        self.actualizar_lista()
        window.destroy()

    def generar_tiket(self):
        try:
            generar_tiket()
            messagebox.showinfo("Éxito", "Tiket generado y historial borrado.")
            self.actualizar_lista()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el tiket: {e}")
