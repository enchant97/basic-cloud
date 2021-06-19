"use strict";

const TOKEN_KEY = "token";
var curr_dir;

/**
 * add a spinning loader to the parent
 * of the target element and hides the target
 * @param {Element} target_element - the element that is being loaded
 * @returns the loading element
 */
function add_spin_loader(target_element) {
    const loading_element = document.createElement("div");
    const spinning_element = document.createElement("div");
    const label_element = document.createElement("strong");

    loading_element.classList.add("loading");
    spinning_element.classList.add("spin-load");
    label_element.innerText = "Loading";

    loading_element.append(spinning_element);
    loading_element.append(label_element);
    target_element.parentElement.append(loading_element);

    target_element.style.display = "none";
    return loading_element;
}

/**
 * removes the loading status and
 * unhides the target element
 * @param {Element} target_element - the element that has finished loaded
 * @param {Element} loading_element - the element showing loading
 */
function remove_spin_loader(target_element, loading_element) {
    target_element.style = null;
    loading_element.remove();
}

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
 * trigger a download of file
 * @param {string} href - the href to download from
 * @param {string} filename - the filename of the download
 */
function download(href, filename) {
    const a_elem = document.createElement("a");
    a_elem.href = href;
    a_elem.setAttribute("download", filename);
    a_elem.click();
    a_elem.remove();
}
/**
 * create file and directory row elements
 * and control their function
 */
class FileDirRow {
    constructor(path, name) {
        this.name = name;
        this.path = path;

        this.create_elements();
        this.set_names();
    }
    create_elements() {
        this.icon_elem = document.createElement("img");
        this.name_elem = document.createElement("button");
        this.delete_bnt_elem = document.createElement("button");
        this.download_bnt_elem = document.createElement("button");
    }
    set_names() {
        this.name_elem.innerText = this.name;
        this.delete_bnt_elem.innerText = "×";
        this.download_bnt_elem.innerText = "Download";
    }
    disable_edit() {
        this.delete_bnt_elem.setAttribute("disabled", true);
    }
    disable_download() {
        this.download_bnt_elem.setAttribute("disabled", true);
    }
    add_dir_root_navigate() {
        this.name_elem.addEventListener("click", _ => {
            document.getElementById("load-shares-bnt").setAttribute("disabled", true);
            load_roots();
        });
    }
    add_dir_dir_navigate() {
        this.name_elem.addEventListener("click", _ => {
            document.getElementById("load-shares-bnt").removeAttribute("disabled");
            change_directory(this.path);
        });
    }
    add_dir_navigate() {
        if (this.path !== null) {
            this.add_dir_dir_navigate();
        }
        else {
            this.add_dir_root_navigate();
        }
    }
    add_dir_zip_download() {
        this.download_bnt_elem.addEventListener("click", _ => { start_download_zip(this.path) });
    }
    make_file_row(edit_allowed = true) {
        if (!edit_allowed) { this.disable_edit(); }
        else {
            this.delete_bnt_elem.addEventListener("click", _ => { fetch_rmfile(this.path) });
        }
        this.download_bnt_elem.addEventListener("click", _ => { start_download_file(this.path) });
    }
    make_dir_row_rm() {
        this.delete_bnt_elem.addEventListener("click", _ => { fetch_rmdir(this.path) });
    }
    make_up_dir_row() {
        this.disable_edit();
        this.disable_download();
        this.add_dir_navigate();

    }
    make_dir_row(edit_allowed = true) {
        if (!edit_allowed) { this.disable_edit(); }
        else { this.make_dir_row_rm(); }
        this.add_dir_zip_download();
        this.add_dir_navigate();
    }
    make_dir_root_row() {
        this.disable_edit();
        this.add_dir_zip_download();
        this.add_dir_dir_navigate();
    }
    append_elements(parent) {
        parent.append(this.icon_elem);
        parent.append(this.name_elem);
        parent.append(this.delete_bnt_elem);
        parent.append(this.download_bnt_elem);
    }
}

/**
 * append file row elements
 * @param {Element} parent - the parent to append to
 * @param {string} path - the file path
 * @param {string} name - the name to display
 */
function append_file_row_element(parent, path, name) {
    const fdr = new FileDirRow(path, name);
    fdr.make_file_row();
    fdr.append_elements(parent);
}

/**
 * append directory row elements
 * @param {Element} parent - the parent to append to
 * @param {string} path - the directory path
 * @param {string} name - the name to display
 */
function append_directory_row_element(parent, path, name) {
    const fdr = new FileDirRow(path, name);
    fdr.make_dir_row();
    fdr.append_elements(parent);
}

/**
 * append directory up row elements
 * @param {Element} parent - the parent to append to
 * @param {string} path - the directory path
 * @param {string} name - the name to display
 */
function append_directory_up_row_element(parent, path, name) {
    const fdr = new FileDirRow(path, name);
    fdr.make_up_dir_row();
    fdr.append_elements(parent);
}

/**
 * append root directory row elements
 * @param {Element} parent - the parent to append to
 * @param {string} path - the directory path
 * @param {string} name - the name to display
 */
function append_directory_root_row_element(parent, path, name) {
    const fdr = new FileDirRow(path, name);
    fdr.make_dir_root_row();
    fdr.append_elements(parent);
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
    if (token === null) {
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
    const headers = {
        "Authorization": `Bearer ${get_stored_token()}`,
        "Content-Type": content_type,
    };
    if (content_type === null) { delete headers["Content-Type"]; }
    return headers;
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

async function fetch_create_account(username, password) {
    const resp = await fetch("/api/user",
        {
            method: "POST",
            body: JSON.stringify({ username, password }),
        });
    if (!resp.ok) { throw new Error(resp.status) }
    return await resp.json();
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
            body: JSON.stringify({ directory: directory }),
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
 * remove a file
 * @param {string} file_path - file path
 */
async function fetch_rmfile(file_path) {
    const resp = await fetch("/api/file/rm",
        {
            method: "DELETE",
            body: JSON.stringify({ file_path }),
            headers: get_auth_headers(),
        });
    if (resp.status === 401) { navigate_to_login(); }
    if (!resp.ok) { throw new Error(resp.status) }
    return await resp.text();
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
            body: JSON.stringify({ file_path: file_path }),
            headers: get_auth_headers(),
        });
    if (resp.status === 401) { navigate_to_login(); }
    if (!resp.ok) { throw new Error(resp.status) }
    const json_data = await resp.json();
    return json_data.token;
}

/**
 * upload a file
 * @param {FormData} form_data - the file and directory to upload to
 * @returns
 */
async function fetch_upload_file(form_data) {
    const resp = await fetch("/api/file/upload/overwrite",
        {
            method: "POST",
            body: form_data,
            headers: get_auth_headers(null),
        });
    if (resp.status === 401) { navigate_to_login(); }
    if (!resp.ok) { throw new Error(resp.status) }
    const json_data = await resp.json();
    return json_data;
}

/**
 * create a new directory
 * @param {string} directory - directory path
 * @param {string} name - the name of the directory to create
 * @returns the directory path created
 */
async function fetch_mkdir(directory, name) {
    const resp = await fetch("/api/directory/mkdir",
        {
            method: "POST",
            body: JSON.stringify({ directory, name }),
            headers: get_auth_headers(),
        });
    if (resp.status === 401) { navigate_to_login(); }
    if (!resp.ok) { throw new Error(resp.status) }
    return await resp.text();
}
/**
 * remove a directory
 * @param {string} directory - directory path
 */
async function fetch_rmdir(directory) {
    const resp = await fetch("/api/directory/rm",
        {
            method: "DELETE",
            body: JSON.stringify({ directory }),
            headers: get_auth_headers(),
        });
    if (resp.status === 401) { navigate_to_login(); }
    if (!resp.ok) { throw new Error(resp.status) }
    return await resp.text();
}
/**
 * download a directory as a zip
 * @param {string} directory - the directory
 */
async function fetch_download_zip(directory) {
    directory = btoa(directory);
    var api_url = "/api/directory/download/" + directory;
    const resp = await fetch(api_url,
        {
            method: "GET",
            headers: get_auth_headers("text/plain"),
        });
    if (resp.status === 401) { navigate_to_login(); }
    if (!resp.ok) { throw new Error(resp.status) }
    return await resp.blob();
}
/**
 * download a directory as a zip
 * @param {string} directory - the directory to download
 */
function start_download_zip(directory) {
    fetch_download_zip(directory)
        .then(blob => {
            const url = URL.createObjectURL(blob);
            download(url, directory);
            URL.revokeObjectURL(url);
        });
}
/**
 * start downloading a file
 * @param {string} file_path - path of file to download
 */
function start_download_file(file_path) {
    fetch_download_token(file_path).then(token => {
        const url = "/api/file/download/by-token/" + token;
        download(url, file_path);
    });
}
/**
 * start uploading a file
 * @param {string} root_path - the path to use for upload destination
 * @param {string} file_elem - the file element to get file from
 */
async function start_upload_file(root_path, file_elem) {
    const form_data = new FormData();
    form_data.append("file", file_elem.files[0]);
    form_data.append("directory", root_path);
    await fetch_upload_file(form_data);
    file_elem.remove();
    alert("uploaded");
}

/**
 * show the dialog for uploading a
 * new file to current directory and then upload it
 */
function upload_file() {
    if (curr_dir) {
        const file_elem = document.createElement("input");
        file_elem.setAttribute("type", "file");
        file_elem.addEventListener("input", _ => {
            start_upload_file(curr_dir, file_elem);
        });
        file_elem.click();
    }
    else {
        alert("cannot upload here...");
    }
}

/**
 * create a new directory
 */
function create_dir() {
    if (curr_dir) {
        const name = prompt("directory name");
        if (name) {
            fetch_mkdir(curr_dir, name)
                .then(directory => {
                    alert("created directory, " + directory);
                    change_directory(curr_dir);
                })
                .catch(err => {
                    alert("failed to create directory")
                });
        }
        else {
            alert("invalid name given");
        }
    }
    else {
        alert("cannot create directory here...");
    }
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
    else {
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
    const files_and_dirs = document.getElementById("files-and-dirs");
    const loading_element = add_spin_loader(files_and_dirs);
    const roots = await fetch_root_dirs();

    delete_children(files_and_dirs);
    append_directory_root_row_element(files_and_dirs, roots.shared, roots.shared);
    append_directory_root_row_element(files_and_dirs, roots.home, roots.home);
    update_curr_dir_status("");
    curr_dir = null;
    document.getElementById("upload-file-bnt").setAttribute("disabled", true);
    document.getElementById("create-dir-bnt").setAttribute("disabled", true);
    remove_spin_loader(files_and_dirs, loading_element);
}

/**
 * change the page to show a new directory
 * @param {string} new_directory - the new directory to navigate to
 */
async function change_directory(new_directory) {
    const files_and_dirs = document.getElementById("files-and-dirs");
    const loading_element = add_spin_loader(files_and_dirs);
    const dir_content = await fetch_dir_content(new_directory);

    delete_children(files_and_dirs);

    append_directory_up_row_element(files_and_dirs, get_parent_dir(new_directory), "..");

    dir_content.forEach(path_content => {
        const path_name = path_content.name;
        const combined_path = new_directory + "/" + path_name;
        if (path_content.meta.is_directory) {
            append_directory_row_element(files_and_dirs, combined_path, path_name);
        }
        else {
            append_file_row_element(files_and_dirs, combined_path, path_name);
        }
    });
    curr_dir = new_directory;
    document.getElementById("upload-file-bnt").removeAttribute("disabled");
    document.getElementById("create-dir-bnt").removeAttribute("disabled");
    update_curr_dir_status(new_directory.replace("\\", "/"));
    remove_spin_loader(files_and_dirs, loading_element);
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
            else { throw err; }
        });
}

function handle_create_account_form() {
    const username = document.getElementById("username");
    const password = document.getElementById("password");
    const password_conf = document.getElementById("password-conf");
    if (password.value !== password_conf.value) {
        alert("passwords do not match");
        password_conf.value = "";
        password_conf.focus();
    }
    else {
        fetch_create_account(username.value, password.value)
            .then(_ => { navigate_to_login() })
            .catch(err => alert(err.message));
    }
}
