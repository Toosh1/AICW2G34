import tkinter as tk
from datetime import datetime

def get_bot_response(user_input):
    bot_response = ""
    return bot_response

def send_message():
    user_input = entry_box.get().strip()
    if user_input == "":
        return

    add_chat_bubble(user_input, is_user=True)
    entry_box.delete(0, tk.END)

    root.after(300, lambda: add_chat_bubble(get_bot_response(user_input), is_user=False))

def add_chat_bubble(text, is_user):
    time_sent = datetime.now().strftime('%H:%M  %d/%m/%Y')

    outer_frame = tk.Frame(chat_canvas_frame, bg="#fcfcfc")
    outer_frame.pack(fill='x', pady=5)

    outer_frame.grid_columnconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(1, weight=1)

    bubble_frame = tk.Frame(outer_frame, bg="#fcfcfc")

    bubble_bg = "#daf0e0" if is_user else "#d5eef2"

    bubble = tk.Label(
        bubble_frame,
        text=text,
        wraplength=300,
        justify=tk.LEFT,
        padx=10,
        pady=7,
        bg=bubble_bg,
        fg="black",
        font=("Arial", 11),
        bd=0,
        relief="solid"
    )
    bubble.pack(anchor='e' if is_user else 'w')

    timestamp = tk.Label(
        bubble_frame,
        text=time_sent,
        bg="#fcfcfc",
        fg="gray",
        font=("Arial", 8),
        padx=5
    )
    timestamp.pack(anchor='e' if is_user else 'w')

    if is_user:
        bubble_frame.grid(row=0, column=1, sticky='e', padx=(0, 10))
    else:
        bubble_frame.grid(row=0, column=0, sticky='w', padx=(10, 0))

    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1.0)

root = tk.Tk()
root.title("Pisces: Train Chatbot")
root.geometry("500x600")

chat_canvas = tk.Canvas(root, bg="#fcfcfc")
chat_scrollbar = tk.Scrollbar(root, command=chat_canvas.yview)
chat_canvas.configure(yscrollcommand=chat_scrollbar.set)

chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chat_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

chat_canvas_frame = tk.Frame(chat_canvas, bg="#fcfcfc")
chat_canvas.create_window((0, 0), window=chat_canvas_frame, anchor='nw')

def on_frame_configure(event):
    chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))

chat_canvas_frame.bind("<Configure>", on_frame_configure)

bottom_frame = tk.Frame(root, bg="white")
bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

entry_box = tk.Entry(bottom_frame, font=("Arial", 12))
entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5), pady=10)
entry_box.bind("<Return>", lambda event: send_message())

send_button = tk.Button(bottom_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT, padx=(5, 10), pady=10)

entry_box.focus()
root.mainloop()