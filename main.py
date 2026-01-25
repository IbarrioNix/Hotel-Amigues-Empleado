import tkinter as tk
from gui.login_window import LoginWindow

def main():
    try:
        root = tk.Tk()
        app = LoginWindow(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario")
    except Exception as e:
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Asegurar que la ventana se cierre correctamente
        try:
            root.destroy()
        except:
            pass

if __name__ == '__main__':
    main()