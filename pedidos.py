import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
from database import obtener_conexion
import io
import datetime

class PedidosFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_stock = []  #Seleccion Stock
        self.pedidos = []  #Pedidos Lissss
        self.total_precio_var = tk.DoubleVar(value=0.0)  #Variable temporal
        self.create_widgets()
        self.ventanas_abiertas = {}

    def create_widgets(self):
        form_frame = ttk.LabelFrame(self, text="Nuevo Pedido")
        form_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(form_frame, text="Nombre del Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.cliente_var = tk.StringVar()
        self.cliente_entry = ttk.Entry(form_frame, textvariable=self.cliente_var, width=30)
        self.cliente_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.buscar_cliente_btn = ttk.Button(form_frame, text="Buscar", command=self.buscar_cliente)
        self.buscar_cliente_btn.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(form_frame, text="Fecha de Emisión:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.fecha_emision = DateEntry(form_frame, width=12, background='darkblue',
                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_emision.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Fecha de Entrega:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.fecha_entrega = DateEntry(form_frame, width=12, background='darkblue',
                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_entrega.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Pagado : ").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.sena_var = tk.DoubleVar()
        self.sena_entry = ttk.Entry(form_frame, textvariable=self.sena_var, width=20)
        self.sena_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Stock a Usar:").grid(row=5, column=0, padx=5, pady=5, sticky='ne')
        self.stock_frame = ttk.Frame(form_frame)
        self.stock_frame.grid(row=5, column=1, padx=5, pady=5, sticky='w')

        self.agregar_stock_btn = ttk.Button(form_frame, text="Agregar Productos", command=self.agregar_productos_stock)
        self.agregar_stock_btn.grid(row=5, column=2, padx=5, pady=5, sticky='nw')

        ttk.Label(form_frame, text="Total Precio:").grid(row=6, column=0, padx=5, pady=5, sticky='e')
        self.total_precio_label = ttk.Label(form_frame, textvariable=self.total_precio_var)
        self.total_precio_label.grid(row=6, column=1, padx=5, pady=5, sticky='w') 

        self.stock_tree = ttk.Treeview(self.stock_frame, columns=('Producto', 'Cantidad', 'Precio', "Minimo"), show='headings', height=5)
        self.stock_tree.heading('Producto', text='Producto')
        self.stock_tree.heading('Cantidad', text='Cantidad')
        self.stock_tree.heading('Precio', text='Precio')
        self.stock_tree.heading('Minimo', text='Mínimo')
        self.stock_tree.column('Producto', width=200, anchor='center')
        self.stock_tree.column('Cantidad', width=100, anchor='center')
        self.stock_tree.column('Precio', width=100, anchor='center')
        self.stock_tree.column('Minimo', width=100, anchor='center')
        self.stock_tree.pack(side='left', fill='x')


        btn_refrescar = ttk.Button(self, text="Refrescar", command=self.actualizar_lista)
        btn_refrescar.pack(padx=10, pady=10, side=tk.TOP)

        scrollbar = ttk.Scrollbar(self.stock_frame, orient="vertical", command=self.stock_tree.yview)
        self.stock_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self.eliminar_stock_btn = ttk.Button(form_frame, text="Eliminar Producto", command=self.eliminar_producto_stock)
        self.eliminar_stock_btn.grid(row=5, column=2, padx=5, pady=35, sticky='nw')

        self.cargar_pedido_btn = ttk.Button(form_frame, text="Cargar Pedido", command=self.cargar_pedido)
        self.cargar_pedido_btn.grid(row=8, column=1, padx=5, pady=10, sticky='e')

        list_frame = ttk.LabelFrame(self, text="Pedidos")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ID', 'Cliente', 'Fecha Emisión', 'Fecha Entrega', 'Monto', 'Seña', 'Estado')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        self.tree.tag_configure('pendiente', background='red')
        self.tree.tag_configure('produccion', background='blue')
        self.tree.tag_configure('terminado', background='green')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center')

        self.tree.pack(fill='both', expand=True)

        self.tree.bind('<Double-1>', self.on_item_double_click)

        self.actualizar_lista()
                                    

    def buscar_cliente(self):

        buscar_win = tk.Toplevel(self)
        buscar_win.title("Buscar Cliente")
        buscar_win.geometry("500x400")

        ttk.Label(buscar_win, text="Buscar Cliente:").pack(padx=10, pady=10)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(buscar_win, textvariable=search_var, width=40)
        search_entry.pack(padx=10, pady=5)

        tree = ttk.Treeview(buscar_win, columns=('ID', 'Nombre', 'Correo', 'Teléfono'), show='headings')
        for col in ('ID', 'Nombre', 'Correo', 'Teléfono'):
            tree.heading(col, text=col)
            tree.column(col, anchor='center')
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(buscar_win, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        def buscar():
            query = search_var.get().strip()
            for row in tree.get_children():
                tree.delete(row)
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre, correo, telefono FROM clientes WHERE nombre LIKE ?", ('%' + query + '%',))
                for row in cursor.fetchall():
                    tree.insert('', tk.END, values=row)
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error al buscar clientes: {e}")

        buscar_btn = ttk.Button(buscar_win, text="Buscar", command=buscar)
        buscar_btn.pack(padx=10, pady=5)

        def seleccionar():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Selecciona un cliente.")
                return
            cliente = tree.item(selected[0], 'values')
            self.cliente_var.set(cliente[1])
            buscar_win.destroy()

        seleccionar_btn = ttk.Button(buscar_win, text="Seleccionar Cliente", command=seleccionar)
        seleccionar_btn.pack(padx=10, pady=5)

    def agregar_productos_stock(self):
        seleccionar_win = tk.Toplevel(self)
        seleccionar_win.title("Seleccionar Productos del Stock")
        seleccionar_win.geometry("700x500")

        ttk.Label(seleccionar_win, text="Buscar Producto:").pack(padx=10, pady=10)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(seleccionar_win, textvariable=search_var, width=50)
        search_entry.pack(padx=10, pady=5)

        tree = ttk.Treeview(seleccionar_win, columns=('ID', 'Nombre Producto', 'Cantidad Disponible', 'precio', "minimo"), show='headings', selectmode='extended')
        for col in ('ID', 'Nombre Producto', 'Cantidad Disponible', 'precio', "minimo"):
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=250)
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(seleccionar_win, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        def buscar():
            query = search_var.get().strip()
            for row in tree.get_children():
                tree.delete(row)
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre_producto, cantidad, precio, minimo FROM stock WHERE nombre_producto LIKE ? ORDER BY nombre_producto ASC", ('%' + query + '%',))

                for row in cursor.fetchall():
                    tree.insert('', tk.END, values=row)
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error al buscar productos: {e}")

        buscar_btn = ttk.Button(seleccionar_win, text="Buscar", command=buscar)
        buscar_btn.pack(padx=10, pady=5)

        def seleccionar_productos():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Selecciona al menos un producto.")
                return

            for item in selected:
                producto = tree.item(item, 'values')
                producto_id, nombre, cantidad_disponible, precio, minimo = producto

                try:
                    cantidad_disponible = float(cantidad_disponible)
                    precio = float(precio)
                    minimo = float(minimo)
                except ValueError:
                    messagebox.showerror("Error", "Valor mínimo inválido.")
                    return

                if any(p['id'] == producto_id for p in self.selected_stock):
                    messagebox.showerror("Error", f"El producto '{nombre}' ya está seleccionado.")
                    continue
             # SACAR VENTANA
                cantidad_win = tk.Toplevel(seleccionar_win)
                cantidad_win.title("Especificar Cantidad/Metros")
                cantidad_win.geometry("300x250")

                ttk.Label(cantidad_win, text=f"Producto: {nombre}").pack(padx=10, pady=10)
                ttk.Label(cantidad_win, text=f"Precio: {precio}").pack(padx=10, pady=5)
                ttk.Label(cantidad_win, text=f"Mínimo: {minimo}").pack(padx=10, pady=5)  

                def validar_entrada(text):
                    if text.isdigit() or text == "":
                        return True
                    try:
                        float(text)
                        return True
                    except ValueError:
                        return False

                valid_command = cantidad_win.register(validar_entrada)

                # Cantidad (unidades)
                cantidad_var = tk.DoubleVar()
                ttk.Label(cantidad_win, text="Cantidad (unidades):").pack(padx=10, pady=5)
                cantidad_entry = ttk.Entry(cantidad_win, textvariable=cantidad_var, validate="key", validatecommand=(valid_command, '%P'))
                cantidad_entry.pack(padx=10, pady=5)

                # Cantidad por Metro SACAR
                metros_var = tk.DoubleVar()
                ttk.Label(cantidad_win, text="Cantidad (metros):").pack(padx=10, pady=5)
                metros_entry = ttk.Entry(cantidad_win, textvariable=metros_var, validate="key", validatecommand=(valid_command, '%P'))
                metros_entry.pack(padx=10, pady=5)

                def confirmar():
                    cantidad = cantidad_var.get()
                    metros = metros_var.get()
                    if cantidad <= 0 and metros <= 0:
                        messagebox.showerror("Error", "Debes ingresar una cantidad o metros válidos.")
                        return

                    try:
                        cantidad_disponible_num = float(cantidad_disponible)
                    except ValueError:
                        messagebox.showerror("Error", "Datos de stock inválidos.")
                        return

                    self.selected_stock.append({
                        'id': producto_id,
                        'nombre': nombre,
                        'cantidad': cantidad,
                        'metros': metros,
                        'precio': precio
                    })
                    self.stock_tree.insert('', tk.END, values=(nombre, cantidad, metros, precio))
                    total_precio = sum(float(p['precio']) * float(p['cantidad']) for p in self.selected_stock)
                    self.total_precio_var.set(total_precio)                   
                    cantidad_win.destroy()
                    seleccionar_win.destroy()

                confirmar_btn = ttk.Button(cantidad_win, text="Confirmar", command=confirmar)
                confirmar_btn.pack(padx=10, pady=10)

        seleccionar_btn = ttk.Button(seleccionar_win, text="Seleccionar Productos", command=seleccionar_productos)
        seleccionar_btn.pack(padx=10, pady=5)


    def eliminar_producto_stock(self):
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Selecciona un producto para eliminar.")
            return

        for item in selected:
            nombre, cantidad, precio, minimo = self.stock_tree.item(item, 'values')
            try:
                cantidad = float(cantidad)
                precio = float(precio)
            except ValueError:
                messagebox.showerror("Error", "Los datos del producto seleccionado no son válidos.")
                return
            for p in self.selected_stock:
                if p['nombre'] == nombre and float(p['cantidad']) == cantidad:
                    self.selected_stock.remove(p)
                    break
            self.stock_tree.delete(item)

        total_precio = sum(float(p['precio']) * float(p['cantidad']) for p in self.selected_stock)
        self.total_precio_var.set(total_precio)  # Actualizar la variable del monto total
    def cargar_pedido(self):
        cliente = self.cliente_var.get().strip()
        fecha_emision = self.fecha_emision.get()
        fecha_entrega = self.fecha_entrega.get()
        sena = self.sena_var.get()
        if not cliente:
            messagebox.showerror("Error", "El nombre del cliente es obligatorio.")
            return
        if not fecha_emision or not fecha_entrega:
            messagebox.showerror("Error", "Las fechas son obligatorias.")
            return
        if not self.selected_stock:
            messagebox.showerror("Error", "Debes seleccionar al menos un producto del stock.")
            return
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            # Obtener ID del cliente
            cursor.execute("SELECT id FROM clientes WHERE nombre = ?", (cliente,))
            cliente_id = cursor.fetchone()
            if not cliente_id:
                messagebox.showerror("Error", "Cliente no encontrado.")
                conn.close()
                return
            cliente_id = cliente_id[0]

            cursor.execute('''
                INSERT INTO pedidos (cliente_id, fecha_emision, fecha_entrega, sena)
                VALUES (?, ?, ?, ?)
            ''', (cliente_id, fecha_emision, fecha_entrega, sena))
            
            pedido_id = cursor.lastrowid

            # MODIFICAR INGRESO SIN CATEGORIA hay que cambiar esto
            cursor.execute('''
                INSERT INTO caja (tipo, descripcion, categoria, monto)
                VALUES (?, ?, ?, ?)
            ''', ("Ingreso", f"Venta con el ID {pedido_id}", None, sena))

            for producto in self.selected_stock:
                producto_id = producto['id']
                cantidad = producto['cantidad']
                precio = producto['precio'] 
                # Actualizar el stock
                cursor.execute('''
                    UPDATE stock
                    SET cantidad = cantidad - ?, precio = ?
                    WHERE id = ?
                ''', (cantidad, precio, producto_id))

                cursor.execute('''
                    INSERT INTO pedidos_stock (pedido_id, stock_id, cantidad, precio)  -- Reemplazamos metros por precio
                    VALUES (?, ?, ?, ?)
                ''', (pedido_id, producto_id, cantidad, precio)) 

            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Pedido cargado correctamente.")
            self.actualizar_lista()
            self.limpiar_formulario()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el pedido: {e}")


    def limpiar_formulario(self):
        self.cliente_var.set('')
        self.fecha_emision.set_date(datetime.date.today())
        self.fecha_entrega.set_date(datetime.date.today())
        self.sena_var.set(0.0)
        self.selected_stock = []
        for row in self.stock_tree.get_children():
         self.stock_tree.delete(row)
        self.total_precio_var.set(0.0)

    def actualizar_estado_pedido(self, pedido_id, nuevo_estado):
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE pedidos
            SET estado = ?
            WHERE id = ?
        ''', (nuevo_estado, pedido_id))

        conn.commit()
        conn.close()
        for pedido in self.pedidos:
            if pedido[0] == pedido_id:
                pedido[-1] = nuevo_estado 
                break

        self.actualizar_lista()

    def actualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT pedidos.id, clientes.nombre, pedidos.fecha_emision, 
                pedidos.fecha_entrega,
                pedidos.sena, pedidos.estado
            FROM pedidos
            JOIN clientes ON pedidos.cliente_id = clientes.id
        ''')

        pedidos = cursor.fetchall()
        conn.close()

        for pedido in pedidos:
            self.tree.insert("", "end", values=pedido)

        messagebox.showinfo("Refrescado", "Lista de pedidos actualizada.")


    def on_item_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = selected_item[0]
        pedido_id = self.tree.item(item, "values")[0]

        if pedido_id in self.ventanas_abiertas:
            try:
                self.ventanas_abiertas[pedido_id].focus() 
                return
            except tk.TclError:
                del self.ventanas_abiertas[pedido_id]

        top = tk.Toplevel(self)
        top.title(f"Pedido ID: {pedido_id}")
        self.ventanas_abiertas[pedido_id] = top 
        
        def on_close():
            del self.ventanas_abiertas[pedido_id]
            top.destroy() 
        ttk.Button(top, text="Editar Pedido", command=lambda: self.editar_pedido(pedido_id, top)).pack(padx=10, pady=5)
        ttk.Button(top, text="Cambiar Estado", command=lambda: self.cambiar_estado(pedido_id, top)).pack(padx=10, pady=5)
        ttk.Button(top, text="Exportar a PDF", command=lambda: self.exportar_pedido_jpeg(pedido_id, top)).pack(padx=10, pady=5)
        ttk.Button(top, text="Eliminar Pedido", command=lambda: self.eliminar_pedido(pedido_id, top)).pack(padx=10, pady=5)

    def editar_pedido(self, pedido_id, window):
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fecha_emision, fecha_entrega, indicaciones, monto_total
                FROM pedidos
                WHERE id = ?
            ''', (pedido_id,))
            datos = cursor.fetchone()
            conn.close()

            if not datos:
                messagebox.showerror("Error", "No se encontró el pedido.")
                window.destroy()
                return
            edit_window = tk.Toplevel(window)
            edit_window.title(f"Editar Pedido ID: {pedido_id}")

            labels = ["Fecha de Emisión", "Fecha de Entrega", "Indicaciones", "Monto Total"]
            entries = []

            for i, label in enumerate(labels):
                ttk.Label(edit_window, text=label).grid(row=i, column=0, padx=10, pady=5)
                entry = ttk.Entry(edit_window)
                entry.grid(row=i, column=1, padx=10, pady=5)
                entry.insert(0, datos[i])
                entries.append(entry)

            def guardar_cambios():
                fecha_emision = entries[0].get()
                fecha_entrega = entries[1].get()
                indicaciones = entries[2].get()
                monto_total = entries[3].get()

                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE pedidos
                        SET fecha_emision = ?, fecha_entrega = ?, indicaciones = ?, monto_total = ?
                        WHERE id = ?
                    ''', (fecha_emision, fecha_entrega, indicaciones, monto_total, pedido_id))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Éxito", "Pedido actualizado correctamente.")
                    edit_window.destroy()
                    window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar el pedido: {e}")

            ttk.Button(edit_window, text="Guardar Cambios", command=guardar_cambios).grid(row=len(labels), columnspan=2, pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al editar el pedido: {e}")

    def cambiar_estado(self, pedido_id, window):
        estados = ["pendiente", "produccion", "terminado"]
        estado_actual = self.obtener_estado(pedido_id)
        nueva_ventana = tk.Toplevel(self)
        nueva_ventana.title("Cambiar Estado")

        ttk.Label(nueva_ventana, text="Selecciona el nuevo estado:").pack(padx=10, pady=10)
        estado_var = tk.StringVar(value=estado_actual)
        estado_combo = ttk.Combobox(nueva_ventana, textvariable=estado_var, values=estados, state='readonly')
        estado_combo.pack(padx=10, pady=5)


        def confirmar_cambio():
            nuevo_estado = estado_var.get()
            self.actualizar_estado_pedido(pedido_id, nuevo_estado)
            for item in self.tree.get_children():
                item_values = self.tree.item(item, "values")
                if item_values[0] == pedido_id:
                    if nuevo_estado == "diseño":
                        tag_estado = 'diseño'
                    elif nuevo_estado == "produccion":
                        tag_estado = 'produccion'
                    elif nuevo_estado == "terminado":
                        tag_estado = 'terminado'
                    else:
                        tag_estado = ''
                    self.tree.item(item, values=(item_values[0], item_values[1], item_values[2], item_values[3], item_values[4], item_values[5], nuevo_estado), tags=(tag_estado,))


            nueva_ventana.destroy()

        ttk.Button(nueva_ventana, text="Confirmar", command=confirmar_cambio).pack(padx=10, pady=10)

    def obtener_estado(self, pedido_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT estado FROM pedidos WHERE id = ?", (pedido_id,))
        estado = cursor.fetchone()
        conn.close()
        return estado[0] if estado else ""


    def eliminar_pedido(self, pedido_id, window):
        confirm = messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar el pedido {pedido_id}?")
        if confirm:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT sena FROM pedidos WHERE id = ?", (pedido_id,))
            sena = cursor.fetchone()
            if sena:
                sena = sena[0]
                cursor.execute("DELETE FROM caja WHERE descripcion = ?", (f"Seña para Pedido ID {pedido_id}",))
                
            cursor.execute("DELETE FROM pedidos_stock WHERE pedido_id = ?", (pedido_id,))
            cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Pedido eliminado correctamente.")
            self.actualizar_lista()
            window.destroy()

    
