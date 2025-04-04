import tkinter as tk
from tkinter import ttk, messagebox
from database import obtener_conexion
import pywhatkit as kit
import re


class ClientesFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.ventanas_abiertas = {}

    def create_widgets(self):
        form_frame = ttk.LabelFrame(self, text="Nuevo Cliente")
        form_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.nombre_var = tk.StringVar()
        self.nombre_entry = ttk.Entry(form_frame, textvariable=self.nombre_var)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Correo:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.correo_var = tk.StringVar()
        self.correo_entry = ttk.Entry(form_frame, textvariable=self.correo_var)
        self.correo_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Número de Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.telefono_var = tk.StringVar()
        self.telefono_entry = ttk.Entry(form_frame, textvariable=self.telefono_var)
        self.telefono_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        self.agregar_btn = ttk.Button(form_frame, text="Agregar Cliente", command=self.agregar_cliente)
        self.agregar_btn.grid(row=3, column=1, padx=5, pady=10, sticky='e')

        list_frame = ttk.LabelFrame(self, text="Lista de Clientes")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ID', 'Nombre', 'Correo', 'Teléfono')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center')
        self.tree.pack(fill='both', expand=True)

        self.tree.bind('<Double-1>', self.on_item_double_click)

        self.actualizar_lista()

    def agregar_cliente(self):
        nombre = self.nombre_var.get().strip()
        correo = self.correo_var.get().strip()
        telefono = self.telefono_var.get().strip()

        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return
        
        if correo and not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            messagebox.showerror("Error", "El correo no tiene un formato válido.")
            return

        if not telefono.startswith("+") or not telefono[1:].isdigit():
            messagebox.showerror("Error", "El número de teléfono debe incluir el código de país y contener solo dígitos (ejemplo: +543872200997).")
            return
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clientes (nombre, correo, telefono)
                VALUES (?, ?, ?)
            ''', (nombre, correo, telefono))
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Cliente añadido correctamente.")
            self.actualizar_lista()
            self.limpiar_formulario()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al agregar el cliente: {e}")


    def limpiar_formulario(self):
        self.nombre_var.set('')
        self.correo_var.set('')
        self.telefono_var.set('')

    def actualizar_lista(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT clientes.id, clientes.nombre, clientes.correo, clientes.telefono
                FROM clientes
            ''')
            for row in cursor.fetchall():
                self.tree.insert('', tk.END, values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al obtener los clientes: {e}")


    def on_item_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = selected_item[0]
        cliente_id, nombre, correo, telefono = self.tree.item(item, "values")

        if cliente_id in self.ventanas_abiertas:
            try:
                self.ventanas_abiertas[cliente_id].focus()
            except tk.TclError:
                del self.ventanas_abiertas[cliente_id]    


        top = tk.Toplevel(self)
        top.title(f"Cliente ID: {cliente_id}")
        self.ventanas_abiertas[cliente_id] = top 

        def on_close():
            del self.ventanas_abiertas[cliente_id]
            top.destroy()


        ttk.Label(top, text=f"Cliente: {nombre}").pack(padx=10, pady=10)

        enviar_btn = ttk.Button(top, text="Enviar WhatsApp", command=lambda: self.enviar_whatsapp(telefono))
        enviar_btn.pack(padx=10, pady=5)

        ttk.Button(top, text="Eliminar Cliente", command=lambda: self.eliminar_cliente(cliente_id, top)).pack(padx=10, pady=5)
    def enviar_whatsapp(self, telefono):
        telefono = telefono.strip()
        if not telefono:
            messagebox.showerror("Error", "El cliente no tiene número de teléfono registrado.")
            return

        import re
        if not re.match(r"^\+\d+$", telefono):
            messagebox.showerror("Error", "El número de teléfono debe incluir el código de país y contener solo dígitos (ejemplo: +543872200997).")
            return

        try:
            kit.sendwhatmsg_instantly(
                f"{telefono}", 
                "Hola, ¿cómo estás? tu pedido se encuentra listo ! :)",  
                wait_time=10,  
                tab_close=True,  
                close_time=3  
            )
            messagebox.showinfo("Éxito", "Mensaje de WhatsApp enviado.")
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el navegador predeterminado. Asegúrate de tener un navegador instalado.")
        except ConnectionError:
            messagebox.showerror("Error", "No se pudo enviar el mensaje debido a problemas de conexión a Internet.")
        except Exception as e:

            messagebox.showerror("Error", f"No se pudo enviar el mensaje: {e}")


    def eliminar_cliente(self, cliente_id, window):
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            confirm = messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar el cliente ID: {cliente_id}?")
            if confirm:
                cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                self.actualizar_lista()
                window.destroy()
            else:
                conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al eliminar el cliente: {e}")
