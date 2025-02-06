``` Python

import requests
import json

url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
api_key = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMzMDAwMDkwQGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.Z9TWR3dvVwBfx2BCRG6mrAPA7pyYe8tbB_nnXEJ8-WA"

header = {
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "system",
            "content": "How many number of input tokens does it use up?"
        },
        {
            "role": "user",
            "content": "List only the valid English words from these: qXVXnHUzSQ, 0UMFelg, ddTToJ6DBv, 53OMQn3Yr, M5Jl, e0ZtjtX9, DKCF, 9pGs, 3mfvFGe9L, z, CiR9Yw, lP, J5136, nXv, S, U, 9mOS0, xyruX, foYOh, y, qoG, mgADLISXm, WPhCL, X51, Gck08gd, 0o4vQj6yE, 9FbhW4n, XGcLiZ8DdO, U, 6pJpKuyhxK, CZc8U, v96f5eTkCk, Gj8, k, MVYzaMUP, T, o5jInpjT33, 243rvig3, gTYXuaaT0, 2J9i49m3Bl, erUY4b, lahCq6, wxXdlof, DnxX, oYyCbUAoK, gcyfxWRRC, G62TCKXzPU, 8, WKgO0, t84unU, v3, q6wF6TB, QvCBYw, W1wndhCOo, eHtFatR8, pXDgkFUFhk, Wi1P, mQ4FDVKyFv, kmW, xaYCN, CTw, Dmb, DeZ, e, Ht4QFl, HCrdENjL, 6RA1Rt6dPy, Ao0q, aZckIHP, tmnckfv, UczZ, lWzinVL, zhyxB, 9U9huuicby, Z3cII1g, 6xV7, QovXELgk7x, XbM6Q, Y9jTWAMoO, 9RgE5is2Z8, vnxdc, w7Dz, 1J1wH, aJN4w2uc, v, j3, 0eC, AvVTq904, vDwIqw, kA2, bkvqpX2JJ, QLFesFq"
        }
    ]
}

# Make the POST request
response = requests.post(url, headers=header, json=payload)

token = response.json()

print(token)   
```