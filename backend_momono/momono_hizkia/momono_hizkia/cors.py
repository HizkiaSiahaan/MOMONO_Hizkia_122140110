def cors_tween_factory(handler, registry):
    def cors_tween(request):
        # Jika request OPTIONS (preflight), beri response langsung
        if request.method == 'OPTIONS':
            response = request.response
            response.status_code = 200
        else:
            response = handler(request)
        
        # Tambahkan header CORS
        response.headers.update({
            'Access-Control-Allow-Origin': 'http://localhost:3000',  # sesuaikan frontend Anda
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Credentials': 'true',
        })
        return response
    return cors_tween
