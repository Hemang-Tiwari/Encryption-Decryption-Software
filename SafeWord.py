import random
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog, ttk
from pydub import AudioSegment
from PIL import Image
import numpy as np
import os
from cryptography.fernet import Fernet


def clearEncryptField():
    preText_field.delete(0, END)
    encryptText_field.delete(0, END)
    encryptKeyCode_field.delete(0, END)


def clearDecryptField():
    postText_field.delete(0, END)
    decryptText_field.delete(0, END)
    decryptKeyCode_field.delete(0, END)


def encryptTexttoCode():
    encryptText_field.delete(0, END)
    encryptKeyCode_field.delete(0, END)
    shiftPosition = random.randint(1, 26)
    encryptText = preText_field.get()

    unrecognizeLetterCount = 0
    for string in encryptText:
        if not string.isalpha():
            unrecognizeLetterCount += 1

    if unrecognizeLetterCount != 0:
        encryptText_field.insert(0, "Character Error!")
        encryptKeyCode_field.insert(0, "Character Error!")
    else:
        encryptList = []
        for letter in encryptText:
            if letter.isupper():
                updateNumericValue = (ord(letter) - 64) + shiftPosition
                if updateNumericValue > 26:
                    updateNumericValue %= 26
                convertValue = updateNumericValue + 64
                encryptList.append(chr(convertValue))
            elif letter.islower():
                updateNumericValue = (ord(letter) - 96) + shiftPosition
                if updateNumericValue > 26:
                    updateNumericValue %= 26
                convertValue = updateNumericValue + 96
                encryptList.append(chr(convertValue))

        encryptText = ''.join(encryptList)
        encryptText_field.insert(0, encryptText)
        encryptKeyCode_field.insert(0, str(shiftPosition))

    status_bar.config(text="Text Encryption Complete")


def decryptTexttoCode():
    decryptText_field.delete(0, END)
    decryptText = postText_field.get()
    keycodeStr = decryptKeyCode_field.get()

    if not keycodeStr.isdigit():
        decryptText_field.insert(0, "Invalid Key Code!")
        status_bar.config(text="Invalid Key Code for Decryption")
        return

    keycode = int(keycodeStr)

    unrecognizeLetterCount = 0
    for string in decryptText:
        if not string.isalpha():
            unrecognizeLetterCount += 1

    if unrecognizeLetterCount != 0:
        decryptText_field.insert(0, "Character Error!")
        status_bar.config(text="Character Error in Decryption")
    else:
        decryptList = []
        for letter in decryptText:
            if letter.isupper():
                updateNumericValue = (ord(letter) - 64) - keycode
                if updateNumericValue < 1:
                    updateNumericValue += 26
                convertValue = updateNumericValue + 64
                decryptList.append(chr(convertValue))
            elif letter.islower():
                updateNumericValue = (ord(letter) - 96) - keycode
                if updateNumericValue < 1:
                    updateNumericValue += 26
                convertValue = updateNumericValue + 96
                decryptList.append(chr(convertValue))

        decryptText = ''.join(decryptList)
        decryptText_field.insert(0, decryptText)
        status_bar.config(text="Text Decryption Complete")


def encryptFile():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    with open(file_path, 'r') as file:
        data = file.read()

    shiftPosition = random.randint(1, 26)
    encrypted_data = ''.join(
        chr((ord(char) - 32 + shiftPosition) % 95 + 32) for char in data
    )

    with open(file_path, 'w') as file:
        file.write(encrypted_data)

    messagebox.showinfo("Success", f"File encrypted with key: {shiftPosition}")
    status_bar.config(text="File Encryption Complete")


def decryptFile():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    keycodeStr = simpledialog.askstring("Input", "Enter the key code:")
    if not keycodeStr.isdigit():
        messagebox.showerror("Error", "Invalid Key Code!")
        status_bar.config(text="Invalid Key Code for File Decryption")
        return

    keycode = int(keycodeStr)

    with open(file_path, 'r') as file:
        data = file.read()

    decrypted_data = ''.join(
        chr((ord(char) - 32 - keycode) % 95 + 32) for char in data
    )

    with open(file_path, 'w') as file:
        file.write(decrypted_data)

    messagebox.showinfo("Success", "File decrypted successfully")
    status_bar.config(text="File Decryption Complete")


def xor_encrypt_decrypt(data, key):
    return bytes([b ^ key for b in data])


def encryptImageFile():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return

    keycode = random.randint(1, 255)

    with open(file_path, 'rb') as image_file:
        image_data = image_file.read()

    encrypted_data = xor_encrypt_decrypt(image_data, keycode)

    with open(file_path, 'wb') as encrypted_image_file:
        encrypted_image_file.write(encrypted_data)

    messagebox.showinfo("Success", f"Image file encrypted with key: {keycode}")
    status_bar.config(text="Image Encryption Complete")


def decryptImageFile():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return

    keycodeStr = simpledialog.askstring("Input", "Enter the key code (0-255):")
    if not keycodeStr.isdigit() or not 0 <= int(keycodeStr) <= 255:
        messagebox.showerror("Error", "Invalid Key Code! It must be an integer between 0 and 255.")
        status_bar.config(text="Invalid Key Code for Image Decryption")
        return

    keycode = int(keycodeStr)

    with open(file_path, 'rb') as encrypted_image_file:
        encrypted_data = encrypted_image_file.read()

    decrypted_data = xor_encrypt_decrypt(encrypted_data, keycode)

    with open(file_path, 'wb') as decrypted_image_file:
        decrypted_image_file.write(decrypted_data)

    messagebox.showinfo("Success", "Image file decrypted successfully")
    status_bar.config(text="Image Decryption Complete")


def encryptAudioFile():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
    if not file_path:
        return

    keycode = random.randint(1, 255)

    audio = AudioSegment.from_file(file_path)
    raw_data = audio.raw_data
    encrypted_data = xor_encrypt_decrypt(raw_data, keycode)

    encrypted_audio = audio._spawn(encrypted_data)
    encrypted_audio.export(file_path, format="wav")

    messagebox.showinfo("Success", f"Audio file encrypted with key: {keycode}")
    status_bar.config(text="Audio Encryption Complete")


def decryptAudioFile():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
    if not file_path:
        return

    keycodeStr = simpledialog.askstring("Input", "Enter the key code (0-255):")
    if not keycodeStr.isdigit() or not 0 <= int(keycodeStr) <= 255:
        messagebox.showerror("Error", "Invalid Key Code! It must be an integer between 0 and 255.")
        status_bar.config(text="Invalid Key Code for Audio Decryption")
        return

    keycode = int(keycodeStr)

    audio = AudioSegment.from_file(file_path)
    raw_data = audio.raw_data
    decrypted_data = xor_encrypt_decrypt(raw_data, keycode)

    decrypted_audio = audio._spawn(decrypted_data)
    decrypted_audio.export(file_path, format="wav")

    messagebox.showinfo("Success", "Audio file decrypted successfully")
    status_bar.config(text="Audio Decryption Complete")


# Initialize the main window
root = Tk()
root.title("SafeWord")
root.geometry("600x400")
root.configure(bg='#2E3B4E')  # Background color of the main window

# Style configurations
style = ttk.Style()
style.configure('TNotebook', background='#2E3B4E', foreground='white')
style.configure('TNotebook.Tab', background='#4B6587', foreground='black', padding=[10, 5])
style.map('TNotebook.Tab', background=[('selected', '#800000')])

style.configure('TLabel', background='#2E3B4E', foreground='white')
style.configure('TEntry', foreground='#4B6587')
style.configure('TButton', background='#4B6587', foreground='white', padding=[5, 5])
style.configure('TLabelFrame', background='#2E3B4E', foreground='white')

# Create a Notebook (Tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill='both',)

# Text Encryption/Decryption Tab
text_tab = Frame(notebook, bg='#2E3B4E')
notebook.add(text_tab, text="Text")

# Text Encryption Frame
encryptFrame = LabelFrame(text_tab, text="Text Encryption", padx=10, pady=10, bg='#2E3B4E', fg='white')
encryptFrame.pack(fill="both", expand=True, padx=10, pady=10)

preText_label = Label(encryptFrame, text="Enter Text to Encrypt:", bg='#2E3B4E', fg='white')
preText_label.grid(row=0, column=0, pady=5)
preText_field = Entry(encryptFrame, width=50, fg='#4B6587', bg='#F7F6F2')
preText_field.grid(row=0, column=1, pady=5)

encryptButton = Button(encryptFrame, text="Encrypt", command=encryptTexttoCode, bg='#4B6587', fg='white')
encryptButton.grid(row=0, column=2, padx=10)

encryptText_label = Label(encryptFrame, text="Encrypted Text:", bg='#2E3B4E', fg='white')
encryptText_label.grid(row=1, column=0, pady=5)
encryptText_field = Entry(encryptFrame, width=50, fg='#4B6587', bg='#F7F6F2')
encryptText_field.grid(row=1, column=1, pady=5)

encryptKeyCode_label = Label(encryptFrame, text="Encryption Key Code:", bg='#2E3B4E', fg='white')
encryptKeyCode_label.grid(row=2, column=0, pady=5)
encryptKeyCode_field = Entry(encryptFrame, width=50, fg='#4B6587', bg='#F7F6F2')
encryptKeyCode_field.grid(row=2, column=1, pady=5)

clearButton = Button(encryptFrame, text="Clear", command=clearEncryptField, bg='#4B6587', fg='white')
clearButton.grid(row=3, column=1, pady=10)

# Text Decryption Frame
decryptFrame = LabelFrame(text_tab, text="Text Decryption", padx=10, pady=10, bg='#2E3B4E', fg='white')
decryptFrame.pack(fill="both", expand=True, padx=10, pady=10)

postText_label = Label(decryptFrame, text="Enter Text to Decrypt:", bg='#2E3B4E', fg='white')
postText_label.grid(row=0, column=0, pady=5)
postText_field = Entry(decryptFrame, width=50, fg='#4B6587', bg='#F7F6F2')
postText_field.grid(row=0, column=1, pady=5)

decryptButton = Button(decryptFrame, text="Decrypt", command=decryptTexttoCode, bg='#4B6587', fg='white')
decryptButton.grid(row=0, column=2, padx=10)

decryptText_label = Label(decryptFrame, text="Decrypted Text:", bg='#2E3B4E', fg='white')
decryptText_label.grid(row=1, column=0, pady=5)
decryptText_field = Entry(decryptFrame, width=50, fg='#4B6587', bg='#F7F6F2')
decryptText_field.grid(row=1, column=1, pady=5)

decryptKeyCode_label = Label(decryptFrame, text="Decryption Key Code:", bg='#2E3B4E', fg='white')
decryptKeyCode_label.grid(row=2, column=0, pady=5)
decryptKeyCode_field = Entry(decryptFrame, width=50, fg='#4B6587', bg='#F7F6F2')
decryptKeyCode_field.grid(row=2, column=1, pady=5)

clearButton = Button(decryptFrame, text="Clear", command=clearDecryptField, bg='#4B6587', fg='white')
clearButton.grid(row=3, column=1, pady=10)

# File Encryption/Decryption Tab
file_tab = Frame(notebook, bg='#2E3B4E')
notebook.add(file_tab, text="File")

fileEncryptFrame = LabelFrame(file_tab, text="File Encryption/Decryption", padx=10, pady=10, bg='#2E3B4E', fg='white')
fileEncryptFrame.pack(fill="both", expand=True, padx=10, pady=10)

encryptFileButton = Button(fileEncryptFrame, text="Encrypt File", command=encryptFile, bg='#4B6587', fg='white')
encryptFileButton.pack(pady=5)

decryptFileButton = Button(fileEncryptFrame, text="Decrypt File", command=decryptFile, bg='#4B6587', fg='white')
decryptFileButton.pack(pady=5)

# Image Encryption/Decryption Tab
image_tab = Frame(notebook, bg='#2E3B4E')
notebook.add(image_tab, text="Image")

imageEncryptFrame = LabelFrame(image_tab, text="Image Encryption/Decryption", padx=10, pady=10, bg='#2E3B4E', fg='white')
imageEncryptFrame.pack(fill="both", expand=True, padx=10, pady=10)

encryptImageButton = Button(imageEncryptFrame, text="Encrypt Image", command=encryptImageFile, bg='#4B6587', fg='white')
encryptImageButton.pack(pady=5)

decryptImageButton = Button(imageEncryptFrame, text="Decrypt Image", command=decryptImageFile, bg='#4B6587', fg='white')
decryptImageButton.pack(pady=5)

# Audio Encryption/Decryption Tab
audio_tab = Frame(notebook, bg='#2E3B4E')
notebook.add(audio_tab, text="Audio")

audioEncryptFrame = LabelFrame(audio_tab, text="Audio Encryption/Decryption", padx=10, pady=10, bg='#2E3B4E', fg='white')
audioEncryptFrame.pack(fill="both", expand=True, padx=10, pady=10)

encryptAudioButton = Button(audioEncryptFrame, text="Encrypt Audio", command=encryptAudioFile, bg='#4B6587', fg='white')
encryptAudioButton.pack(pady=5)

decryptAudioButton = Button(audioEncryptFrame, text="Decrypt Audio", command=decryptAudioFile, bg='#4B6587', fg='white')
decryptAudioButton.pack(pady=5)

# Status Bar
status_bar = Label(root, text="Ready", bd=1, relief=SUNKEN, anchor=W, bg='#4B6587', fg='white')
status_bar.pack(side=BOTTOM, fill=X)

root.mainloop()
