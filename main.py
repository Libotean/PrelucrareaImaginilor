from image_io import read_bmp
from conversions import mod_gray, convert_cmyk, convert_yuv, convert_yCbCr, convert_hsv
from effects import inversare, binarize, get_channel
from analysis import calcul_histograma, calcul_momente_imagine, calcul_proiectii

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk

matrix = None
inv_matrix = None

def open_image():
    file_path = filedialog.askopenfilename(
        title="Select a BMP Image",
        filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")]
    )

    if not file_path:
        print("No file selected.")
        return

    try:
        global matrix
        matrix, w, h, bits = read_bmp(file_path)
        filename = file_path.split("/")[-1]
        status_var.set(f"{filename}  |  {w} x {h} px  |  {bits} bpp")
        afiseaza(matrix, canvas_original)
        canvas_2.delete('all')
        clear_analysis()
    except Exception as e:
        print(f"Error: {e}")

def resetare():
    global inv_matrix, matrix
    canvas_2.delete('all')
    clear_analysis()
    status_var.set("Niciun fisier deschis.")
    inv_matrix = None
    matrix = None
    canvas_original.delete('all')

def show_invert(option):
    global inv_matrix
    if option == 1:
        if matrix is None:
            return
        inv_matrix = inversare(matrix)
        afiseaza(inv_matrix, canvas_2)
    else:
        channel_map = {2: 'r', 3: 'g', 4: 'b'}
        if inv_matrix is None:
            return
        if option in channel_map:
            idx = channel_map[option]
            canal_img = get_channel(inv_matrix, idx)
            afiseaza(canal_img, canvas_2)

def clear_analysis():
    for widget in frame_analysis.winfo_children():
        widget.destroy()

def show_histogram():
    clear_analysis()
    hist = calcul_histograma(matrix)

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.bar(range(256), hist, color='gray', width=1, edgecolor='none')
    ax.set_xlim(0, 255)

    canvas_mpl = FigureCanvasTkAgg(fig, master=frame_analysis)
    canvas_mpl.draw()
    canvas_mpl.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)

def show_momente():
    if matrix is None: return
    clear_analysis()
    m_x, m_y, M_xx, M_yy, M_xy, unghi_rad, unghi_grade = calcul_momente_imagine(matrix)
    text = tk.Text(frame_analysis, font=("Courier", 11))
    text.pack(fill="both", expand=True)
    text.insert("end", f"Centru de masa: m_x = {m_x:.2f}, m_y = {m_y:.2f}\n")
    text.insert("end", f"Momente de ordin 2: M_xx = {M_xx:.2f}, M_yy = {M_yy:.2f}\n")
    text.insert("end", f"Momentul de covarianta: M_xy = {M_xy:.2f}\n")
    text.insert("end", f"Orientare (radiani): {unghi_rad:.2f}\n")
    text.insert("end", f"Orientare (grade): {unghi_grade:.2f}\n")
    text.insert("end", f"\nMatricea de covarianta:\n")
    text.insert("end", f"| {M_xx:.2f}  {M_xy:.2f} |\n")
    text.insert("end", f"| {M_xy:.2f}  {M_yy:.2f} |\n")
    text.config(state="disabled")

def show_proiectii():
    clear_analysis()
    proiectie_H, proiectie_V = calcul_proiectii(binarize(matrix))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
    ax1.plot(proiectie_H, color='blue')
    ax1.set_title("Proiectie orizontala")

    ax2.plot(proiectie_V, color='red')
    ax2.set_title("Proiectie verticala")

    canvas_mpl = FigureCanvasTkAgg(fig, master=frame_analysis)
    canvas_mpl.draw()
    canvas_mpl.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)

def afiseaza(mat, canvas):
    arr = np.array(mat, dtype=np.uint8)
    img = Image.fromarray(arr)
    MAX_W, MAX_H = 600, 600
    img.thumbnail((MAX_W, MAX_H))
    imgtk = ImageTk.PhotoImage(img)
    # canvas.config(width=img.width, height=img.height)
    canvas.create_image(300, 300, anchor="center", image=imgtk)
    canvas.image = imgtk

def center_window():
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2) - 50
    root.geometry(f"+{x}+{y}")

root = tk.Tk()
root.title("Photoshop aftermarket")
root.after(10, center_window)

# ================= MENIURI ====================
menubar = tk.Menu(root)
# fisier
menu_file = tk.Menu(menubar, tearoff=0)
menu_file.add_command(label="Deschide", command=open_image)
menu_file.add_command(label="Resetare", command=resetare)
menu_file.add_separator()
menu_file.add_command(label="Iesire", command=root.quit)
menubar.add_cascade(label="Fisier", menu=menu_file)

# conversii
menu_conversii = tk.Menu(menubar, tearoff=0)
menu_conversii.add_command(label="Gri - Media aritmetica", command=lambda: afiseaza(mod_gray(matrix, 1), canvas_2))
menu_conversii.add_command(label="Gri - Luminozitate", command=lambda: afiseaza(mod_gray(matrix, 2), canvas_2))
menu_conversii.add_command(label="Gri - Lightness", command=lambda: afiseaza(mod_gray(matrix, 3), canvas_2))
menu_conversii.add_separator()
menu_conversii.add_command(label="CMYK", command=lambda: afiseaza(convert_cmyk(matrix), canvas_2))
menu_conversii.add_command(label="YUV", command=lambda: afiseaza(convert_yuv(matrix), canvas_2))
menu_conversii.add_command(label="YCbCr", command=lambda: afiseaza(convert_yCbCr(matrix), canvas_2))
menu_conversii.add_command(label="HSV", command=lambda: afiseaza(convert_hsv(matrix), canvas_2))
menubar.add_cascade(label="Conversii", menu=menu_conversii)

# efecte
menu_efecte = tk.Menu(menubar, tearoff=0)
menu_efecte.add_command(label="Binarizare", command=lambda: afiseaza(binarize(matrix), canvas_2))
menu_inversare = tk.Menu(menu_efecte, tearoff=0)
menu_inversare.add_command(label="Afiseaza inversata", command=lambda: show_invert(1))
menu_inversare.add_command(label="Canal R", command=lambda: show_invert(2))
menu_inversare.add_command(label="Canal G", command=lambda: show_invert(3))
menu_inversare.add_command(label="Canal B", command=lambda: show_invert(4))

menu_efecte.add_cascade(label="Inversare", menu=menu_inversare)
menubar.add_cascade(label="Efecte", menu=menu_efecte)

# analiza
menu_analiza = tk.Menu(menubar, tearoff=0)
menu_analiza.add_command(label="Histograma", command=show_histogram)
menu_analiza.add_command(label="Momente", command=show_momente)
menu_analiza.add_command(label="Proiectii", command=show_proiectii)
menubar.add_cascade(label="Analiza", menu=menu_analiza)
root.config(menu=menubar)

frame_poze = tk.Frame(root)
frame_poze.pack()

canvas_original = tk.Canvas(frame_poze, width=600, height=600, bg="lightgray")
canvas_original.pack(side="left", padx=5, pady=5)

canvas_2 = tk.Canvas(frame_poze, width=600, height=600, bg="lightgray")
canvas_2.pack(side="left", padx=5, pady=5)

frame_analysis = tk.Frame(root, height=250, bg="#1e1e1e")
frame_analysis.pack(fill="x", padx=5, pady=5)
frame_analysis.pack_propagate(False) 

status_var = tk.StringVar(value="Niciun fisier deschis")

status_bar = tk.Label(root, textvariable=status_var, anchor="w")
status_bar.pack(fill="x", side="bottom")

root.mainloop()