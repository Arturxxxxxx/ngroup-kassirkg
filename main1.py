import hmac, hashlib
secret="+996220186813"
ticket_no="Fs6j4hnW39Tde5mEs9uXhynEpVBTr"
print(hmac.new(secret.encode(), ticket_no.encode(), hashlib.sha256).hexdigest())