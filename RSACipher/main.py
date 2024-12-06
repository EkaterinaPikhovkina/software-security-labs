import tkinter as tk
from tkinter import messagebox
from math import gcd


class RSAInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("RSA Cryptographic System")

        # Key generation section
        self.key_frame = tk.Frame(self.root)
        self.key_frame.pack(pady=10)

        tk.Label(self.key_frame, text="Prime p:").grid(row=0, column=0)
        self.p_entry = tk.Entry(self.key_frame)
        self.p_entry.grid(row=0, column=1)

        tk.Label(self.key_frame, text="Prime q:").grid(row=1, column=0)
        self.q_entry = tk.Entry(self.key_frame)
        self.q_entry.grid(row=1, column=1)

        self.generate_key_btn = tk.Button(self.key_frame, text="Generate Keys", command=self.generate_keys)
        self.generate_key_btn.grid(row=2, columnspan=2, pady=10)

        # Display keys
        self.public_key_label = tk.Label(self.root, text="Public Key: ")
        self.public_key_label.pack()

        self.private_key_label = tk.Label(self.root, text="Private Key: ")
        self.private_key_label.pack()

        # Encryption section
        self.encrypt_frame = tk.Frame(self.root)
        self.encrypt_frame.pack(pady=10)

        tk.Label(self.encrypt_frame, text="Plaintext:").grid(row=0, column=0)
        self.plaintext_entry = tk.Entry(self.encrypt_frame, width=30)
        self.plaintext_entry.grid(row=0, column=1)

        self.encrypt_btn = tk.Button(self.encrypt_frame, text="Encrypt", command=self.encrypt)
        self.encrypt_btn.grid(row=1, columnspan=2, pady=10)

        self.ciphertext_label = tk.Label(self.root, text="Ciphertext: ")
        self.ciphertext_label.pack()

        # Decryption section
        self.decrypt_frame = tk.Frame(self.root)
        self.decrypt_frame.pack(pady=10)

        tk.Label(self.decrypt_frame, text="Ciphertext:").grid(row=0, column=0)
        self.ciphertext_entry = tk.Entry(self.decrypt_frame, width=30)
        self.ciphertext_entry.grid(row=0, column=1)

        self.decrypt_btn = tk.Button(self.decrypt_frame, text="Decrypt", command=self.decrypt)
        self.decrypt_btn.grid(row=1, columnspan=2, pady=10)

        self.decrypted_text_label = tk.Label(self.root, text="Decrypted Text: ")
        self.decrypted_text_label.pack()

    def generate_keys(self):
        try:
            p = int(self.p_entry.get())
            q = int(self.q_entry.get())

            if not (self.is_prime(p) and self.is_prime(q) and p != q):
                raise ValueError("p and q must be distinct prime numbers.")

            n = p * q
            phi = (p - 1) * (q - 1)

            e = 3
            while gcd(e, phi) != 1:
                e += 2

            d = self.modinv(e, phi)

            self.public_key = (e, n)
            self.private_key = (d, n)

            self.public_key_label.config(text=f"Public Key: {self.public_key}")
            self.private_key_label.config(text=f"Private Key: {self.private_key}")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))

    def encrypt(self):
        try:
            plaintext = self.plaintext_entry.get()
            e, n = self.public_key
            ciphertext = [pow(ord(char), e, n) for char in plaintext]
            self.ciphertext_label.config(text=f"Ciphertext: {ciphertext}")
        except Exception as ex:
            messagebox.showerror("Error", "Key not generated or invalid input.")

    def decrypt(self):
        try:
            ciphertext = eval(self.ciphertext_entry.get())
            d, n = self.private_key
            decrypted_text = ''.join([chr(pow(char, d, n)) for char in ciphertext])
            self.decrypted_text_label.config(text=f"Decrypted Text: {decrypted_text}")
        except Exception as ex:
            messagebox.showerror("Error", "Invalid ciphertext or key not generated.")

    @staticmethod
    def is_prime(num):
        if num < 2:
            return False
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                return False
        return True

    @staticmethod
    def modinv(a, m):
        m0, x0, x1 = m, 0, 1
        while a > 1:
            q = a // m
            m, a = a % m, m
            x0, x1 = x1 - q * x0, x0
        return x1 + m0 if x1 < 0 else x1


if __name__ == "__main__":
    root = tk.Tk()
    app = RSAInterface(root)
    root.mainloop()