import tkinter as tk
from datetime import datetime
import os
import threading
from llama_cpp import Llama
from dotenv import load_dotenv
import nlp

load_dotenv()
llm = Llama(model_path=os.getenv("LLAMA_PATH"), verbose=False)

# Global variables
messages = [""]
info = {
    "departure_station": None,
    "arrival_station": None,
    "departure_time": None,
    "departure_date": None,
}
current_stage = "ask_info"
chat_canvas_frame = None
chat_frame = None

# --- Chat Functionality ---
def append_message(role, message):
    messages.append({"role": role, "content": message})

def add_message(text, is_user):
    time_sent = datetime.now().strftime('%H:%M')
    msg_container = tk.Frame(chat_canvas_frame, bg="#F0F0F0")
    msg_container.pack(fill='x', pady=2, padx=10, anchor='e' if is_user else 'w')

    msg_bg = "#a0d8ef" if is_user else "#e0e0e0"
    justify = "right" if is_user else "left"

    msg = tk.Label(
        msg_container,
        text=text,
        padx=10,
        pady=7,
        bg=msg_bg,
        fg="black",
        wraplength=340,
        justify=justify,
        anchor='w',
        font=("Arial", 11)
    )
    msg.pack(side='right' if is_user else 'left', anchor='e' if is_user else 'w')

    timestamp = tk.Label(
        msg_container,
        text=time_sent,
        bg="#F0F0F0",
        fg="#818181",
        font=("Arial", 8),
        padx=5
    )
    timestamp.pack(anchor='e' if is_user else 'w')

    chat_frame.update_idletasks()
    chat_frame.yview_moveto(1.0)

def llm_generate_question_async():
    typing_label = tk.Label(chat_canvas_frame, text="Pisces is typing...", fg="gray", font=("Arial", 10, "italic"), bg="#F0F0F0")
    typing_label.pack(anchor='w', padx=10, pady=2)
    chat_frame.update_idletasks()

    def generate():
        chat_question = llm.create_chat_completion(messages)
        llm_response = chat_question["choices"][0]["message"]["content"]
        append_message("assistant", llm_response)
        typing_label.destroy()
        add_message(llm_response, is_user=False)

    threading.Thread(target=generate).start()

# --- Prompt Builders ---
def generic_prompt_builder(keys):
    return {
        "role": "system",
        "content": (
            "You are a railway assistant helping a user book a ticket. "
            "Please ask for only the following missing info:\n" +
            "\n".join(f"- {key}" for key in keys if info[key] is None)
        )
    }

def specific_prompt_builder(goal):
    return {
        "role": "system",
        "content": f"Ask the user only for: {goal}"
    }

def incorrect_station_prompt_builder(close_stations):
    suggestion = ", ".join(close_stations[1])
    return {
        "role": "system",
        "content": f"The station '{close_stations[0]}' was not recognized. Try: {suggestion}."
    }

# --- NLP Integration ---
def fill_station_info_gui(user_input):
    departure, arrival, similar_stations = nlp.get_station_data(user_input)

    if not departure and not arrival:
        messages[0] = incorrect_station_prompt_builder((user_input, similar_stations))
        llm_generate_question_async()
        return False

    if departure:
        info["departure_station"] = departure
    if arrival:
        info["arrival_station"] = arrival

    if similar_stations != [None]:
        if not info.get("departure_station"):
            messages[0] = incorrect_station_prompt_builder(similar_stations[0])
            llm_generate_question_async()
            return False
        if not info.get("arrival_station"):
            messages[0] = incorrect_station_prompt_builder(similar_stations[0])
            llm_generate_question_async()
            return False

    return True

def fill_time_info_gui(user_input):
    outbound = nlp.extract_date_and_time(user_input)
    outbound_date, outbound_time = outbound["DATE"], outbound["TIME"]

    if not outbound_date or not outbound_time:
        if not outbound_date and not outbound_time:
            messages[0] = specific_prompt_builder("departure date and time")
        elif not outbound_date:
            messages[0] = specific_prompt_builder("departure date")
        elif not outbound_time:
            messages[0] = specific_prompt_builder("departure time")
        llm_generate_question_async()
        return False

    info["departure_date"] = outbound_date
    info["departure_time"] = outbound_time
    return True

# --- Chat Controller ---
def send_message():
    global current_stage
    user_input = entry_box.get().strip()
    if user_input == "":
        return

    add_message(user_input, is_user=True)
    entry_box.delete(0, tk.END)
    append_message("user", user_input)

    if current_stage == "ask_info":
        if fill_station_info_gui(user_input):
            if info["departure_station"] and info["arrival_station"]:
                current_stage = "ask_time"
                messages[0] = specific_prompt_builder("departure date and time")
                llm_generate_question_async()
        return

    if current_stage == "ask_time":
        if fill_time_info_gui(user_input):
            add_message("Thank you! I now have all the details I need to plan your trip.", is_user=False)
            current_stage = "done"
        return

# --- GUI Main ---
def gui_main():
    global root, chat_frame, chat_canvas_frame, entry_box

    root = tk.Tk()
    root.title("Pisces: Train Chatbot")
    root.geometry("420x580")
    root.configure(bg="#F0F0F0")

    # Chat display
    container = tk.Frame(root, bg="#F0F0F0")
    container.pack(fill=tk.BOTH, expand=True)

    chat_frame = tk.Canvas(container, bg="#F0F0F0", highlightthickness=0)
    chat_scrollbar = tk.Scrollbar(container, command=chat_frame.yview)
    chat_frame.configure(yscrollcommand=chat_scrollbar.set)

    chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    chat_canvas_frame = tk.Frame(chat_frame, bg="#F0F0F0")
    chat_frame.create_window((0, 0), window=chat_canvas_frame, anchor='nw')

    def on_configure(event):
        chat_frame.configure(scrollregion=chat_frame.bbox("all"))
        chat_frame.yview_moveto(1.0)

    chat_canvas_frame.bind("<Configure>", on_configure)

    # Bottom input
    bottom_frame = tk.Frame(root, bg="white", padx=10, pady=10)
    bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

    entry_box = tk.Entry(bottom_frame, font=("Arial", 12))
    entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    entry_box.bind("<Return>", lambda event: send_message())

    send_button = tk.Button(bottom_frame, text="Send", command=send_message, font=("Arial", 10))
    send_button.pack(side=tk.RIGHT)

    # Start conversation
    messages[0] = generic_prompt_builder(info.keys())
    llm_generate_question_async()

    root.mainloop()

if __name__ == "__main__":
    gui_main()
