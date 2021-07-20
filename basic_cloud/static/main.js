import * as api_errors from "./modules/errors.js";
import * as helpers from "./modules/helpers.js";
import Popup, { POPUP_MESSAGE_TYPE_CLASS, ButtonChoice } from "./modules/popup.js";
import BasicCloudApi from "./modules/api.js";

const TOKEN_KEY = "token";
const USERNAME_KEY = "username";

var curr_dir;

/**
 * show login screen
 */
function show_login_screen() {
    show_blank_screen();
    Popup.append_login(
        "Please Login",
        "Login is required for this service",
        process_login_details,
        show_create_account_screen
    );
}

/**
 * show the account creation screen
 */
function show_create_account_screen() {
    Popup.append_create_account(
        "Create Account",
        "A strong password is recommended.",
        process_create_account_details,
        show_login_screen
    );
}

/**
 * remove all elements from screen
 * (this will be shown once logged out)
 */
function show_blank_screen() {
    const navbar = document.querySelector("header nav");
    const main = document.querySelector("main");

    helpers.delete_children(navbar);
    helpers.delete_children(main);
}

/**
 * show the main screen
 * (this will be shown after login)
 */
function show_main_screen() {
    const navbar = document.querySelector("header nav");
    const main = document.querySelector("main");

    helpers.delete_children(navbar);
    helpers.delete_children(main);

    const load_shares_bnt = document.createElement("button");
    const upload_file_bnt = document.createElement("button");
    const create_dir_bnt = document.createElement("button");
    const logout_bnt = document.createElement("button");
    const curr_dir_label = document.createElement("h3");
    const files_and_dirs_container = document.createElement("div");

    load_shares_bnt.innerText = "Shares";
    load_shares_bnt.setAttribute("disabled", true);
    load_shares_bnt.id = "load-shares-bnt";
    load_shares_bnt.addEventListener("click", go_to_shares);
    upload_file_bnt.innerText = "Upload File";
    upload_file_bnt.setAttribute("disabled", true);
    upload_file_bnt.id = "upload-file-bnt";
    upload_file_bnt.addEventListener("click", upload_file);
    create_dir_bnt.innerText = "Create Directory";
    create_dir_bnt.setAttribute("disabled", true);
    create_dir_bnt.id = "create-dir-bnt";
    create_dir_bnt.addEventListener("click", create_dir);
    logout_bnt.innerText = "Logout";
    logout_bnt.addEventListener("click", do_logout);

    curr_dir_label.id = "curr-directory";
    files_and_dirs_container.id = "files-and-dirs";

    navbar.append(load_shares_bnt);
    navbar.append(upload_file_bnt);
    navbar.append(create_dir_bnt);
    navbar.append(logout_bnt);
    main.append(curr_dir_label);
    main.append(files_and_dirs_container);
}

/**
 * create file and directory row elements
 * and control their function
 */
class FileDirRow {
    constructor(path, name) {
        this.name = name;
        this.path = path;
        this.button_choices = [];

        this.create_elements();
        this.set_names();
    }
    create_elements() {
        this.icon_elem = document.createElement("img");
        this.name_elem = document.createElement("button");
        this.delete_bnt_elem = document.createElement("button");
        this.download_bnt_elem = document.createElement("button");
        this.more_options_elem = document.createElement("button");
    }
    set_names() {
        this.name_elem.innerText = this.name;
        this.delete_bnt_elem.innerText = "×";
        this.download_bnt_elem.innerText = "Download";
        this.more_options_elem.innerText = "≡";
        this.more_options_elem.addEventListener("click", _ => {
            Popup.append_selection("More Options", this.path, this.button_choices);
        });
    }
    add_dir_root_navigate() {
        this.name_elem.addEventListener("click", _ => {
            document.getElementById("load-shares-bnt").setAttribute("disabled", true);
            load_roots()
                .catch (err => {
                    if (err instanceof api_errors.AuthError) { show_login_screen(); }
                    else { throw err; }
                });
        });
    }
    add_dir_dir_navigate() {
        this.name_elem.addEventListener("click", _ => {
            document.getElementById("load-shares-bnt").removeAttribute("disabled");
            change_directory(this.path)
                .catch(err => {
                    if (err instanceof api_errors.AuthError) { show_login_screen(); }
                    else{ throw err; }
                });
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
        if (edit_allowed) {
            this.button_choices.push(new ButtonChoice("Delete", BasicCloudApi.delete_file, [this.path]));
        }
        this.download_bnt_elem.addEventListener("click", _ => { start_download_file(this.path) });
    }
    make_dir_row_rm() {
        this.button_choices.push(new ButtonChoice("Delete", BasicCloudApi.delete_directory, [this.path]));
    }
    make_up_dir_row() {
        this.download_bnt_elem.setAttribute("disabled", true);
        this.more_options_elem.setAttribute("disabled", true);
        // if path is null then it must be "root"
        if (this.path === null) {
            this.add_dir_root_navigate();
        }
        else {
            this.add_dir_navigate();
        }
    }
    make_dir_row(edit_allowed = true) {
        if (edit_allowed) {
            this.button_choices.push(new ButtonChoice("Delete", BasicCloudApi.delete_directory, [this.path]));
        }
        this.add_dir_zip_download();
        this.add_dir_navigate();
    }
    make_dir_root_row() {
        this.add_dir_zip_download();
        this.add_dir_dir_navigate();
        this.more_options_elem.setAttribute("disabled", true);
    }
    append_elements(parent) {
        parent.append(this.icon_elem);
        parent.append(this.name_elem);
        parent.append(this.more_options_elem);
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
 * checks whether the path is at the "root"
 * @param {string} the_dir - the current directory
 * @returns bool for whether at root
 */
function directory_at_root(the_dir) {
    if (the_dir == "homes/" + get_stored_username() || the_dir == "shared") {
        return true;
    }
    return false;
}

function get_stored_username() {
    let username = localStorage.getItem(USERNAME_KEY);
    if (username === null) {
        return sessionStorage.getItem(USERNAME_KEY);
    }
    return username
}

function remove_username() {
    sessionStorage.removeItem(USERNAME_KEY);
    localStorage.removeItem(USERNAME_KEY);
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
 * updates the current directory element
 */
function update_curr_dir_status(new_location) {
    document.getElementById("curr-directory").innerText = "Location: /" + new_location;
}

/**
 * download a directory as a zip
 * @param {string} directory - the directory to download
 */
function start_download_zip(directory) {
    BasicCloudApi.get_directory_as_zip(directory)
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const filename = helpers.path_to_filename(directory)
            helpers.download(url, filename);
            URL.revokeObjectURL(url);
        })
        .catch (err => {
        if (err instanceof api_errors.AuthError) {
            show_login_screen();
        }
        else { throw err; }
        });
}
/**
 * start downloading a file
 * @param {string} file_path - path of file to download
 */
function start_download_file(file_path) {
    const filename = helpers.path_to_filename(file_path);
    BasicCloudApi.get_file(file_path)
        .then(blob => {
            const url = URL.createObjectURL(blob);
            helpers.download(url, filename);
            URL.revokeObjectURL(url);
        })
        .catch(err => {
            if (err instanceof api_errors.AuthError) {
                show_login_screen();
            }
            else { throw err; }
        });
}
function handle_file_upload(file_elem) {
    const loading_popup = Popup.append_loading(
        "Uploading File",
        "uploading please wait"
    );

    BasicCloudApi.post_upload_file(file_elem.files[0], curr_dir)
        .then(_ => {
            loading_popup.remove();
            Popup.append_message("Upload Success", "file has been uploaded");
            file_elem.remove();
        })
        .catch(_err => {
            loading_popup.remove();
            Popup.append_message(
                "Upload Error",
                "the upload has failed",
                POPUP_MESSAGE_TYPE_CLASS.ERROR
            );
            // cleanup
            file_elem.remove();
        });
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
            handle_file_upload(file_elem);
        });
        file_elem.click();
    }
    else {
        Popup.append_message(
            "Upload Error",
            "cannot upload here",
            POPUP_MESSAGE_TYPE_CLASS.ERROR
        );
    }
}

/**
 * create a new directory
 */
function create_dir() {
    if (curr_dir) {
        const name = prompt("directory name");
        if (name) {
            BasicCloudApi.post_create_directory(curr_dir, name)
                .then(directory => {
                    Popup.append_message(
                        "Directory Creation Success",
                        "created directory at: " + directory
                    );
                    change_directory(curr_dir);
                })
                .catch(err => {
                    if (err instanceof api_errors.AuthError) {
                        show_login_screen();
                    }
                    else {
                        Popup.append_message(
                        "Directory Creation Error",
                        "unhandled error",
                        POPUP_MESSAGE_TYPE_CLASS.ERROR
                        );
                     }
                });
        }
        else {
            Popup.append_message(
                "Directory Creation Error",
                "invalid name given",
                POPUP_MESSAGE_TYPE_CLASS.ERROR
            );
        }
    }
    else {
        Popup.append_message(
            "Directory Creation Error",
            "cannot create directory here",
            POPUP_MESSAGE_TYPE_CLASS.ERROR
        );
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
    const token = (await BasicCloudApi.post_login_token(username, password)).access_token;
    // remove tokens from browser storage
    remove_token();
    remove_username();
    // store the tokens
    if (rememberme) {
        localStorage.setItem(USERNAME_KEY, username);
        localStorage.setItem(TOKEN_KEY, token);
    }
    else {
        sessionStorage.setItem(USERNAME_KEY, username);
        sessionStorage.setItem(TOKEN_KEY, token);
    }
}

/**
 * log the user out and redirect to login page
 */
function do_logout() {
    remove_token();
    remove_username();
    show_login_screen();
}

/**
 * load and display the root directories
 */
async function load_roots() {
    const files_and_dirs = document.getElementById("files-and-dirs");
    const loading_element = helpers.add_spin_loader(files_and_dirs);
    try {
        const roots = await BasicCloudApi.get_directory_roots();

        helpers.delete_children(files_and_dirs);
        append_directory_root_row_element(files_and_dirs, roots.shared, roots.shared);
        append_directory_root_row_element(files_and_dirs, roots.home, roots.home);
        update_curr_dir_status("");
        curr_dir = null;
        document.getElementById("upload-file-bnt").setAttribute("disabled", true);
        document.getElementById("create-dir-bnt").setAttribute("disabled", true);
    }
    finally {
        helpers.remove_spin_loader(files_and_dirs, loading_element);
    }
}

/**
 * change the page to show a new directory
 * @param {string} new_directory - the new directory to navigate to
 */
async function change_directory(new_directory) {
    const files_and_dirs = document.getElementById("files-and-dirs");
    const loading_element = helpers.add_spin_loader(files_and_dirs);
    try {
        const dir_content = await BasicCloudApi.post_directory_content(new_directory);

        helpers.delete_children(files_and_dirs);

        if (curr_dir === null || directory_at_root(new_directory)) {
            append_directory_up_row_element(files_and_dirs, null, "..");
        }
        else {
            append_directory_up_row_element(files_and_dirs, get_parent_dir(new_directory), "..");
        }

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
    }
    finally {
        helpers.remove_spin_loader(files_and_dirs, loading_element);
    }
}

/**
 * handle the login form being submitted
 */
function process_login_details(username, password, rememberme) {
    do_login(username, password, rememberme)
        .then(_ => {
            show_main_screen();
            load_roots().catch(err => {
                if (err instanceof api_errors.AuthError) {
                    show_login_screen();
                }
                else { throw err; }
            });
        })
        .catch(err => {
            if (err instanceof api_errors.AuthError) {
                Popup.append_message(
                    "Login Failed",
                    "username or password incorrect!",
                    POPUP_MESSAGE_TYPE_CLASS.ERROR,
                    show_login_screen
                );
            }
            else { throw err; }
        });
}

function process_create_account_details(username, password, password_conf) {
    if (password !== password_conf) {
        Popup.append_message(
            "User Creation Error",
            "passwords do not match",
            POPUP_MESSAGE_TYPE_CLASS.ERROR
        );
    }
    else {
        BasicCloudApi.post_create_account(username, password)
            .then(_ => { show_login_screen() })
            .catch(err => {
                if (err instanceof api_errors.BadRequest) {
                    Popup.append_message(
                        "User Creation Failed",
                        "fields given not acceptable",
                        POPUP_MESSAGE_TYPE_CLASS.ERROR,
                        show_create_account_screen);
                }
                else if (err instanceof api_errors.AuthError) {
                    Popup.append_message(
                        "User Creation Failed",
                        "account creation is currently disabled",
                        POPUP_MESSAGE_TYPE_CLASS.ERROR,
                        show_login_screen);
                }
                else {
                    Popup.append_message(
                        "User Creation Failed",
                        "error: " + err.message,
                        POPUP_MESSAGE_TYPE_CLASS.ERROR,
                        show_create_account_screen
                    );
                }
            });
    }
}

window.addEventListener("load", _ => {
    // register required click events
    document.getElementById("login-bnt").addEventListener("click", show_login_screen);

    if (get_stored_token() != null) {
        BasicCloudApi.auth_token = {
            token_type: "bearer",
            access_token: get_stored_token()
        };
        show_main_screen();
        load_roots().catch(err => {
            if (err instanceof api_errors.AuthError) {
                show_login_screen();
            }
            else { throw err; }
        });
    }
});
