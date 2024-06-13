import writer.auth
import writer.serve

_auth = writer.auth.BasicAuth(
    login='admin',
    password='admin',
    delay_after_failure=0
)

writer.serve.register_auth(_auth)
