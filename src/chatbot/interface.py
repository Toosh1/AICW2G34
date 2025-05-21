import tkinter as tk
from datetime import datetime

def get_bot_response(user_input):
    bot_response = user_input
    return bot_response

def send_message():
    user_input = entry_box.get().strip()
    if user_input == "":
        return

    add_message(user_input, is_user=True)
    entry_box.delete(0, tk.END)

    root.after(300, lambda: add_message(get_bot_response(user_input), is_user=False))

def add_message(text, is_user):
    time_sent = datetime.now().strftime('%H:%M')

    row = tk.Frame(chat_frame)
    row.pack( fill='x', pady=2, padx=5, anchor='e' if is_user else 'w')

    msg_bg = "#a0d8ef" if is_user else "#e0e0e0"

    msg = tk.Label(
        row,
        text=text,
        padx=10,
        pady=10,
        bg=msg_bg,
        fg="black",
        font=("Arial", 11),
    )

    msg.pack(side='right' if is_user else 'left', anchor='e' if is_user else 'w')

    timestamp = tk.Label(
        row,
        text=time_sent,
        bg="#F0F0F0",
        fg="#818181",
        font=("Arial", 8),
        padx=5
    )
    timestamp.pack(anchor='e' if is_user else 'w')


def main():
    global root, chat_frame, entry_box
    root = tk.Tk()
    root.title("Pisces: Train Chatbot")
    root.geometry("500x600")

    chat_frame = tk.Canvas(root, bg="#F0F0F0")

    chat_scrollbar = tk.Scrollbar(root, command=chat_frame.yview)
    chat_frame.configure(yscrollcommand=chat_scrollbar.set)

    chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    chat_canvas_frame = tk.Frame(chat_frame, bg="#F0F0F0")
    chat_frame.create_window((0, 0), window=chat_canvas_frame, anchor='nw')

    def on_frame_configure(event):
        chat_frame.configure(scrollregion=chat_frame.bbox("all"))

    chat_canvas_frame.bind("<Configure>", on_frame_configure)

    bottom_frame = tk.Frame(root, bg="white")
    bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

    entry_box = tk.Entry(bottom_frame, font=("Arial", 12))
    entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5), pady=10)
    entry_box.bind("<Return>", lambda event: send_message())

    send_button = tk.Button(bottom_frame, text="Send", command=send_message)
    send_button.pack(side=tk.RIGHT, padx=(5, 10), pady=10)

    root.mainloop()