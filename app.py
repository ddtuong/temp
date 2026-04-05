import tkinter as tk
from tkinter import Text, ttk, Message, END
from util import *
import cv2 as cv
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Smart Pokayoke")
root.geometry("900x600")

# =========================
# MAIN FRAME
# =========================
main_frame = tk.Frame(root, bg="white", highlightbackground="green", highlightthickness=2)
main_frame.pack(fill="both", expand=True, padx=5, pady=5)

# =========================
# GRID CONFIG
# =========================
main_frame.rowconfigure(0, weight=0)  # header
main_frame.rowconfigure(1, weight=0)  # control
main_frame.rowconfigure(2, weight=1)  # canvas (giãn mạnh) Vertical expansion

main_frame.columnconfigure(0, weight=1) # Horizontal expansion

# =========================
# HEADER: DONE
# =========================
header = tk.Frame(main_frame, bg="white")
header.grid(row=0, column=0, sticky="ew", padx=10, pady=5) # coordinate (0,0) and expand horizontally ("ew")

header.columnconfigure(0, weight=1) # horizontal expansion
header.columnconfigure(1, weight=0)

tk.Label(header, text="Smart Pokayoke",
         fg="red", bg="white",
         font=("Arial", 16, "bold")
).grid(row=0, column=0, sticky="w")

btn_frame = tk.Frame(header, bg="white")
btn_frame.grid(row=0, column=1, sticky="e")

def create_btn(parent, text, width=12, color="green", command=None):
    return tk.Button(parent, text=text,
                     fg=color,
                     highlightbackground=color,
                     highlightthickness=1,
                     width=width,
                     command=command,
                     relief="flat")

log_out_btn = create_btn(btn_frame, "Đăng xuất", command= lambda: log_out(log_out_btn))
exit_btn = create_btn(btn_frame, "Thoát", command=root.destroy)

log_out_btn.pack(side="left", padx=5)
exit_btn.pack(side="left", padx=5)

# =========================
# CONTROL PANEL: DONE
# =========================
control = tk.Frame(main_frame, bg="white")
control.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

for i in range(6):
    control.columnconfigure(i, weight=1)

tk.Label(control, text="Chọn COM:",
         fg="black", bg="white",
         font=("Arial", 12, ) # "bold"
).grid(row=0, column=0, sticky="e")
 
combo_box = ttk.Combobox(
    control,
    values=["COM1"],
    state="readonly"
)
combo_box.set("COM1")
refresh_btn = create_btn(control, "Làm mới", command= lambda: refresh_com_ports(refresh_btn, combo_box))
connect_btn = create_btn(control, "Kết nối", command= lambda: connect(connect_btn, combo_box))
save_run_btn = create_btn(control, "LƯU & CHẠY NGẦM", command= lambda: save_and_run(save_run_btn))
pause_btn = create_btn(control, "DỪNG", command= lambda: pause(pause_btn))
log_out_btn = create_btn(control, "Đăng xuất", command= lambda: log_out(log_out_btn))

# code_entry = tk.Entry(control)
code_text = Text(control, height=1, width=50, fg="red", bg="white", font=("Arial", 12, "bold"), bd=1, relief="solid")
code_text.insert(END, "Chưa có mã code nào được scan...")
code_text.config(state="disabled")
# set position for the variable
combo_box.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
refresh_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)
connect_btn.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
save_run_btn.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
pause_btn.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
tk.Label(control, text="Mã Code Scan được:",
         fg="black", bg="white",
         font=("Arial", 12, ) # "bold"
).grid(row=2, column=0, sticky="e")
code_text.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

# =========================
# CANVAS (FULL RESPONSIVE)
# =========================
# canvas = tk.Canvas(main_frame,
#                    bg="white",
#                    highlightbackground="red",
#                    highlightthickness=2)

# canvas.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
main_frame.rowconfigure(2, weight=1, minsize=400)   # 👈 chiều cao tối thiểu
main_frame.columnconfigure(0, weight=1, minsize=400)  # 👈 chiều rộng tối thiểu

canvas = tk.Canvas(
    main_frame,
    width=400,   # 👈 chiều rộng
    height=400,  # 👈 chiều cao
    bg="green",
    highlightbackground="red",
    highlightthickness=2
)

canvas.grid(row=2, column=0,sticky="nsew", padx=10, pady=10) # , sticky="nsew"

# =========================
# CAMERA SETUP
# =========================
cap = cv.VideoCapture(0)  # 0 = webcam

def update_frame():
    ret, frame = cap.read()
    if ret:
        # chuyển BGR → RGB
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        # resize theo canvas
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        frame = cv.resize(frame, (canvas_width, canvas_height))
        print(f"Canvas size: {canvas_width}x{canvas_height}, Frame size: {frame.shape[1]}x{frame.shape[0]}")
        # convert sang Tkinter image
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        # hiển thị
        canvas.create_image(0, 0, anchor="nw", image=imgtk)
        canvas.imgtk = imgtk  # giữ reference

    root.after(10, update_frame)  # loop

update_frame()

root.mainloop()