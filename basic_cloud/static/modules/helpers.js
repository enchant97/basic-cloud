/**
 * gets the filename from a filepath
 * @param {String} file_path - the filepath to convert
 * @returns the filename
 */
export function path_to_filename(file_path) {
    // convert windows filepath to unix/linux style
    file_path = file_path.replace("\\", "/");

    var last_slash = file_path.lastIndexOf("/");
    if (last_slash === -1) {
        return file_path;
    }

    return file_path.substring(last_slash + 1);
}
/**
 * delete a parents children
 * @param {Element} elem - the parent element
 */
export function delete_children(parent) {
    while (parent.hasChildNodes()) {
        parent.removeChild(parent.lastChild);
    }
}
/**
 * trigger a download of file
 * @param {string} href - the href to download from
 * @param {string} filename - the filename of the download
 */
export function download(href, filename) {
    const a_elem = document.createElement("a");
    a_elem.href = href;
    a_elem.setAttribute("download", filename);
    a_elem.click();
    a_elem.remove();
}
/**
 * add a spinning loader to the parent
 * of the target element and hides the target
 * @param {Element} target_element - the element that is being loaded
 * @returns the loading element
 */
export function add_spin_loader(target_element) {
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
export function remove_spin_loader(target_element, loading_element) {
    target_element.style = null;
    loading_element.remove();
}
