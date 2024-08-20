from channels.middleware import BaseMiddleware
from django.db import close_old_connections
from rest_framework.exceptions import AuthenticationFailed
from accounts.tokenauthentication import JWTAuthentication

class JWTWebsocketMiddleware(BaseMiddleware):
    
    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_string=scope.get("query_string",b"").decode("utf-8")
        query_parameter=dict(qp.split("=") for qp in query_string.split("&"))
        token=query_parameter.get("token")
        
        if token is None:
            await send({
                "type":"websocket.close",
                "code":4000
            })
        
        authentication=JWTAuthentication()
        try:
            user=await authentication.authenticate_websocket(scope,token)
            if user is not None:
                scope["user"]=user
                
            else:
                await send({
                "type":"websocket.close",
                "code":4001
            })
            
            return await super().__call__(scope,receive,send)
        except AuthenticationFailed:
            await send({
                "type":"websocket.close",
                "code":4002
            })
                    