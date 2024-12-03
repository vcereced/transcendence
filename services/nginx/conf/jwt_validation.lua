-- -- /etc/nginx/lua/jwt_validation.lua

local jwt = require "resty.jwt"
local validators = require "resty.jwt-validators"

-- Debugging cat [container]:/var/log/nginx/error.log
local cookies = ngx.var.http_cookie
ngx.log(ngx.DEBUG, "Cookies: ", cookies or "No cookies")

-- get cookies
local cookies = ngx.var.http_cookie

if not cookies then
    ngx.status = ngx.HTTP_UNAUTHORIZED
    ngx.log(ngx.ERR, "Missing cookies for check jwt_token")
    return ngx.exit(ngx.HTTP_UNAUTHORIZED)
end

-- Función para extraer el valor de una cookie específica
local function get_cookie_value(cookie_name, cookies)
    for cookie in string.gmatch(cookies, "[^;]+") do
        local name, value = cookie:match("^%s*(.-)%s*=%s*(.-)%s*$")
        if name == cookie_name then
            return value
        end
    end
    return nil
end

-- Extraer el token de la cookie "jwt_token"
local jwt_token = get_cookie_value("accessToken", cookies)

if not jwt_token then
    ngx.status = ngx.HTTP_UNAUTHORIZED
    ngx.log(ngx.ERR, "Missing token in cookies")
    return ngx.exit(ngx.HTTP_UNAUTHORIZED)
end

-- Clave secreta para verificar el JWT
local jwt_secret_key = os.getenv("JWT_SECRET")

-- Validar y decodificar el token JWT
local jwt_obj = jwt:verify(jwt_secret_key, jwt_token, {
    exp = validators.is_not_expired(),
})

if not jwt_obj["verified"] then
    ngx.status = ngx.HTTP_UNAUTHORIZED
    ngx.log(ngx.ERR, "Invalid token")
    return ngx.exit(ngx.HTTP_UNAUTHORIZED)
end


