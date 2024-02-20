# This is the backend for the file sharing app
The backend uses session based authentication to authenticate users.
Import the postman collection to test the endpoints
- # Login
    - ## Client user
        - Username: client
        - Password: client
    - ## Operational user
        - Username: ops
        - Password: ops

- # Signup
    - Only client users can sign up, use the client user credentials to sign up a new user

- # File upload
    - Only client Operations users can upload files
    - The file will be uploaded to the uploads folder
    - The file will be renamed to a unique hash
    - Operations users can't list the files in the uploads folder

- # File download
    - Only client users can list and download files
    - The file will be downloaded from the uploads folder
    - Client users can't upload files
    - To download a file, copy the file hash and paste it in the download input of postman

- # Logout
    - All users can logout