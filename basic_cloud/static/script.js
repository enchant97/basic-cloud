const TOKEN_KEY = "token";

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
                change_directory(path);
            });
        }
        else {
            bnt.addEventListener("click", _ => {
                load_roots();
            });
        }
    }
    else {
        elem.classList.add("file");
    }
    elem.append(bnt);
    parent.append(elem);
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

async function fetch_root_dirs() {
    const resp = await fetch("/api/directory/roots",
        {
            method: "GET",
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

async function load_roots() {
    const roots = await fetch_root_dirs();
    const folders_elem = document.getElementById("folders");
    delete_children(document.getElementById("files"));
    delete_children(folders_elem);
    append_path_row(folders_elem, roots.shared, roots.shared, true);
    append_path_row(folders_elem, roots.home, roots.home, true);
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
        combined_path = new_directory + "/" + path_content.name;
        if (path_content.meta.is_directory) {
            append_path_row(folders_elem, combined_path, path_content.name, true);
        }
        else {
            append_path_row(files_elem, combined_path, path_content.name, false);
        }
    });
}
