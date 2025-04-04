import tkinter as tk
from tkinter import ttk, messagebox
from database import obtener_conexion

class StockFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.ventanas_abiertas = {}

    def create_widgets(self):
        self.form_frame = ttk.LabelFrame(self, text="Nuevo Producto")
        self.form_frame.pack(fill='x', padx=10, pady=10)

        self.nombre_var = self.create_entry("Nombre del Producto:", self.form_frame, tk.StringVar())
        self.cantidad_var = self.create_entry("Cantidad:", self.form_frame, tk.IntVar())
        self.precio_var = self.create_entry("Precio:", self.form_frame, tk.DoubleVar())
        self.minimo_var = self.create_entry("Mínimo:", self.form_frame, tk.IntVar())

        self.agregar_btn = ttk.Button(self.form_frame, text="Agregar Producto", command=self.agregar_producto)
        self.agregar_btn.grid(row=4, column=1, padx=5, pady=10, sticky='e')

        self.refrescar_btn = ttk.Button(self.form_frame, text="Refrescar", command=self.actualizar_lista)
        self.refrescar_btn.grid(row=4, column=0, padx=5, pady=10, sticky='w')

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.actualizar_lista())
        self.search_entry = ttk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack(fill='x', padx=10, pady=5)

        list_frame = ttk.LabelFrame(self, text="Inventario")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ID', 'Nombre Producto', 'Cantidad', 'Precio', 'Mínimo')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center')
        self.tree.pack(fill='both', expand=True)

        self.tree.bind('<Double-1>', self.on_item_double_click)

        movimientos_frame = ttk.LabelFrame(self, text="Movimientos")
        movimientos_frame.pack(fill='both', expand=True, padx=10, pady=10, side='right')
        
        limpiar_btn = ttk.Button(movimientos_frame, text="Limpiar Historial", command=self.limpiar_historial)
        limpiar_btn.pack(padx=10, pady=5)

        self.movimientos_tree = ttk.Treeview(movimientos_frame, columns=('Fecha', 'Movimiento'), show='headings')
        self.movimientos_tree.heading('Fecha', text='Fecha y Hora')
        self.movimientos_tree.heading('Movimiento', text='Movimiento')
        self.movimientos_tree.column('Fecha', width=150, anchor='center')
        self.movimientos_tree.column('Movimiento', width=300, anchor='w')

        scrollbar = ttk.Scrollbar(movimientos_frame, orient='vertical', command=self.movimientos_tree.yview)
        self.movimientos_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self.movimientos_tree.pack(fill='both', expand=True)


        self.actualizar_lista()
        self.cargar_movimientos()


    def create_entry(self, label_text, parent, var):
        ttk.Label(parent, text=label_text).grid(row=parent.grid_size()[1], column=0, padx=5, pady=5, sticky='e')
        entry = ttk.Entry(parent, textvariable=var)
        entry.grid(row=parent.grid_size()[1]-1, column=1, padx=5, pady=5, sticky='w')
        return var

    def agregar_producto(self):
        nombre = self.nombre_var.get().strip()
        cantidad = self.cantidad_var.get()
        precio = self.precio_var.get()
        minimo = self.minimo_var.get()

        if not nombre:
            messagebox.showerror("Error", "El nombre del producto es obligatorio.")
            return
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO stock (nombre_producto, cantidad, precio, minimo) VALUES (?, ?, ?, ?)''', 
                        (nombre, cantidad, precio, minimo))
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Producto añadido al inventario.")
            self.limpiar_formulario()
            self.actualizar_lista()
        except Exception as e:
            messagebox.showerror("Error", "Ocurrió un error al agregar el producto")

    def limpiar_formulario(self):
        self.nombre_var.set('')
        self.cantidad_var.set(0)
        self.precio_var.set(0.0)
        self.minimo_var.set(0)

    def actualizar_lista(self):
        search_term = self.search_var.get().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stock ORDER BY nombre_producto ASC")

            for row in cursor.fetchall():
                producto_id, nombre, cantidad, precio, minimo = row
                if search_term in nombre.lower() or search_term in str(cantidad) or search_term in str(precio) or search_term in str(minimo):
                    item = self.tree.insert('', tk.END, values=row)
                    if cantidad < minimo:
                        self.tree.item(item, tags=('rojo',))
                    else:
                        self.tree.item(item, tags=('blanco',))
            
            conn.close()
            
            self.tree.tag_configure('rojo', background='red', foreground='white')
            self.tree.tag_configure('blanco', background='white', foreground='black')
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al obtener los productos: {e}")

    def on_item_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = selected_item[0]
        producto_id, nombre, cantidad, precio, minimo = self.tree.item(item, "values")

        if producto_id in self.ventanas_abiertas:
            try:
                self.ventanas_abiertas[producto_id].focus() 
                return
            except tk.TclError:
                del self.ventanas_abiertas[producto_id]
        
        top = tk.Toplevel(self)
        top.title(f"Editar Producto ID: {producto_id}")
        self.ventanas_abiertas[producto_id] = top 
    
        def on_close():
            del self.ventanas_abiertas[producto_id]
            top.destroy() 

        nombre_var = tk.StringVar(value=nombre)
        cantidad_var = tk.StringVar(value=str(cantidad))
        precio_var = tk.DoubleVar(value=precio)
        minimo_var = tk.IntVar(value=minimo)

        self.create_entry("Nombre del Producto:", top, nombre_var)
        self.create_entry("Cantidad:", top, cantidad_var)
        self.create_entry("Precio:", top, precio_var)
        self.create_entry("Mínimo:", top, minimo_var)

        guardar_btn = ttk.Button(top, text="Guardar Cambios", command=lambda: self.guardar_cambios(producto_id, nombre_var.get(), cantidad_var.get(), precio_var.get(), minimo_var.get(), top))
        guardar_btn.grid(row=4, column=0, padx=5, pady=10)

        eliminar_btn = ttk.Button(top, text="Eliminar Producto", command=lambda: self.eliminar_producto(producto_id, top))
        eliminar_btn.grid(row=4, column=1, padx=5, pady=10)

    def guardar_cambios(self, producto_id, nuevo_nombre, nueva_cantidad, nuevo_precio, nuevo_minimo, window):
        if not nuevo_nombre:
            messagebox.showerror("Error", "El nombre del producto es obligatorio.")
            return

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT cantidad FROM stock WHERE id = ?", (producto_id,))
            cantidad_actual = cursor.fetchone()[0]

            if nueva_cantidad.startswith('+'):
                cambio = int(nueva_cantidad[1:])
                nueva_cantidad = cantidad_actual + cambio
                movimiento = f"Se agregó {cambio} a '{nuevo_nombre}'"
            elif nueva_cantidad.startswith('-'):
                cambio = int(nueva_cantidad)
                nueva_cantidad = cantidad_actual + cambio
                movimiento = f"Se restó {abs(cambio)} de '{nuevo_nombre}'"
            else:
                nueva_cantidad = int(nueva_cantidad)
                movimiento = f"Cantidad de '{nuevo_nombre}' actualizada a {nueva_cantidad}"

            nuevo_precio = float(nuevo_precio)
            nuevo_minimo = int(nuevo_minimo)
        except ValueError:
            messagebox.showerror("Error", "Cantidad, precio y mínimo deben ser valores numéricos.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al obtener la cantidad actual: {e}")
            return

        if nueva_cantidad < 0:
            messagebox.showerror("Error", "La cantidad no puede ser negativa.")
            return

        try:
            cursor.execute('''UPDATE stock SET nombre_producto = ?, cantidad = ?, precio = ?, minimo = ? WHERE id = ?''',
                        (nuevo_nombre, nueva_cantidad, nuevo_precio, nuevo_minimo, producto_id))
            conn.commit()

            from datetime import datetime
            fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO movimientos_stock (fecha_hora, movimiento) VALUES (?, ?)", (fecha_hora, movimiento))
            conn.commit()
            conn.close()

            self.movimientos_tree.insert('', 'end', values=(fecha_hora, movimiento))

            messagebox.showinfo("Éxito", "Producto actualizado.")
            self.actualizar_lista()
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al actualizar el producto: {e}")

    def cargar_movimientos(self):
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT fecha_hora, movimiento FROM movimientos_stock ORDER BY id ASC")
            for row in cursor.fetchall():
                self.movimientos_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar los movimientos: {e}")

    def eliminar_producto(self, producto_id, window):
        confirm = messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar el producto ID: {producto_id}?")
        if confirm:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM stock WHERE id = ?", (producto_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
                self.actualizar_lista()
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al eliminar el producto: {e}")




    def limpiar_historial(self):
        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de limpiar el historial de movimientos?")
        if confirm:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM movimientos_stock")
                conn.commit()
                conn.close()

                for row in self.movimientos_tree.get_children():
                    self.movimientos_tree.delete(row)

                messagebox.showinfo("Éxito", "Historial de movimientos limpiado.")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al limpiar el historial: {e}")