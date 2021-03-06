import * as api_errors from "./errors.js";

export const API_VERSION = "0.3.0";

export default class BasicCloudApi {
    static auth_token;
    static base_url = window.location.origin;
    /**
     * will handle all http status code errors.
     * unknown errors will use generic 'UnhandledError'
     * @param {Response} response - the response to handle
     */
    static handle_known_http_errors(response) {
        switch (response.status) {
            case 400:
                throw new api_errors.BadRequest(response.statusText);
            case 401:
                throw new api_errors.AuthError(response.status.statusText);
            case 422:
                // this may indicate the API is not compatible with current version
                throw new api_errors.UnprocessableError(response.statusText);
            case 500:
                // the server is broken :(
                throw new api_errors.InternalServerError(response.statusText);
            default:
                throw new api_errors.UnhandledError(response.status);
        }
    }
    /**
     * create http header, with the authorization token
     * @param {string} content_type - the content type to use
     * @returns the http headers
     */
    static get_auth_headers(content_type = "application/json") {
        const headers = {
            "Authorization": `Bearer ${BasicCloudApi.auth_token.access_token}`,
            "Content-Type": content_type,
        };
        if (content_type === null) { delete headers["Content-Type"]; }
        return headers;
    }
    /**
     * get the api version that is running on the server
     * @returns the api version
     */
    static async get_api_version() {
        const response = await fetch(BasicCloudApi.base_url + "/api/version",
            {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.json();
    }
    /**
     * create a new account
     * @param {string} username - the username to use
     * @param {string} password - the password to use
     * @returns the created user
     */
    static async post_create_account(username, password) {
        const response = await fetch(BasicCloudApi.base_url + "/api/users/",
            {
                method: "POST",
                body: JSON.stringify({ username, password }),
                headers: { "Content-Type": "application/json" },
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.json();
    }
    /**
     * get a login token using provided details
     * @param {string} username - the username to use
     * @param {string} password - the password to use
     * @param {boolean} save_token - whether the save token
     * @returns the access token
     */
    static async post_login_token(username, password, save_token = true) {
        const response = await fetch(BasicCloudApi.base_url + "/token",
            {
                method: "POST",
                body: `grant_type=password&username=${username}&password=${password}`,
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        const token = await response.json();
        if (save_token) { BasicCloudApi.auth_token = token; }
        return token;
    }
    /**
     * get the directory roots
     * @returns the "roots"
     */
    static async get_directory_roots() {
        const response = await fetch(BasicCloudApi.base_url + "/api/directory/roots",
            {
                method: "GET",
                headers: BasicCloudApi.get_auth_headers(),
            }
        );
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.json();
    }
    /**
     * get a directory's content
     * @param {string} directory - the current directory
     * @returns the directory content
     */
    static async post_directory_content(directory) {
        const response = await fetch(BasicCloudApi.base_url + "/api/directory/contents",
            {
                method: "POST",
                body: JSON.stringify({ directory: directory }),
                headers: BasicCloudApi.get_auth_headers(),
            }
        );
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.json();
    }
    /**
     * get the folder's history
     * @param {string} directory - the directory
     * @returns the complete directory history as a ContentChange
     */
    static async get_directory_history(directory) {
        directory = btoa(directory);
        const api_url = BasicCloudApi.base_url + "/api/directory/" + directory + "/history";
        const response = await fetch(api_url,
            {
                method: "GET",
                headers: BasicCloudApi.get_auth_headers(),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.json();
    }
    /**
     * create a directory
     * @param {string} directory - the current directory
     * @param {string} name - the new directory name
     * @returns the created directory path
     */
    static async post_create_directory(directory, name) {
        const response = await fetch(BasicCloudApi.base_url + "/api/directory/mkdir",
            {
                method: "POST",
                body: JSON.stringify({ directory, name }),
                headers: BasicCloudApi.get_auth_headers(),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.text();
    }
    /**
     * delete a directory
     * @param {string} directory - the directory to delete
     */
    static async delete_directory(directory) {
        const response = await fetch(BasicCloudApi.base_url + "/api/directory/rm",
            {
                method: "DELETE",
                body: JSON.stringify({ directory }),
                headers: BasicCloudApi.get_auth_headers(),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
    }
    /**
     * download a directory as a zip file
     * @param {string} directory - the directory to download
     * @returns the zip as a blob
     */
    static async get_directory_as_zip(directory) {
        directory = btoa(directory);
        var api_url = BasicCloudApi.base_url + "/api/directory/download/" + directory;
        const response = await fetch(api_url,
            {
                method: "GET",
                headers: BasicCloudApi.get_auth_headers("text/plain"),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.blob();
    }
    /**
     * delete a file
     * @param {string} file_path - the file path to delete
     */
    static async delete_file(file_path) {
        const response = await fetch(BasicCloudApi.base_url + "/api/file/rm",
            {
                method: "DELETE",
                body: JSON.stringify({ file_path }),
                headers: BasicCloudApi.get_auth_headers(),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
    }
    /**
     * download the file content
     * @param {string} file_path - file path to download
     * @returns the file as a blob
     */
    static async get_file(file_path) {
        file_path = btoa(file_path);
        var api_url = BasicCloudApi.base_url + "/api/file/download/" + file_path;
        const response = await fetch(api_url,
            {
                method: "GET",
                headers: BasicCloudApi.get_auth_headers("text/plain"),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.blob();
    }
    /**
     * upload a file
     * @param {Blob} file - file to upload
     * @param {string} directory - the directory to upload to
     */
    static async post_upload_file(file, directory) {
        const form_data = new FormData();
        form_data.append("file", file);
        form_data.append("directory", directory);

        const response = await fetch(BasicCloudApi.base_url + "/api/file/upload/overwrite",
            {
                method: "POST",
                body: form_data,
                headers: BasicCloudApi.get_auth_headers(null),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
    }
    /**
     * get the files history
     * @param {string} file_path - the file to get the history
     * @returns the complete file history as a ContentChange
     */
    static async get_file_history(file_path) {
        file_path = btoa(file_path);
        const api_url = BasicCloudApi.base_url + "/api/file/" + file_path + "/history";
        const response = await fetch(api_url,
            {
                method: "GET",
                headers: BasicCloudApi.get_auth_headers(),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.json();
    }
    /**
     * get a files shares
     * @param {string} file_path - the file path
     * @returns any created shares
     */
    static async get_file_shares(file_path) {
        file_path = btoa(file_path);
        const api_url = BasicCloudApi.base_url + "/api/file/" + file_path + "/shares";
        const response = await fetch(api_url,
            {
                method: "GET",
                headers: BasicCloudApi.get_auth_headers(),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.json();
    }
    /**
     * create a new file share
     * @param {string} path - the filepath
     * @param {string} expires - add a expiry date
     * @param {number} uses_left - add a usage limit
     * @returns the created file share
     */
    static async post_file_share(path, expires = null, uses_left = null) {
        const response = await fetch(BasicCloudApi.base_url + "/api/file/share",
            {
                method: "POST",
                body: JSON.stringify({ path, expires, uses_left }),
                headers: BasicCloudApi.get_auth_headers(),
            }
        );
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.json();
    }
    /**
     * get share meta
     * @param {string} share_uuid - the share's uuid
     * @returns the shares meta
     */
    static async get_file_share_meta(share_uuid) {
        const api_url = BasicCloudApi.base_url + "/api/file/share/" + share_uuid;
        const response = await fetch(api_url,
            {
                method: "GET",
                headers: BasicCloudApi.get_auth_headers(),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.json();
    }
    /**
     * delete a file share
     * @param {string} share_uuid - the share's uuid
     */
    static async delete_file_share(share_uuid) {
        const response = await fetch(BasicCloudApi.base_url + "/api/file/share/" + share_uuid,
            {
                method: "DELETE",
                headers: BasicCloudApi.get_auth_headers(),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
    }
    /**
     * download the file from the share
     * @param {string} share_uuid the share's uuid
     * @returns the file as a blob
     */
    static async get_file_share_file(share_uuid) {
        var api_url = BasicCloudApi.base_url + "/api/file/share/" + share_uuid + "/download";
        const response = await fetch(api_url,
            {
                method: "GET",
                headers: BasicCloudApi.get_auth_headers("text/plain"),
            });
        if (!response.ok) { BasicCloudApi.handle_known_http_errors(response); }
        return await response.blob();
    }
}
