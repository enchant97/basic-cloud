"use strict";

const TOKEN_KEY = "token";

/**
 * redirect to the login page
 */
function navigate_to_login() {
    window.location.href = "/login";
}

/**
 * delete a parents children
 * @param {Element} elem - the parent element
 */
function delete_children(parent) {
    while (parent.hasChildNodes()) {
        parent.removeChild(parent.lastChild);
    }
}

/**
 * appends new path navigators to the parent
 * @param {Element} parent - the parent element
 * @param {string} path - the path
 * @param {string} name - the name to display
 * @param {boolean} is_dir - whether path is a directory
 */
function append_path_row(parent, path, name, is_dir) {
    const elem = document.createElement("li");
    const bnt = document.createElement("button");
    bnt.innerText = name;
    if (is_dir) {
        elem.classList.add("directory");
        if (path !== null) {
            bnt.addEventListener("click", _ => {
                document.getElementById("load-shares-bnt").removeAttribute("disabled");
                change_directory(path);
            });
        }
        else {
            bnt.addEventListener("click", _ => {
                document.getElementById("load-shares-bnt").setAttribute("disabled", true);
                load_roots();
            });
        }
    }
    else {
        bnt.addEventListener("click", _ => { start_download_file(path) });
        elem.classList.add("file");
    }
    elem.append(bnt);
    parent.append(elem);
}

function go_to_shares() {
    document.getElementById("load-shares-bnt").setAttribute("disabled", true);
    load_roots();
}

/**
 * gets the parent directory of a path,
 * or returns null if there is none
 * @param {string} curr_dir - the current index
 */
function get_parent_dir(curr_dir) {
    const last_i = curr_dir.lastIndexOf("/");
    if (last_i === -1) {
        return null;
    }
    return curr_dir.substring(0, last_i);
}

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

/**
 * remove any stored token in
 * either session or local storage
 */
function remove_token() {
    localStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
}

/**
 * adds a auth header with the token
 * @param {string} content_type - the content type
 * @returns html header for use with fetch
 */
function get_auth_headers(content_type = "application/json") {
    return {
        "Authorization": `Bearer ${get_stored_token()}`,
        "Content-Type": content_type,
    }
}

/**
 * updates the current directory element
 */
function update_curr_dir_status(new_location) {
    document.getElementById("curr-directory").innerText = "Location: /" + new_location;
}

/**
 * fetches a new token with given credentials
 * @param {string} username
 * @param {string} password
 * @returns the token
 */
async function fetch_token(username, password) {
    const resp = await fetch("/token",
        {
            method: "POST",
            body: `grant_type=password&username=${username}&password=${password}`,
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });
    if (resp.status === 401) {
        throw new InvalidLoginError("invalid login details");
    }
    const token = await resp.json();
    return token.access_token;
}

/**
 * get the files and directories
 * @param {string} directory - the directory to load
 * @returns the files and directories
 */
async function fetch_dir_content(directory) {
    const resp = await fetch("/api/directory/contents",
        {
            method: "POST",
            body: JSON.stringify({directory: directory}),
            headers: get_auth_headers(),
        }
    );
    if (resp.status === 401) { navigate_to_login(); }
    return await resp.json();
}

/**
 * get the root directories
 * @returns the root directories
 */
async function fetch_root_dirs() {
    const resp = await fetch("/api/directory/roots",
        {
            method: "GET",
            headers: get_auth_headers(),
        }
    );
    if (resp.status === 401) { navigate_to_login(); }
    return await resp.json();
}

/**
 * request a download token
 * @param {string} file_path - path of file to download
 * @returns download token
 */
async function fetch_download_token(file_path) {
    const resp = await fetch("/api/file/download/new-token",
    {
        method: "POST",
        body: JSON.stringify({ file_path: file_path}),
        headers: get_auth_headers(),
    });
    if (resp.status === 401) { navigate_to_login(); }
    if (!resp.ok) { throw new Error(resp.status) }
    const json_data = await resp.json();
    return json_data.token;
}

/**
 * start downloading a file
 * @param {string} file_path - path of file to download
 */
function start_download_file(file_path) {
    fetch_download_token(file_path).then(token => {
        const a_elem = document.createElement("a");
        a_elem.href = "/api/file/download/by-token/" + token;
        a_elem.setAttribute("download", true);
        a_elem.click();
        a_elem.remove();
    });
}

/**
 * handle the login for the api,
 * requesting and storing the token
 * @param {string} username - the user username
 * @param {string} password - the user password
 * @param {boolean} rememberme - whether to store the token
 */
async function do_login(username, password, rememberme) {
    // get a token
    const token = await fetch_token(username, password);
    // remove tokens from browser storage
    remove_token();
    // store the tokens
    if (rememberme) {
        localStorage.setItem(TOKEN_KEY, token);
    }
    else{
        sessionStorage.setItem(TOKEN_KEY, token);
    }
}

/**
 * log the user out and redirect to login page
 */
function do_logout() {
    remove_token();
    navigate_to_login();
}

/**
 * load and display the root directories
 */
async function load_roots() {
    const roots = await fetch_root_dirs();
    const folders_elem = document.getElementById("folders");
    delete_children(document.getElementById("files"));
    delete_children(folders_elem);
    append_path_row(folders_elem, roots.shared, roots.shared, true);
    append_path_row(folders_elem, roots.home, roots.home, true);
    update_curr_dir_status("");
}

/**
 * change the page to show a new directory
 * @param {string} new_directory - the new directory to navigate to
 */
async function change_directory(new_directory) {
    const dir_content = await fetch_dir_content(new_directory);

    const folders_elem = document.getElementById("folders");
    const files_elem = document.getElementById("files");

    delete_children(folders_elem);
    delete_children(files_elem);

    append_path_row(folders_elem, get_parent_dir(new_directory), "..", true);

    dir_content.forEach(path_content => {
        const path_name = path_content.name;
        const combined_path = new_directory + "/" + path_name;
        if (path_content.meta.is_directory) {
            append_path_row(folders_elem, combined_path, path_name, true);
        }
        else {
            append_path_row(files_elem, combined_path, path_name, false);
        }
    });
    update_curr_dir_status(new_directory.replace("\\", "/"));
}

/**
 * handle the login form being submitted
 */
function handle_login_form() {
    const username = document.getElementById("username");
    const password = document.getElementById("password");
    const rememberme = document.getElementById("rememberme");

    do_login(username.value, password.value, rememberme.checked)
        .then(_ => {
            window.location.href = "/";
        }).catch(err => {
            if (err instanceof InvalidLoginError) {
                password.value = "";
                alert(err.message);
                password.focus();
            }
            else { throw err;}
        });
}
