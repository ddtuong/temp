import tkinter as tk
from tkinter import Text, ttk, Message, END, scrolledtext

from util import *
import cv2 as cv
from PIL import Image, ImageTk
import os
from tkinter import messagebox
root = tk.Tk()
root.title("Smart Pokayoke")
root.geometry("1000x750")

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
main_frame.rowconfigure(2, weight=0)  # scanned code panel
# main_frame.rowconfigure(3, weight=1)  # canvas (giãn mạnh) Vertical expansion

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

log_out_btn = tk.Button(btn_frame, text="Đăng xuất", fg="green", command=lambda: log_out(log_out_btn), font=("Times New Roman", 12), relief="flat")
exit_btn = tk.Button(btn_frame, text="Thoát", fg="green", command=root.destroy, font=("Times New Roman", 12), relief="flat")

log_out_btn.pack(side="left", padx=5)
exit_btn.pack(side="left", padx=5)

# =========================
# CONTROL PANEL: DONE
# =========================

# =========================
# DRAW BOUNDING BOX
# =========================
points = []
rect_id = None
draw_mode = False
def load_box_from_file():
    global rect_id

    try:
        with open("coordinate.txt", "r") as f:
            content = f.read().strip()

        if not content:
            print("File rỗng!")
            return False

        data = content.split(",")
        if len(data) != 4:
            print("Sai format!")
            return False

        x1, y1, x2, y2 = map(int, data)

        if rect_id is not None:
            canvas.delete(rect_id)

        rect_id = canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="blue",
            width=2
        )

        print("Loaded box from file")
        return True

    except Exception as e:
        print("Error:", e)
        return False

def on_click(event):
    global points, rect_id, draw_mode

    x, y = event.x, event.y
    points.append((x, y))

    if len(points) == 2:
        (x1, y1), (x2, y2) = points

        if rect_id is not None:
            canvas.delete(rect_id)

        rect_id = canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red",
            width=2
        )

        # 🔥 LUÔN LƯU FILE
        try:
            with open("coordinate.txt", "w") as f:
                f.write(f"{x1},{y1},{x2},{y2}")
            print("Saved coordinate.txt")
        except Exception as e:
            print("Save error:", e)

        # reset
        points = []

        # tắt draw mode
        canvas.unbind("<Button-1>")
        draw_mode = False
        print("Draw mode OFF (auto)")
   
def toggle_draw():
    global draw_mode

    if os.path.exists("coordinate.txt"):
        result = messagebox.askyesno(
            "Thông báo",
            "Đã tồn tại bounding box.\nBạn có muốn vẽ lại không?"
        )

        if not result:  # NO → dùng box cũ
            if load_box_from_file():
                return
            else:
                messagebox.showerror(
                    "Lỗi",
                    "Không thể tải bounding box cũ! Bạn hãy vẽ lại."
                )
                print("Load failed → switching to draw mode")
                os.remove("coordinate.txt")
                print("Deleted old file")

        else:  # YES → vẽ lại
            os.remove("coordinate.txt")
            print("Deleted old file")

    # bật draw mode
    draw_mode = True
    canvas.bind("<Button-1>", on_click)
    print("Draw mode ON")

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
refresh_btn = tk.Button(control,text="Làm mới", fg="green", command= lambda: refresh_com_ports(refresh_btn, combo_box), font=("Times New Roman", 12), relief="flat")
connect_btn = tk.Button(control, text="Kết nối", fg="green", command= lambda: connect(connect_btn, combo_box), font=("Times New Roman", 12), relief="flat")
save_run_btn = tk.Button(control, text="LƯU & CHẠY NGẦM", fg="green", command= lambda: save_and_run(save_run_btn), font=("Times New Roman", 12, "bold"), relief="flat")
pause_btn = tk.Button(control, text="DỪNG", fg="green", command= lambda: pause(pause_btn), font=("Times New Roman", 12, "bold"), relief="flat")
draw_bbox_btn = tk.Button(control, text="VẼ BOUNDING BOX", command=toggle_draw, fg="red", font=("Times New Roman", 12, "bold"), relief="flat")

# set position for the variable
combo_box.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
refresh_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)
connect_btn.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
save_run_btn.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
pause_btn.grid(row=1, column=2, sticky="ew", padx=5, pady=5)
draw_bbox_btn.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

code_text = scrolledtext.ScrolledText(
    control, 
    wrap=tk.WORD, 
    height=5, 
    font=("Consolas", 11, "italic"),
    bd=1,
    relief="solid",
    bg="#0f172a",   
    fg="#22c55e",   
    insertbackground="white"
)
code_text.insert(END, "Chưa có mã code nào được scan...")
code_text.config(state="disabled")

tk.Label(control, text="Mã Code:",
         fg="black", bg="white",
         font=("Arial", 12, ) # "bold"
).grid(row=2, column=0, sticky="e") # sticky="ew", padx=5, pady=5
code_text.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

# =========================
# CANVAS (FULL RESPONSIVE)
# =========================


canvas = tk.Canvas(
    main_frame,
    # width=640,
    # height=480,
    # bg="green",
    highlightbackground="red",
    highlightthickness=2
)

canvas.grid(row=3, column=0, padx=10, pady=10) # , sticky="nsew"

# =========================
# CAMERA SETUP
# =========================
cap = cv.VideoCapture(0)  # 0 = webcam
# tạo image ban đầu (quan trọng)
canvas_img = canvas.create_image(0, 0, anchor="nw")

def update_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv.flip(frame, 1)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        # lấy kích thước frame
        h, w, _ = frame.shape

        # ✅ set lại kích thước canvas theo frame
        canvas.config(width=w, height=h)

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        canvas.itemconfig(canvas_img, image=imgtk)
        canvas.imgtk = imgtk

        # giữ rectangle luôn ở trên
        if rect_id is not None:
            canvas.tag_raise(rect_id)
    root.after(10, update_frame)

update_frame()

root.mainloop()