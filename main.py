import os
import random
import customtkinter as ctk
from PIL import Image
from tkinter import filedialog
import core

class AppBiblioteca(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("G-Bible")
        self.geometry("1100x750")
        
        # --- NUEVO: Control de redimensionamiento responsivo ---
        self.ancho_anterior = self.winfo_width()
        self.id_redimension = None
        self.bind("<Configure>", self.al_redimensionar)
        
        self.config_data = core.cargar_config()
        self.todos_los_juegos = []
        self.filtro_busqueda = ""
        self.categoria_actual = "⭐ Favoritos"

        self.paleta_colores = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD", 
                               "#D4A5A5", "#9B59B6", "#3498DB", "#E67E22", "#2ECC71"]
        self.colores_carpetas = {}

        img_vacia = Image.new("RGB", (140, 140), (50, 50, 50))
        self.img_por_defecto = ctk.CTkImage(img_vacia, size=(140, 140))

        # --- LAYOUT PRINCIPAL ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1) 

        # ==========================================
        # SIDEBAR
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(1, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="🎮 Mi Launcher", font=("Arial", 20, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        self.scroll_sidebar = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll_sidebar.grid(row=1, column=0, sticky="nsew", padx=10, pady=0)

        self.btn_add = ctk.CTkButton(self.sidebar, text="+ Vincular Carpeta", command=self.agregar_carpeta)
        self.btn_add.grid(row=2, column=0, padx=20, pady=(10, 5))

        self.btn_recargar = ctk.CTkButton(
            self.sidebar, text="🔄 Recargar Juegos", 
            fg_color="#27AE60", hover_color="#2ECC71",
            command=self.cargar_datos_y_dibujar
        )
        self.btn_recargar.grid(row=3, column=0, padx=20, pady=(5, 20))

        # ==========================================
        # MAIN FRAME
        # ==========================================
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.top_bar = ctk.CTkFrame(self.main_frame, height=60, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))

        self.lbl_titulo_seccion = ctk.CTkLabel(self.top_bar, text=self.categoria_actual, font=("Arial", 28, "bold"))
        self.lbl_titulo_seccion.pack(side="left")

        self.top_right_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.top_right_frame.pack(side="right")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.actualizar_busqueda)
        self.entry_busqueda = ctk.CTkEntry(self.top_right_frame, placeholder_text="Buscar juego...", width=250, textvariable=self.search_var)
        self.entry_busqueda.pack(side="right", padx=(10, 0))

        self.btn_desvincular = ctk.CTkButton(
            self.top_right_frame, text="🗑️ Desvincular", width=100,
            fg_color="#C0392B", hover_color="#E74C3C", font=("Arial", 14, "bold"),
            command=self.desvincular_carpeta
        )

        self.scroll_main = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.scroll_main.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.cargar_datos_y_dibujar()

    # --- NUEVA LÓGICA: EVENTO DE REDIMENSIÓN ---
    def al_redimensionar(self, event):
        # Solo actuamos si el evento viene de la ventana principal
        if event.widget == self:
            nuevo_ancho = self.winfo_width()
            # Si el ancho cambia más de 50 píxeles, redibujamos
            if abs(nuevo_ancho - self.ancho_anterior) > 50:
                self.ancho_anterior = nuevo_ancho
                # Cancelamos el redibujado anterior si el usuario sigue arrastrando la ventana
                if self.id_redimension:
                    self.after_cancel(self.id_redimension)
                # Esperamos 300ms después de que suelte la ventana para calcular y redibujar
                self.id_redimension = self.after(300, self.dibujar_juegos)

    # --- LÓGICA EXISTENTE ---
    def agregar_carpeta(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.config_data["bibliotecas"][os.path.basename(ruta)] = ruta
            core.guardar_config(self.config_data)
            self.cargar_datos_y_dibujar()

    def desvincular_carpeta(self):
        if self.categoria_actual in self.config_data["bibliotecas"]:
            del self.config_data["bibliotecas"][self.categoria_actual]
            core.guardar_config(self.config_data)
            self.categoria_actual = "⭐ Favoritos" 
            self.search_var.set("")
            self.cargar_datos_y_dibujar()

    def seleccionar_categoria(self, nombre_cat):
        self.categoria_actual = nombre_cat
        self.search_var.set("")
        self.dibujar_juegos()

    def actualizar_busqueda(self, *args):
        self.filtro_busqueda = self.search_var.get().lower()
        self.dibujar_juegos()

    def cambiar_portada(self, ruta_carpeta_juego):
        ruta_img = filedialog.askopenfilename(
            title="Selecciona una portada", 
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
        )
        if ruta_img:
            core.asignar_portada_personalizada(ruta_img, ruta_carpeta_juego)
            self.cargar_datos_y_dibujar()

    def toggle_favorito(self, ruta_exe):
        if ruta_exe in self.config_data["favoritos"]:
            self.config_data["favoritos"].remove(ruta_exe)
        else:
            self.config_data["favoritos"].append(ruta_exe)
        core.guardar_config(self.config_data)
        self.dibujar_juegos()

    # --- RENDERIZADO ---
    def cargar_datos_y_dibujar(self):
        self.todos_los_juegos = []
        for nombre_cat, ruta in self.config_data["bibliotecas"].items():
            if nombre_cat not in self.colores_carpetas:
                self.colores_carpetas[nombre_cat] = random.choice(self.paleta_colores)

            juegos = core.buscar_juegos(ruta)
            for j in juegos:
                j["categoria"] = nombre_cat
            self.todos_los_juegos.extend(juegos)
            
        self.dibujar_sidebar()
        self.dibujar_juegos()

    def dibujar_sidebar(self):
        for w in self.scroll_sidebar.winfo_children(): w.destroy()

        btn_fav = ctk.CTkButton(
            self.scroll_sidebar, text="⭐ Favoritos", anchor="w", font=("Arial", 14, "bold"),
            fg_color="#333333" if self.categoria_actual == "⭐ Favoritos" else "transparent", 
            hover_color="#444444", text_color="#FFD700",
            command=lambda: self.seleccionar_categoria("⭐ Favoritos")
        )
        btn_fav.pack(fill="x", pady=(0, 10))

        for cat in sorted(self.config_data["bibliotecas"].keys()):
            color_fondo = "#333333" if self.categoria_actual == cat else "transparent"
            color_texto = self.colores_carpetas.get(cat, "#FFFFFF")
            
            btn_cat = ctk.CTkButton(
                self.scroll_sidebar, text=f"📁 {cat}", anchor="w", font=("Arial", 14, "bold"),
                fg_color=color_fondo, hover_color="#444444", text_color=color_texto,
                command=lambda c=cat: self.seleccionar_categoria(c)
            )
            btn_cat.pack(fill="x", pady=2)

    def dibujar_juegos(self):
        for w in self.scroll_main.winfo_children(): w.destroy()
        
        buscando = bool(self.filtro_busqueda)
        
        self.btn_desvincular.pack_forget() 
        if not buscando and self.categoria_actual != "⭐ Favoritos":
            self.btn_desvincular.pack(side="left") 

        if buscando:
            self.lbl_titulo_seccion.configure(text=f'Buscando: "{self.search_var.get()}"')
            juegos_visibles = [j for j in self.todos_los_juegos if self.filtro_busqueda in j["nombre"].lower()]
        else:
            self.lbl_titulo_seccion.configure(text=self.categoria_actual)
            if self.categoria_actual == "⭐ Favoritos":
                juegos_visibles = [j for j in self.todos_los_juegos if j["ruta_exe"] in self.config_data["favoritos"]]
            else:
                juegos_visibles = [j for j in self.todos_los_juegos if j["categoria"] == self.categoria_actual]

        if not juegos_visibles:
            msg = "No hay juegos aquí." if not buscando else "No se encontraron resultados."
            ctk.CTkLabel(self.scroll_main, text=msg, font=("Arial", 16), text_color="gray").pack(pady=50)
            return

        grid = ctk.CTkFrame(self.scroll_main, fg_color="transparent")
        grid.pack(fill="x", padx=10)
        
        # --- NUEVO CÁLCULO DE COLUMNAS ---
        # Si la app recién se abre, el ancho puede detectarse como 1, así que asumimos 1100 por defecto
        ancho_actual = self.winfo_width() if self.winfo_width() > 10 else 1100
        ancho_disponible = ancho_actual - 220 # Descontamos los 220px del menú lateral
        ancho_tarjeta = 195 # 140px de imagen + márgenes y espaciado
        columnas_maximas = max(1, ancho_disponible // ancho_tarjeta)

        col, row = 0, 0
        for j in juegos_visibles:
            card = ctk.CTkFrame(grid, fg_color="#2b2b2b", corner_radius=10)
            card.grid(row=row, column=col, padx=12, pady=12)
            
            try:
                img = ctk.CTkImage(Image.open(j["imagen"]), size=(140, 140)) if j["imagen"] else self.img_por_defecto
            except: 
                img = self.img_por_defecto
            
            btn_img = ctk.CTkButton(card, image=img, text="", width=140, height=140, fg_color="#3d3d3d",
                                   command=lambda e=j["ruta_exe"], c=j["ruta_carpeta"]: core.lanzar_juego(e, c))
            btn_img.pack(padx=5, pady=(5, 0))
            
            nombre_corto = j["nombre"][:16] + "..." if len(j["nombre"]) > 16 else j["nombre"]
            lbl_nombre = ctk.CTkLabel(card, text=nombre_corto, font=("Arial", 13, "bold"))
            lbl_nombre.pack(pady=(5, 0))
            
            ctrls = ctk.CTkFrame(card, fg_color="transparent")
            ctrls.pack(fill="x", pady=(5, 10), padx=5)
            
            es_fav = j["ruta_exe"] in self.config_data["favoritos"]
            btn_fav = ctk.CTkButton(ctrls, text="★" if es_fav else "☆", width=35, height=30, fg_color="transparent", 
                                   text_color="#FFD700" if es_fav else "#888888", font=("Arial", 22), hover_color="#333333",
                                   command=lambda r=j["ruta_exe"]: self.toggle_favorito(r))
            btn_fav.pack(side="left")
            
            btn_portada = ctk.CTkButton(ctrls, text="🖼️", width=35, height=30, 
                                      fg_color="#8E44AD", hover_color="#9B59B6", font=("Arial", 16),
                                      command=lambda r=j["ruta_carpeta"]: self.cambiar_portada(r))
            btn_portada.pack(side="right", padx=(5, 0))

            btn_folder = ctk.CTkButton(ctrls, text="📁", width=35, height=30, 
                                      fg_color="#2980B9", hover_color="#3498DB", font=("Arial", 16),
                                      command=lambda r=j["ruta_carpeta"]: core.abrir_carpeta(r))
            btn_folder.pack(side="right")

            # --- AHORA USAMOS EL LÍMITE DINÁMICO ---
            col += 1
            if col >= columnas_maximas: 
                col = 0
                row += 1

if __name__ == "__main__":
    AppBiblioteca().mainloop()