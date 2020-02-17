# aiowialon

Wialon Remote API async client

## Install

    pip install aiowialon

## Connection and Login

```python
from aiowialon import connect

token = "WIALON_REMOTE_API_ACCESS_TOKEN"

async with connect(token) as session:
    print(session.username)
```

## Environment Variables

