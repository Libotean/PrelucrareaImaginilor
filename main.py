import math
import cv2
from image_io import read_bmp
from conversions import mod_gray, convert_cmyk, convert_yuv, convert_yCbCr, convert_hsv
from effects import inversare, binarize, get_channel, apply_neighbor_filter, apply_sharpen, apply_neighbor_filter_color, apply_sharpen_color, apply_floyd_steinberg
from analysis import calcul_histograma, calcul_momente_imagine, calcul_proiectii, equalize_histogram, apply_morphology, opening, closing, apply_fourier
from etichetare import directie_alungire, etichetare, extrage_obiect
from lab8 import remove_gaussian_noise, laplacian_filter
from lab9 import edge_detect, apply_canny_edge_detection

import tkinter as tk
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk

matrix = None
inv_matrix = None
labels_matrix  = None
num_labels_val = 0 

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

        frame_etichetare.pack_forget()
        label_unghi.pack_forget()

        global labels_matrix, num_labels_val
        labels_matrix = None
        num_labels_val = 0
    except Exception as e:
        print(f"Error: {e}")

def resetare():
    global inv_matrix, matrix, labels_matrix
    canvas_2.delete('all')
    canvas_original.delete('all')
    clear_analysis()
    status_var.set("Niciun fisier deschis.")
    inv_matrix = None
    matrix = None
    labels_matrix = None
    frame_etichetare.pack_forget()
    label_unghi.pack_forget()

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

def show_orientation():
    clear_analysis()
    orientare_rad, orientare_deg = directie_alungire(matrix)
    text = tk.Text(frame_analysis, font=("Courier", 11))
    text.pack(fill="both", expand=True)
    text.insert("end", f"Directia de alungire (radiani): {orientare_rad:.2f}\n")
    text.insert("end", f"Directia de alungire (grade): {orientare_deg:.2f}\n")
    text.config(state="disabled")

def aplica_etichetare():
    global labels_matrix, num_labels_val

    imagine_colorata, labels_matrix, num_labels_val = etichetare(matrix)
    afiseaza(imagine_colorata, canvas_2)

    frame_etichetare.pack(before=frame_poze)
    label_unghi.pack(after=frame_etichetare)

    # Actualizeaza optiunile din dropdown
    optiuni = [str(i) for i in range(1, num_labels_val + 1)]
    dropdown_etichete["values"] = optiuni
    if optiuni:
        dropdown_etichete.current(0)

def selectie_obiect(event=None):
    if labels_matrix is None:
        return

    eticheta = int(dropdown_etichete.get())
    obiect   = extrage_obiect(matrix, labels_matrix, eticheta)
    afiseaza(obiect, canvas_2)

    unghi_rad, unghi_grade = directie_alungire(obiect)
    label_unghi.config(text=f"Directie alungire: {unghi_grade:.2f}° ({unghi_rad:.4f} rad)")

def show_equalization():
    if matrix is None: return
    res = equalize_histogram(matrix, len(matrix[0]), len(matrix))
    afiseaza(res, canvas_2)

def show_morphology(op_type):
    if matrix is None: return
    
    kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    
    bin_img = binarize(matrix)
    if op_type == "dilate":
        res = apply_morphology(bin_img, kernel, mode='dilate')
    elif op_type == "erode":
        res = apply_morphology(bin_img, kernel, mode='erode')
    elif op_type == "open":
        res = opening(bin_img, kernel)
    elif op_type == "close":
        res = closing(bin_img, kernel)
        
    afiseaza(res, canvas_2)

def show_edge_detection(filter_type):
    if matrix is None: 
        return

    res = edge_detect(matrix, filter_type)
    
    afiseaza(res, canvas_2)

def show_opencv_canny():
    if matrix is None:
        return
    
    img_np = np.array(matrix, dtype=np.uint8)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    t_lower = 100
    t_upper = 200
    edges = cv2.Canny(img_bgr, t_lower, t_upper, L2gradient=True)
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    
    res = edges_rgb.tolist()

    afiseaza(res, canvas_2)

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
menu_morfologie = tk.Menu(menu_efecte, tearoff=0)
menu_morfologie.add_command(label="Dilatare", command=lambda: show_morphology("dilate"))
menu_morfologie.add_command(label="Eroziune", command=lambda: show_morphology("erode"))
menu_morfologie.add_command(label="Deschidere (Opening)", command=lambda: show_morphology("open"))
menu_morfologie.add_command(label="Inchidere (Closing)", command=lambda: show_morphology("close"))
menu_efecte.add_cascade(label="Morfologie Binara", menu=menu_morfologie)
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
menu_analiza.add_command(label="Egalizare Histograma", command=show_equalization)
menu_analiza.add_command(label="Momente", command=show_momente)
menu_analiza.add_command(label="Proiectii", command=show_proiectii)
menu_analiza.add_command(label="Transformata Fourier", command=lambda: afiseaza(apply_fourier(matrix), canvas_2))
menubar.add_cascade(label="Analiza", menu=menu_analiza)

# etichetare
menu_etichetare = tk.Menu(menubar, tearoff=0)
menu_etichetare.add_command(label="Directia de alungire", command=show_orientation)
menu_etichetare.add_command(label="Etichetare", command=aplica_etichetare)
menubar.add_cascade(label="Etichetare", menu=menu_etichetare)

# filtre
menu_filtre = tk.Menu(menu_efecte, tearoff=0)
menu_filtre.add_command(label="Mediere (Mean)", command=lambda: afiseaza(apply_neighbor_filter(matrix, 'mean'), canvas_2))
menu_filtre.add_command(label="Median", command=lambda: afiseaza(apply_neighbor_filter(matrix, 'median'), canvas_2))
menu_filtre.add_command(label="Minim", command=lambda: afiseaza(apply_neighbor_filter(matrix, 'min'), canvas_2))
menu_filtre.add_command(label="Maxim", command=lambda: afiseaza(apply_neighbor_filter(matrix, 'max'), canvas_2))
menu_filtre.add_command(label="Accentuare (Sharpen)", command=lambda: afiseaza(apply_sharpen(matrix), canvas_2))
menu_efecte.add_cascade(label="Filtre Spatiale", menu=menu_filtre)
menu_filtre_color = tk.Menu(menu_efecte, tearoff=0)
menu_filtre_color.add_command(label="Mediere (Mean)", command=lambda: afiseaza(apply_neighbor_filter_color(matrix, 'mean'), canvas_2))
menu_filtre_color.add_command(label="Median", command=lambda: afiseaza(apply_neighbor_filter_color(matrix, 'median'), canvas_2))
menu_filtre_color.add_command(label="Minim", command=lambda: afiseaza(apply_neighbor_filter_color(matrix, 'min'), canvas_2))
menu_filtre_color.add_command(label="Maxim", command=lambda: afiseaza(apply_neighbor_filter_color(matrix, 'max'), canvas_2))
menu_filtre_color.add_command(label="Floyd-Steinberg", command=lambda: afiseaza(apply_floyd_steinberg(matrix), canvas_2))
menu_filtre_color.add_command(label="Accentuare (Sharpen)", command=lambda: afiseaza(apply_sharpen_color(matrix), canvas_2))
menu_efecte.add_cascade(label="Filtre Spatiale color", menu=menu_filtre_color)

menu_lab8 = tk.Menu(menubar, tearoff=0)
menu_lab8.add_command(label="Eliminare Zgomot Gaussian", command=lambda: afiseaza(remove_gaussian_noise(matrix), canvas_2))
menu_lab8.add_command(label="Filtru Laplacian", command=lambda: afiseaza(laplacian_filter(matrix), canvas_2))
menubar.add_cascade(label="Lab8", menu=menu_lab8)

menu_contur = tk.Menu(menu_efecte, tearoff=0)
menu_contur.add_command(label="Vertical Simplu", command=lambda: show_edge_detection(1))
menu_contur.add_command(label="Orizontal Simplu", command=lambda: show_edge_detection(2))
menu_contur.add_separator()
menu_contur.add_command(label="Sobel Vertical", command=lambda: show_edge_detection(3))
menu_contur.add_command(label="Sobel Orizontal", command=lambda: show_edge_detection(4))
menu_contur.add_separator()
menu_contur.add_command(label="Scharr Vertical", command=lambda: show_edge_detection(5))
menu_contur.add_command(label="Scharr Orizontal", command=lambda: show_edge_detection(6))
menu_contur.add_separator()
menu_contur.add_command(label="Metoda Canny", command=lambda: afiseaza(apply_canny_edge_detection(matrix), canvas_2))
menu_contur.add_separator()
menu_contur.add_command(label="Canny (OpenCV) - Comparatie", command=show_opencv_canny)

menu_efecte.add_cascade(label="Detectie Contur", menu=menu_contur)

root.config(menu=menubar)

frame_etichetare = tk.Frame(root)
# frame_etichetare.pack()

dropdown_etichete = ttk.Combobox(frame_etichetare, width=10, state="readonly")
dropdown_etichete.pack(side="left", padx=5)
dropdown_etichete.bind("<<ComboboxSelected>>", selectie_obiect)

label_unghi = tk.Label(root, text="Directie alungire: -")

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