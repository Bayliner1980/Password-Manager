import pandas as pd
import os, random, argparse, shlex, base64
from string import digits, ascii_letters, punctuation
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from io import StringIO

def derive_key(password:str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"static_salt",
        iterations=390000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data:bytes, key:bytes):
    return Fernet(key).encrypt(data)

def decrypt_data(data:bytes, key:bytes):
    return Fernet(key).decrypt(data)

def Load_Or_Create_Csv(file_path:str, key:bytes):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=['id', 'website', 'username', 'password'])
    
    with open(file_path, "rb") as f:
        encyrpted = f.read()

    decrypted = decrypt_data(encyrpted, key)
    return pd.read_csv(StringIO(decrypted.decode()))

def Generate_Password(length=16):
    character_list = digits + ascii_letters + punctuation
    return "".join(random.choices(character_list, k=length))

def Add_Password(df: pd.DataFrame, website:str, username: str, password:str | None = None):
    password = Generate_Password() if not password else password
    df.loc[len(df)] = [len(df), website, username, password]

def Query_Password(df, website:str | None = None, username: str | None = None, password: str | None = None):
    mask = pd.Series(True, index=df.index)

    if website:
        mask &= df["website"].str.contains(website, case=False, na=False)

    if username:
        mask &= df["username"].str.contains(username, case=False, na=False)

    if password:
        mask &= df["password"].str.contains(password, case=False, na=False)

    result = df[mask]

    if result.empty:
        print("No matching entries.")
    else:
        print(result)

def Save_Df(df:pd.DataFrame, file_path:str, key:bytes):
    data = df.to_csv(index=False).encode()
    encrypted = encrypt_data(data, key)

    with open(file_path, "wb") as f:
        f.write(encrypted)

if __name__ == "__main__":
    startup_parser = argparse.ArgumentParser(description="A simple password manager that stores passwords in an encrypted csv file.")
    
    startup_parser.add_argument(
        'Master Password',
        help="Password used to decrupt password file."
    )

    startup_parser.add_argument(
        '-f', '--file', nargs="?", default="passwords",
        help="Path to password file."
    )  

    startup_args = startup_parser.parse_args()
    master_password = vars(startup_args)["Master Password"]
    file_path = startup_args.file

    key = derive_key(master_password)

    try:
        df = Load_Or_Create_Csv(file_path, key)
    except:
        print("Incorrect master password given.")
        quit()

    command_parser = argparse.ArgumentParser(prog="", add_help=False)
    subparsers = command_parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("Add")
    add_parser.add_argument('-u', '--username', required=True)
    add_parser.add_argument('-w', '--website', required=True)

    get_parser = subparsers.add_parser("Query")
    get_parser.add_argument('-w', '--website')       
    get_parser.add_argument('-u', '--username')
    get_parser.add_argument('-p', '--password')

    subparsers.add_parser("Exit")

    while True:
        try:
            raw = input("> ")
            args = command_parser.parse_args(shlex.split(raw))

            command = args.command.lower()

            match args.command:
                case "Add":
                    new_password = Generate_Password()
                    Add_Password(df, args.website, args.username, new_password)
                    Save_Df(df, file_path, key)
                    print("Added:", new_password)
                
                case "Query":
                    Query_Password(df, args.website, args.username, args.password)

                case "Exit":
                    Save_Df(df, file_path, key)
                    break

                case _:
                    print("Unknown command")
    
        except SystemExit:
            pass
        except (KeyboardInterrupt, EOFError):
            Save_Df(df, file_path, key)
            break
