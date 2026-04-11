import os
from tkinter import messagebox
import keyboard

state = {
    "rect_id": None,
    "draw_mode": False,
    "start_x": None,
    "start_y": None,
    "points": [],
    "predict_result": None,
    "tracking": False,
}

def connect(btn_connect, combo_box):
    print(f"Connecting to {combo_box.get()}...")

def refresh_com_ports(btn_refresh, combo_box):
    print("Refreshing COM ports...")

def save_and_run(btn_save_run):
    print("Saving and running...")

def pause(btn_pause):
    print("Pausing...")

def log_out(btn_log_out):
    print("Logging out...")
    
def load_box_from_file(canvas, state):
    try:
        with open("coordinate.txt", "r") as f:
            content = f.read().strip()

        if not content:
            messagebox.showerror("Lỗi", "File rỗng!")
            return False

        data = content.split(",")
        if len(data) != 4:
            messagebox.showerror("Lỗi", "Định dạng file sai!")
            return False

        x1, y1, x2, y2 = map(int, data)
        state["points"] = [x1, y1, x2, y2]

        if state["rect_id"] is not None:
            canvas.delete(state["rect_id"])

        state["rect_id"] = canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="blue",
            width=2
        )

        return True

    except:
        messagebox.showerror("Lỗi", "File không tồn tại!")
        return False
    
def on_mouse_down(event, canvas, state):
    state["start_x"], state["start_y"] = event.x, event.y

    if state["rect_id"] is not None:
        canvas.delete(state["rect_id"])

    state["rect_id"] = canvas.create_rectangle(
        state["start_x"], state["start_y"],
        state["start_x"], state["start_y"],
        outline="red",
        width=2
    )

def on_mouse_drag(event, canvas, state):
    if state["rect_id"] is not None:
        canvas.coords(
            state["rect_id"],
            state["start_x"], state["start_y"],
            event.x, event.y
        )

def on_mouse_up(event, canvas, state):
    x1, y1 = state["start_x"], state["start_y"]
    x2, y2 = event.x, event.y

    # Chuẩn hóa tọa độ (x1, y1) là góc trên bên trái, (x2, y2) là góc dưới bên phải
    x1, x2 = sorted([x1, x2])
    y1, y2 = sorted([y1, y2])

    state["points"] = [x1, y1, x2, y2]

    # lưu file
    try:
        with open("coordinate.txt", "w") as f:
            f.write(f"{x1},{y1},{x2},{y2}")

        messagebox.showinfo("Thông báo", "Đã lưu file tọa độ thành công!")
    except:
        messagebox.showerror("Lỗi", "Có lỗi khi lưu file!")

    state["start_x"], state["start_y"] = None, None

    # tắt draw mode
    canvas.unbind("<Button-1>")
    canvas.unbind("<B1-Motion>")
    canvas.unbind("<ButtonRelease-1>")
    state["draw_mode"] = False

    print("Draw mode OFF")

def toggle_draw(canvas, state):
    # if state["rect_id"] is not None:
    #     canvas.delete(state["rect_id"])
    if os.path.exists("coordinate.txt"):
        result = messagebox.askyesno(
            "Thông báo",
            "Đã tồn tại bounding box.\nBạn có muốn vẽ lại không?"
        )

        if not result:
            if load_box_from_file(canvas, state):
                messagebox.showinfo("Thông báo", "Đã tải bounding box cũ!")
                return
            else:
                messagebox.showerror("Lỗi", "Không thể load!")
                os.remove("coordinate.txt")
        else:
            os.remove("coordinate.txt")

    state["draw_mode"] = True

    canvas.bind("<Button-1>", lambda e: on_mouse_down(e, canvas, state))
    canvas.bind("<B1-Motion>", lambda e: on_mouse_drag(e, canvas, state))
    canvas.bind("<ButtonRelease-1>", lambda e: on_mouse_up(e, canvas, state))

    print("Draw mode ON")

def predict(string=None):
    return "On" if string is not None else "Off"

def on_space_press(event, state, get_frame):
    state["tracking"] = True
    frame = get_frame()

    # if frame is None:
    #     print("Chưa có frame!")
    #     return

    if not state["points"]:
        messagebox.showerror("Lỗi", "Chưa có bounding box!")
        return 

    state["predict_result"] = predict("dummy input")    

    # x1, y1, x2, y2 = state["points"]

    # # crop
    # crop = frame[y1:y2, x1:x2]

    # # predict
    # result = predict_func(crop)

    # set_predict_result(result)

    # print("Predict:", result)

def on_space_release(event):
    state["tracking"] = False
    # if event.keysym == "space":
    #     state["predict_result"] = None
    pass