import tkinter as tk
from tkinter import messagebox
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


private_key = None
public_key = None


def generate_keys():
    global private_key, public_key
    key = RSA.generate(2048)
    private_key = key
    public_key = key.publickey()
    messagebox.showinfo("Keys Generated", "Public and Private keys generated successfully!")


def sign_message():
    global private_key
    if not private_key:
        messagebox.showerror("Error", "Generate keys first!")
        return

    message = message_entry.get("1.0", tk.END).strip()
    if not message:
        messagebox.showerror("Error", "Message cannot be empty!")
        return

    hash_message = SHA256.new(message.encode('utf-8'))
    signature = pkcs1_15.new(private_key).sign(hash_message)
    signature_text.delete("1.0", tk.END)
    signature_text.insert(tk.END, signature.hex())
    messagebox.showinfo("Success", "Message signed successfully!")


def verify_signature():
    global public_key
    if not public_key:
        messagebox.showerror("Error", "Generate keys first!")
        return

    message = message_entry.get("1.0", tk.END).strip()
    signature = signature_text.get("1.0", tk.END).strip()

    if not message or not signature:
        messagebox.showerror("Error", "Message and signature cannot be empty!")
        return

    try:
        hash_message = SHA256.new(message.encode('utf-8'))
        signature_bytes = bytes.fromhex(signature)
        pkcs1_15.new(public_key).verify(hash_message, signature_bytes)
        messagebox.showinfo("Verification", "Signature is valid!")
    except (ValueError, TypeError):
        messagebox.showerror("Verification", "Signature is invalid!")


root = tk.Tk()
root.title("RSA Digital Signature")

key_frame = tk.Frame(root)
key_frame.pack(pady=10)

generate_key_button = tk.Button(key_frame, text="Generate Keys", command=generate_keys)
generate_key_button.pack()

message_frame = tk.LabelFrame(root, text="Message", padx=10, pady=10)
message_frame.pack(pady=10, fill="both", expand="yes")

message_entry = tk.Text(message_frame, height=5)
message_entry.pack(fill="both", expand="yes")

signature_frame = tk.LabelFrame(root, text="Signature", padx=10, pady=10)
signature_frame.pack(pady=10, fill="both", expand="yes")

signature_text = tk.Text(signature_frame, height=5)
signature_text.pack(fill="both", expand="yes")

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

sign_button = tk.Button(button_frame, text="Sign Message", command=sign_message)
sign_button.pack(side="left", padx=5)

verify_button = tk.Button(button_frame, text="Verify Signature", command=verify_signature)
verify_button.pack(side="right", padx=5)

root.mainloop()
