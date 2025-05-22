from datetime import datetime

def get_bot_response(user_input):
    bot_response = user_input
    return bot_response

def send_message():
    """
    Takes input from the entry box and adds it to the chat frame
    """
    user_input = entry_box.get().strip()
    if user_input == "":
        return

    add_message(user_input, is_user=True)
    entry_box.delete(0, tk.END)

    root.after(300, lambda: add_message(get_bot_response(user_input), is_user=False))
    root.after(100, lambda: chat_frame.yview_moveto(1.0))

def add_message(text, is_user):
    """
    Creates labels for the message box and the (formatted) timestamp
    """
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

    chat_canvas_frame.update_idletasks()
    chat_frame.configure(scrollregion=chat_frame.bbox("all"))
    chat_frame.yview_moveto(1.0)

import tkinter as tk

root = tk.Tk()
root.title("Pisces: Train Chatbot")
root.geometry("500x600")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

chat_wrapper = tk.Frame(root)
chat_wrapper.grid(row=0, column=0, sticky="nsew")

chat_frame = tk.Canvas(chat_wrapper, bg="#F0F0F0")
chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

chat_scrollbar = tk.Scrollbar(chat_wrapper, command=chat_frame.yview)
chat_frame.configure(yscrollcommand=chat_scrollbar.set)
chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

chat_canvas_frame = tk.Frame(chat_frame, bg="#F0F0F0")
chat_window = chat_frame.create_window((0, 0), window=chat_canvas_frame, anchor='nw')

def on_frame_configure(event):
    chat_frame.configure(scrollregion=chat_frame.bbox("all"))

chat_canvas_frame.bind("<Configure>", on_frame_configure)

def on_canvas_configure(event):
    canvas_width = event.width
    chat_frame.itemconfig(chat_window, width=canvas_width)

chat_frame.bind("<Configure>", on_canvas_configure)

bottom_frame = tk.Frame(root, bg="white")
bottom_frame.grid(row=1, column=0, sticky="ew")

entry_box = tk.Entry(bottom_frame, font=("Arial", 12))
entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5), pady=10)
entry_box.bind("<Return>", lambda event: send_message())

send_button = tk.Button(bottom_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT, padx=(5, 10), pady=10)

entry_box.focus()

# Test Messages
add_message("Hello! How can I help you?", is_user=False)
add_message("Hi! I'd like to book a train.", is_user=True)
add_message("Sure. When would you like to travel?", is_user=False)
add_message("Next Friday, please.", is_user=True)
add_message("I will check for the cheapest tickets for next Friday then!", is_user=False)

root.mainloop()