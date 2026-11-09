from starlette.requests import Request


def get_client_ip(request: Request) -> str:
    """
    Extract the client IP address from standard proxy headers or the underlying connection.
    Prioritizes X-Forwarded-For, then X-Real-IP, and falls back to client.host.
    """
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"

