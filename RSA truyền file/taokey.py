import rsa
pub, priv = rsa.newkeys(2048)
with open("public.pem", "wb") as f:
    f.write(pub.save_pkcs1())
with open("private.pem", "wb") as f:
    f.write(priv.save_pkcs1())
print("Đã tạo file public.pem và private.pem")
