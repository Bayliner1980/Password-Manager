Simple password manager that stores the website, username and password in an encrypted file. 

With the manager you can Add and Query passwords stored in the file. The program uses pandas to store the data, as well as, read and write. The cryptography library is used for all encrypting and decrypting.

To use the program, clone the repository and install the required libraries using, pip install -r requirements.txt. Then run with python main.py [Master Password]. You can specify the location of the file storing the password data using the -f/--file flag, the default location is the directory the program is stored in.

