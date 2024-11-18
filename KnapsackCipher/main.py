import tkinter as tk
from tkinter import messagebox
import random
from math import gcd


def generate_keys(n):
    B = [random.randint(1, 10)]
    for _ in range(1, n):
        B.append(random.randint(sum(B) + 1, sum(B) * 2))
    m = sum(B) + random.randint(1, 10)
    t = random.randint(2, m - 1)
    while gcd(t, m) != 1:
        t = random.randint(2, m - 1)
    A = [(b * t) % m for b in B]
    return (B, m, t), A


def encrypt(public_key, binary_message):
    A = public_key
    blocks = [binary_message[i:i + len(A)] for i in range(0, len(binary_message), len(A))]
    ciphertext = []
    for block in blocks:
        block = block.ljust(len(A), '0')
        C = sum(int(bit) * a for bit, a in zip(block, A))
        ciphertext.append(C)
    return ciphertext


def decrypt(private_key, ciphertext, t_inv):
    B, m, _ = private_key
    plaintext = ''
    for C in ciphertext:
        C_prime = (C * t_inv) % m
        block = []
        for b in reversed(B):
            if C_prime >= b:
                block.append(1)
                C_prime -= b
            else:
                block.append(0)
        plaintext += ''.join(map(str, reversed(block)))

    decrypted_message = ''
    for i in range(0, len(plaintext), 8):
        byte = plaintext[i:i + 8]
        decrypted_message += chr(int(byte, 2))

    return plaintext


class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Криптосистема на основі задачі рюкзака")

        self.private_key = None
        self.public_key = None
        self.t_inv = None

        tk.Button(root, text="Згенерувати ключі", command=self.generate_keys_dialog).grid(row=1, column=0, columnspan=2)

        tk.Label(root, text="Повідомлення (бінарне):").grid(row=3, column=0)
        self.message_entry = tk.Entry(root)
        self.message_entry.grid(row=3, column=1)
        tk.Button(root, text="Зашифрувати", command=self.encrypt_message).grid(row=4, column=0, columnspan=2)

        tk.Label(root, text="Зашифроване повідомлення:").grid(row=5, column=0)
        self.ciphertext_display = tk.Text(root, height=5, width=30)
        self.ciphertext_display.grid(row=6, column=0, columnspan=2)

        tk.Button(root, text="Розшифрувати", command=self.decrypt_message).grid(row=8, column=0, columnspan=2)

        tk.Label(root, text="Секретний ключ (B, m, t):").grid(row=11, column=0)
        self.private_key_entry = tk.Entry(root)
        self.private_key_entry.grid(row=11, column=1)

        tk.Label(root, text="t^(-1):").grid(row=12, column=0)
        self.t_inv_entry = tk.Entry(root)
        self.t_inv_entry.grid(row=12, column=1)

        tk.Button(root, text="Розшифрувати за ключами", command=self.manual_decrypt).grid(row=13, column=0,
                                                                                          columnspan=2)

        tk.Label(root, text="Розшифроване повідомлення:").grid(row=9, column=0)
        self.decrypted_message_display = tk.Entry(root)
        self.decrypted_message_display.grid(row=9, column=1)

    def generate_keys_dialog(self):
        key_length = 5
        self.private_key, self.public_key = generate_keys(key_length)
        _, m, t = self.private_key
        self.t_inv = pow(t, -1, m)
        messagebox.showinfo(
            "Ключі згенеровано",
            f"Відкритий ключ: {self.public_key}\n"
            f"Секретний ключ: {self.private_key}\n"
            f"Значення t^(-1): {self.t_inv}"
        )

    def encrypt_message(self):
        if not self.public_key:
            messagebox.showerror("Помилка", "Спочатку згенеруйте ключі!")
            return
        binary_message = self.message_entry.get().strip()
        if not binary_message:
            messagebox.showerror("Помилка", "Введіть повідомлення!")
            return
        if not all(bit in '01' for bit in binary_message):  # Ensure the input is valid binary
            messagebox.showerror("Помилка", "Повідомлення має бути в форматі бінарного рядка!")
            return
        ciphertext = encrypt(self.public_key, binary_message)
        self.ciphertext_display.delete("1.0", tk.END)
        self.ciphertext_display.insert(tk.END, " ".join(map(str, ciphertext)))

    def decrypt_message(self):
        if not self.private_key or not self.t_inv:
            messagebox.showerror("Помилка", "Спочатку згенеруйте ключі!")
            return
        ciphertext = self.ciphertext_display.get("1.0", tk.END).strip()
        if not ciphertext:
            messagebox.showerror("Помилка", "Спочатку зашифруйте повідомлення!")
            return
        try:
            ciphertext = list(map(int, ciphertext.split()))
        except ValueError:
            messagebox.showerror("Помилка", "Шифротекст має бути числовим!")
            return
        decrypted_message = decrypt(self.private_key, ciphertext, self.t_inv)
        self.decrypted_message_display.delete(0, tk.END)
        self.decrypted_message_display.insert(0, decrypted_message)

    def manual_decrypt(self):
        try:
            private_key = eval(self.private_key_entry.get())
            t_inv = int(self.t_inv_entry.get())
            ciphertext = self.ciphertext_display.get("1.0", tk.END).strip()
            if not ciphertext:
                messagebox.showerror("Помилка", "Спочатку введіть шифротекст!")
                return
            ciphertext = list(map(int, ciphertext.split()))
            decrypted_message = decrypt(private_key, ciphertext, t_inv)
            self.decrypted_message_display.delete(0, tk.END)
            self.decrypted_message_display.insert(0, decrypted_message)
        except Exception as e:
            messagebox.showerror("Помилка", f"Невірний формат ключів або даних: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
