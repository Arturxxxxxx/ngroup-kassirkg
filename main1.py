import hmac, hashlib
secret="eihal;sdienalesfieanslfesufabu23nf23fku"
ticket_no="AA004376"
print(hmac.new(secret.encode(), ticket_no.encode(), hashlib.sha256).hexdigest())