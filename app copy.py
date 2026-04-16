import tkinter as tk
from tkinter import Text, ttk, Message, END, scrolledtext
from util import *
import cv2 as cv
from PIL import Image, ImageTk
import os
from tkinter import messagebox
import time


class SmartPokayokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Pokayoke")
        self.root.geometry("1000x750")

        # bind space (giữ nguyên)
        self.root.bind("<space>", on_space_press)

        # =========================
        # MAIN FRAME
        # =========================
        self.main_frame = tk.Frame(root, bg="white", highlightbackground="green", highlightthickness=2)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # =========================
        # GRID
        # =========================
        self.main_frame.rowconfigure(0, weight=0)
        self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.rowconfigure(2, weight=0)
        self.main_frame.columnconfigure(0, weight=1)

        # =========================
        # HEADER
        # =========================
        self.header = tk.Frame(self.main_frame, bg="white")
        self.header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=0)

        tk.Label(self.header, text="Smart Pokayoke",
                 fg="red", bg="white",
                 font=("Arial", 16, "bold")
                 ).grid(row=0, column=0, sticky="w")

        self.btn_frame = tk.Frame(self.header, bg="white")
        self.btn_frame.grid(row=0, column=1, sticky="e")

        self.log_out_btn = tk.Button(self.btn_frame, text="Đăng xuất", fg="green",
                                    command=lambda: log_out(self.log_out_btn),
                                    font=("Times New Roman", 12), relief="flat")

        self.exit_btn = tk.Button(self.btn_frame, text="Thoát", fg="green",
                                  command=self.root.destroy,
                                  font=("Times New Roman", 12), relief="flat")

        self.log_out_btn.pack(side="left", padx=5)
        self.exit_btn.pack(side="left", padx=5)

        # =========================
        # CONTROL PANEL
        # =========================
        self.control = tk.Frame(self.main_frame, bg="white")
        self.control.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        for i in range(6):
            self.control.columnconfigure(i, weight=1)

        tk.Label(self.control, text="Chọn COM:",
                 fg="black", bg="white",
                 font=("Arial", 12)
                 ).grid(row=0, column=0, sticky="e")

        self.combo_box = ttk.Combobox(self.control, values=["COM1"], state="readonly")
        self.combo_box.set("COM1")

        self.refresh_btn = tk.Button(self.control, text="Làm mới", fg="green",
                                     command=lambda: refresh_com_ports(self.refresh_btn, self.combo_box),
                                     font=("Times New Roman", 12), relief="flat")

        self.connect_btn = tk.Button(self.control, text="Kết nối", fg="green",
                                     command=lambda: connect(self.connect_btn, self.combo_box),
                                     font=("Times New Roman", 12), relief="flat")

        self.save_run_btn = tk.Button(self.control, text="LƯU & CHẠY NGẦM", fg="green",
                                      command=lambda: save_and_run(self.save_run_btn),
                                      font=("Times New Roman", 12, "bold"), relief="flat")

        self.pause_btn = tk.Button(self.control, text="DỪNG", fg="green",
                                   command=lambda: pause(self.pause_btn),
                                   font=("Times New Roman", 12, "bold"), relief="flat")

        self.draw_bbox_btn = tk.Button(self.control, text="VẼ BOUNDING BOX",
                                       command=lambda: toggle_draw(self.canvas, state),
                                       fg="red", font=("Times New Roman", 12, "bold"),
                                       relief="flat")

        # grid control
        self.combo_box.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.refresh_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)
        self.connect_btn.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        self.save_run_btn.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.pause_btn.grid(row=1, column=2, sticky="ew", padx=5, pady=5)
        self.draw_bbox_btn.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        # TEXT
        self.code_text = scrolledtext.ScrolledText(
            self.control,
            wrap=tk.WORD,
            height=5,
            font=("Consolas", 11, "italic"),
            bd=1,
            relief="solid",
            bg="#0f172a",
            fg="#22c55e",
            insertbackground="white"
        )
        self.code_text.insert(END, "Chưa có mã code nào được scan...")
        self.code_text.config(state="disabled")

        tk.Label(self.control, text="Mã Code:",
                 fg="black", bg="white",
                 font=("Arial", 12)
                 ).grid(row=2, column=0, sticky="e")

        self.code_text.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        # =========================
        # CANVAS
        # =========================
        self.canvas = tk.Canvas(
            self.main_frame,
            highlightbackground="red",
            highlightthickness=2
        )
        self.canvas.grid(row=3, column=0, padx=10, pady=10)

        # =========================
        # CAMERA
        # =========================
        self.cap = cv.VideoCapture(0)
        self.canvas_img = self.canvas.create_image(0, 0, anchor="nw")

        self.current_frame = None

        self.last_predict_time = 0
        self.PREDICT_INTERVAL = 0.5

        # =========================
        # BIND SPACE (giữ nguyên)
        # =========================
        self.root.bind(
            "<KeyPress-space>",
            lambda event: on_space_press(event, state)
        )

        self.root.bind(
            "<KeyRelease-space>",
            lambda event: on_space_release(event, state)
        )

        # LOOP
        self.update_frame()

    # =========================
    # FRAME UPDATE (GIỮ NGUYÊN LOGIC)
    # =========================
    def update_frame(self):
        global state

        ret, frame = self.cap.read()
        if ret:
            frame = cv.flip(frame, 1)

            if state["points"]:
                if state["press_keyboard"]:
                    now = time.time()

                    if now - self.last_predict_time > self.PREDICT_INTERVAL:
                        self.last_predict_time = now
                        state["predict_result"] = predict("dummy input") + str(int(now))
                else:
                    state["predict_result"] = None

                color = (0, 255, 0) if state["predict_result"] == "On" else (0, 0, 255)
                text = f"Predict model: {state['predict_result']}"

                cv.putText(
                    frame,
                    text,
                    (10, 30),
                    cv.FONT_HERSHEY_SIMPLEX,
                    1,
                    color,
                    2
                )

            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

            h, w, _ = frame.shape
            self.canvas.config(width=w, height=h)

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.canvas.itemconfig(self.canvas_img, image=imgtk)
            self.canvas.imgtk = imgtk

            if state["rect_id"] is not None:
                self.canvas.tag_raise(state["rect_id"])

        self.root.after(10, self.update_frame)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartPokayokeApp(root)
    root.mainloop()