import tkinter as tk
from tkinter import ttk
from database import conectar_db
from pedidos import PedidosFrame
from caja import CajaFrame
from clientes import ClientesFrame
from stock import StockFrame

def main():
    conectar_db()
    root = tk.Tk()
    root.title("SUPHRIS")
    root.geometry("1000x600")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    pedidos_tab = PedidosFrame(notebook)
    caja_tab = CajaFrame(notebook)
    clientes_tab = ClientesFrame(notebook)
    stock_tab = StockFrame(notebook)

    notebook.add(pedidos_tab, text='Pedidos')
    notebook.add(caja_tab, text='Caja')
    notebook.add(clientes_tab, text='Clientes')
    notebook.add(stock_tab, text='Stock')

    root.mainloop()

if __name__ == "__main__":
    main()
