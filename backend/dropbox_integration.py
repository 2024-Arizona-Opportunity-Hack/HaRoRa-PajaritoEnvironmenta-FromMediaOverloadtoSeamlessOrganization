import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from urllib.parse import urlencode

app = FastAPI(root_path='/api')
app.add_middleware(SessionMiddleware, secret_key=os.environ['FASTAPI_SESSION_SECRET_KEY'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http:localhost:8080', 'https://www.dropbox.com', 'http://localhost'],
    allow_methods=("GET", "POST", "OPTIONS"),
    allow_headers=('Content-Type', 'Authorization')
)

AUTH_URI = "https://www.dropbox.com/oauth2/authorize"
TOKEN_URI = "https://api.dropboxapi.com/oauth2/token"
CLIENT_URL = 'http://localhost:5173'

@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth_dropbox_callback')
    auth_params = {
        "client_id": os.environ['DROPBOX_CLIENT_ID'],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "token_access_type": "offline"
    }
    auth_url = f"{AUTH_URI}?{urlencode(auth_params)}"
    return {'auth_url': auth_url}
# https://www.dropbox.com/oauth2/authorize?client_id=9g3q8zck6ksa87a&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fapi%2Fauth%2Fdropbox%2Fcallback&response_type=code&token_access_type=offline

@app.get('/auth/dropbox/callback')
async def auth_dropbox_callback(request: Request):
    auth_code = request.query_params['code']
    redirect_uri = request.url_for('auth_dropbox_callback')
    try:
        token_data = {
            "code": auth_code,
            "grant_type": "authorization_code",
            "client_id": os.environ['DROPBOX_CLIENT_ID'],
            "client_secret": os.environ['DROPBOX_CLIENT_SECRET'],
            "redirect_uri": redirect_uri
        }
        token_response = requests.post(TOKEN_URI, data=token_data)
        token_response_data = token_response.json()
        
        access_token = token_response_data['access_token']
        refresh_token = token_response_data.get('refresh_token')
        
        # Fetch user information
        user_info_response = requests.post(
            'https://api.dropboxapi.com/2/users/get_current_account',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_info = user_info_response.json()
        print(user_info)
        
        request.session['user'] = {
            'name': user_info['name']['display_name'],
            'email': user_info['email'],
            'account_id': user_info['account_id']
        }
    except Exception as error:
        return HTMLResponse(f'<h1>{error}</h1>')
    
    response_url = f'{request.url.scheme}://{request.url.netloc}'
    return RedirectResponse(response_url)

@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/', status_code=302)

@app.get('/')
async def home(request: Request):
    user = request.session.get('user')
    if user:
        return HTMLResponse(f'<h1>Welcome, {user["name"]}!</h1>')
    return HTMLResponse('<h1>Please login to access this page</h1>')

@app.get('/protected')
async def protected(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return HTMLResponse(f'<h1>Protected page</h1><p>Welcome, {user["name"]}!</p>')

@app.get('/profile')
async def profile(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return {'name': user['name'], 'email': user['email'], 'account_id': user['account_id']}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('dropbox_integration:app', host='localhost', port=8080, reload=True)