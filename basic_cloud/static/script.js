const TOKEN_KEY = "token";

/**
 * gets the stored token from localStorage
 * and then sessionStorage if none is found
 * @returns the token, or null
 */
function get_stored_token() {
    var token = localStorage.getItem(TOKEN_KEY);
    if (token === null){
        return sessionStorage.getItem(TOKEN_KEY);
    }
    return token;
}

function get_auth_headers(content_type = "application/json") {
    return {
        "Authorization": `Bearer ${get_stored_token()}`,
        "Content-Type": content_type,
    }
}

async function fetch_token(username, password) {
    const resp = await fetch("/token",
        {
            method: "POST",
            body: `grant_type=password&username=${username}&password=${password}`,
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });
    // TODO add error handling
    const token = await resp.json();
    return token.access_token;
}

async function fetch_dir_content(directory) {
    const resp = await fetch("/api/directory/contents",
        {
            method: "POST",
            body: JSON.stringify({directory: directory}),
            headers: get_auth_headers(),
        }
    );
    // TODO add error handling
    return await resp.json();
}

async function do_login() {
    const username = prompt("enter username");
    const password = prompt("enter password");
    token = await fetch_token(username, password);
    localStorage.removeItem(TOKEN_KEY);
    sessionStorage.setItem(TOKEN_KEY, token);
}
